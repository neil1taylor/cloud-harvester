"""Collect PowerVS SSH keys."""
from cloud_harvester.collectors.powervs.client import PowerVSClient
from cloud_harvester.collectors.powervs.workspaces import discover_workspaces


def collect_ssh_keys(api_key: str, token: str, regions: list[str]) -> list[dict]:
    """Collect SSH keys across all PowerVS workspaces."""
    workspaces = discover_workspaces(token, regions)
    results = []

    for ws in workspaces:
        client = PowerVSClient(token, ws["region"], ws["guid"])
        try:
            data = client.get_v1("ssh-keys")
        except Exception:
            continue

        items = data.get("sshKeys", [])
        for item in items:
            # Truncate key for display
            ssh_key = item.get("sshKey", "")
            if len(ssh_key) > 80:
                ssh_key = ssh_key[:40] + "..." + ssh_key[-20:]

            results.append({
                "name": item.get("name", ""),
                "sshKey": ssh_key,
                "creationDate": item.get("creationDate", ""),
                "workspace": ws["name"],
                "zone": ws["zone"],
            })

    return results
