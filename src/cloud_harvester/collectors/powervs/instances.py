"""Collect PowerVS PVM instances."""
from cloud_harvester.collectors.powervs.client import PowerVSClient
from cloud_harvester.collectors.powervs.workspaces import discover_workspaces


def collect_instances(api_key: str, token: str, regions: list[str]) -> list[dict]:
    """Collect PVM instances across all PowerVS workspaces."""
    workspaces = discover_workspaces(token, regions)
    results = []

    for ws in workspaces:
        client = PowerVSClient(token, ws["region"], ws["guid"])
        try:
            data = client.get("pvm-instances")
        except Exception:
            continue

        items = data.get("pvmInstances", [])
        for item in items:
            networks = item.get("networks", [])
            primary_ip = networks[0].get("ipAddress", "") if networks else ""

            results.append({
                "pvmInstanceID": item.get("pvmInstanceID", ""),
                "serverName": item.get("serverName", ""),
                "status": item.get("status", ""),
                "sysType": item.get("sysType", ""),
                "processors": item.get("processors", 0),
                "procType": item.get("procType", ""),
                "memory": item.get("memory", 0),
                "osType": item.get("osType", ""),
                "primaryIp": primary_ip,
                "storageType": item.get("storageType", ""),
                "workspace": ws["name"],
                "zone": ws["zone"],
                "creationDate": item.get("creationDate", ""),
            })

    return results
