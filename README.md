# Jupyterhub K8s Calendar Node Placeholder

This repository contains a Helm chart for deploying a JupyterHub Node Placeholder service on a Kubernetes cluster. The Node Placeholder service is designed to manage and allocate placeholder nodes for JupyterHub users, ensuring efficient resource utilization and improved user experience during surge login events.

The Node Placeholder service works by monitoring the academic calendar events from a provided iCal URL. Based on the events, it dynamically adjusts the number of placeholder nodes available in the Kubernetes cluster, allowing JupyterHub to pre-allocate resources for anticipated user logins. If there are existing user nodes deployed, and these have the capacity to handle additional users, the Node Placeholder service will scale down the number of placeholder nodes accordingly.

The events are fetched from the iCal URL and parsed to determine peak usage times, such as the start of exam periods or other significant academic events where you expect a large number of users to log in. The service then scales the number of placeholder nodes accordingly, ensuring that users have a seamless experience when logging into JupyterHub during these high-demand periods.

When creating these events, they only need to be scheduled for the exact time periods where you expect a surge in logins. For instance, if you expect a surge of logins before a 9am exam, the event should be scheduled to start at 8:50am and end at 9:10am. This allows the Node Placeholder service to allocate resources just in time for the expected demand.

An example calendar entry for an event might look like this:

``` yaml
pool1: 2
pool2: 1
```

This indicates that during the event, 2 placeholder nodes should be allocated from `pool1` and 1 placeholder node from `pool2`.

## Installation

JupyterHub K8S Node Placeholder is installed as a Helm chart.

### Requirements

- Jupyterhub running on Kubernetes
- A publicly accessible iCal URL containing the academic calendar events (eg: Google Calendar, Outlook Calendar)
- Helm 3.x installed on your local machine or CI/CD pipeline

### Example Helm Configuration

An example configuration in `values.yaml` might look like this:

``` yaml
# The URL of the public calendar to use for the node placeholder
calendarUrl: https://url.to/your/public/calendar.ics

calendarTimezone: "America/Los_Angeles"

nodePools:
  # The short name of the node pool, used in the calendar event description
  # In this example, we have a node pool named "user-pool" that contains our
  # Jupyterhub singleuser nodes:
  user:
    nodeSelector:
    hub.jupyter.org/pool-name: base-pool
    resources:
    requests:
        # Some value slightly lower than allocatable RAM on the nodepool in bytes
        # This is an example using a GCP n2-highmem-8 node with 64G of RAM allocatable
        memory: 60929654784
    replicas: 1
```

### Installation with Helm



## Features

## Working with this repository

You will need Python 3.8+ and `pip` installed on your system. You can manage Python
environments using tools like `venv` or `conda`.

For basic development, you will need to install the dependencies listed in
`dev-requirements.txt`. You can do this by running:

``` bash
pip install -r dev-requirements.txt
```

For more advanced development, including testing any changes you make, you will
need to install the dependencies listed in
[`requirements.txt`](node-placeholder-scaler/requirements.txt).

``` bash
pip install -r node-placeholder-scaler/requirements.txt
```

### Pre-Commit hooks: Installing

The previous step, `pip install -r dev-requirements.txt`, installs the package
[`pre-commit`](https://pre-commit.com/). This is used to run a series of
commands defined in the file [`.pre-commit-config.yaml`](.pre-commit-config.yaml)
to help ensure no mistakes are committed to the repo.

After you've installed `dev-requirements.txt`, execute the following two
commands:

``` bash
pre-commit install
pre-commit run --all-files
```

### Development

When working with this repo, you should create a fork and work on a feature
branch. When you're ready to submit your changes, create a pull request against
your fork, and open a PR against the `main` branch of this repo.

#### Changing the Python imports

If you need to change or update the scaler's Python imports, you will need to
recompile the scaler's `requirements.txt` file. You can do this by running:

``` bash
cd node-placeholder-scaler
pip-compile --output-file=requirements.txt requirements.in
```

Create a PR with your changes, and these will be added to the latest image created.

#### Testing your changes

Right now, there are no automated tests for this repo. You can test your changes
to the Python code by running [test.py](node-placeholder-scaler/test.py):

``` bash
python node-placeholder-scaler/test.py
```

This will test the scaler's ability to read and parse calendar events from a known
iCal URL.
