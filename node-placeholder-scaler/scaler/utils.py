def parse_cpu(q):
    """Parse CPU quantity string and return value in millicores."""
    if q.endswith("m"):
        return int(q[:-1])
    else:
        return int(q) * 1000  # Convert cores to millicores


def parse_memory(q):
    """Parse memory quantity string and return value in MiB."""
    if q.endswith("Ki"):
        return int(int(q[:-2]) / 1024)
    elif q.endswith("Mi"):
        return int(q[:-2])
    elif q.endswith("Gi"):
        return int(q[:-2]) * 1024
    elif q.endswith("M"):  # megabytes
        return int(q) * 1e6 // (1024 * 1024)
    else:  # Assume it is in Bytes
        return int(q) // (1024 * 1024)  # Convert Bytes to MiB