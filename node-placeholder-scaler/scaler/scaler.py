#!/usr/bin/env python3
import argparse
import logging
import subprocess
import tempfile
import time
import json
from copy import deepcopy

from ruamel.yaml import YAML

from .calendar import _event_repr, get_calendar, get_events

yaml = YAML(typ="safe")


def parse_quantity(q):
    if q.endswith('m'):  # millicores
        return int(q[:-1])
    elif q.endswith('Ki'):
        return int(int(q[:-2]) / 1024)
    elif q.endswith('Mi'):
        return int(q[:-2])
    elif q.endswith('Gi'):
        return int(q[:-2]) * 1024
    else:
        return int(q)


def get_node_allocatable():
    """Returns dict: {node_name: {'cpu': int (millicores), 'memory': int (Mi)}}"""
    cmd = ["kubectl", "get", "nodes", "-o", "json"]
    output = subprocess.check_output(cmd).decode()
    nodes = json.loads(output)["items"]

    alloc_data = {}
    for node in nodes:
        name = node["metadata"]["name"]
        labels = node["metadata"].get("labels", {})
        alloc = node["status"]["allocatable"]
        alloc_cpu = parse_quantity(alloc["cpu"])
        alloc_mem = parse_quantity(alloc["memory"])
        pool = labels.get("hub.jupyter.org/pool-name", "unknown")
        alloc_data[name] = {
            "cpu_m": alloc_cpu,
            "mem_mi": alloc_mem,
            "node_pool": pool
        }
    return alloc_data


def get_node_usage():
    """Returns dict: {node_name: {'cpu': int (millicores), 'memory': int (Mi)}}"""
    cmd = ["kubectl", "top", "nodes", "--no-headers"]
    output = subprocess.check_output(cmd).decode()

    usage_data = {}
    for line in output.strip().splitlines():
        parts = line.split()
        name = parts[0]
        cpu_m = int(parts[1].replace("m", ""))
        mem_raw = parts[3]
        mem_mi = parse_quantity(mem_raw)
        usage_data[name] = {"cpu_m": cpu_m, "mem_mi": mem_mi}
    return usage_data


def get_usable_resources(node_pool_name):
    alloc = get_node_allocatable()
    usage = get_node_usage()

    result = []
    for node, info in alloc.items():
        if info["node_pool"] != node_pool_name:
            continue
        used = usage.get(node, {"cpu_m": 0, "mem_mi": 0})
        free_cpu = info["cpu_m"] - used["cpu_m"]
        free_mem = info["mem_mi"] - used["mem_mi"]
        result.append({
            "node": node,
            "cpu_alloc_m": info["cpu_m"],
            "cpu_used_m": used["cpu_m"],
            "cpu_free_m": free_cpu,
            "cpu_free_ratio": float(free_cpu / info["cpu_m"]),
            "mem_alloc_mi": info["mem_mi"],
            "mem_used_mi": used["mem_mi"],
            "mem_free_mi": free_mem,
            "node_pool": info["node_pool"],
            "mem_free_ratio": float(free_mem / info["mem_mi"]),
        })
    return result


def make_deployment(pool_name, template, node_selector, resources, replicas):
    deployment_name = f"{pool_name}-placeholder"
    deployment = deepcopy(template)
    deployment["metadata"]["name"] = deployment_name
    deployment["spec"]["replicas"] = replicas
    deployment["spec"]["template"]["spec"]["nodeSelector"] = node_selector
    deployment["spec"]["template"]["spec"]["containers"][0]["resources"] = resources

    return deployment


log = logging.getLogger(__name__)


def get_replica_counts(events):
    replica_counts = {}
    for ev in events:
        logging.info(f"Found event {_event_repr(ev)}")
        if ev.description:
            # initialize
            pools_replica_config = None
            try:
                pools_replica_config = yaml.load(ev.description)
            except Exception as e:
                logging.error(
                    f"Caught unhandled exception parsing event description:\n{e}"
                )
                logging.error(f"Error in parsing description of {_event_repr(ev)}")
                logging.error(f"{ev.description=}")
                pass
            if pools_replica_config is None:
                logging.error(f"No description in event {_event_repr(ev)}")
                continue
            elif isinstance(pools_replica_config, str):
                logging.error("Event description not parsed as dictionary.")
                logging.error(f"{ev.description=}")
                continue
            for pool_name, count in pools_replica_config.items():
                if not isinstance(count, int):
                    logging.info(f"Count {count} not an integer.")
                    continue
                if pool_name not in replica_counts:
                    replica_counts[pool_name] = count
                else:
                    replica_counts[pool_name] = max(replica_counts[pool_name], count)
        else:
            logging.error(f"Event has no description: {_event_repr(ev)}")
    return replica_counts


def main():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")

    argparser = argparse.ArgumentParser()
    argparser.add_argument("--config-file", default="config.yaml")
    argparser.add_argument(
        "--placeholder-template-file", default="placeholder-template.yaml"
    )

    args = argparser.parse_args()

    while True:
        # Reload all config files on each iteration, so we can change config
        # without needing to bounce the pod
        with open(args.config_file) as f:
            config = yaml.load(f)

        with open(args.placeholder_template_file) as f:
            placeholder_template = yaml.load(f)

        calendar = get_calendar(config["calendarUrl"])
        events = get_events(calendar)
        logging.info(f"Found {len(events)} events at {config['calendarUrl']}.")

        replica_count_overrides = get_replica_counts(events)
        logging.info(f"Overrides: {replica_count_overrides}")

        # Generate deployment config based on our config
        for pool_name, pool_config in config["nodePools"].items():            
            pool_usage_result = get_usable_resources(pool_name)
            node_placerholder_required = True
            for node_usage in pool_usage_result:
                if node_usage['mem_free_ratio'] >= 0.2 and node_usage['cpu_free_ratio'] >= 0.2:
                    logging.info(f"Node {node_usage['node']} has sufficient resources. Free CPU Ratio is {node_usage['cpu_free_ratio']:.2f}, Free Memory Ratio is {node_usage['mem_free_ratio']:.2f}.")
                    node_placerholder_required = False
                    break
            if not node_placerholder_required:
                logging.info(f"Node placeholder is not required for pool {pool_name}, resources on other nodes are sufficient.")
                replica_count = replica_count_overrides.get(
                    pool_name, 0
                )
            else:
                replica_count = replica_count_overrides.get(
                    pool_name, pool_config["replicas"]
                )

            deployment = make_deployment(
                pool_name,
                placeholder_template,
                pool_config["nodeSelector"],
                pool_config["resources"],
                replica_count,
            )
            logging.info(f"Setting {pool_name} to have {replica_count} replicas")
            with tempfile.NamedTemporaryFile(mode="r+") as f:
                yaml.dump(deployment, f)
                f.flush()
                proc = subprocess.run(
                    ["kubectl", "apply", "-f", f.name],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                )

                logging.info(proc.stdout.strip())
        time.sleep(60)
