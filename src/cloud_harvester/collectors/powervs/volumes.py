"""Collect PowerVS volumes."""
from cloud_harvester.collectors.powervs.client import PowerVSClient
from cloud_harvester.collectors.powervs.workspaces import discover_workspaces


def collect_volumes(api_key: str, token: str, regions: list[str]) -> list[dict]:
    """Collect volumes across all PowerVS workspaces."""
    workspaces = discover_workspaces(token, regions)
    results = []

    for ws in workspaces:
        client = PowerVSClient(token, ws["region"], ws["guid"])
        try:
            data = client.get("volumes")
        except Exception:
            continue

        items = data.get("volumes", [])
        for item in items:
            pvm_instance = item.get("pvmInstanceIDs", [])
            instance_name = ""
            if pvm_instance:
                instance_name = str(pvm_instance[0]) if pvm_instance else ""

            results.append({
                "volumeID": item.get("volumeID", ""),
                "name": item.get("name", ""),
                "state": item.get("state", ""),
                "size": item.get("size", 0),
                "diskType": item.get("diskType", ""),
                "bootable": item.get("bootable", False),
                "shareable": item.get("shareable", False),
                "pvmInstanceName": instance_name,
                "workspace": ws["name"],
                "zone": ws["zone"],
                "creationDate": item.get("creationDate", ""),
            })

    return results
