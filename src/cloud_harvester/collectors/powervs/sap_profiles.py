"""Collect PowerVS SAP profiles."""
from cloud_harvester.collectors.powervs.client import PowerVSClient
from cloud_harvester.collectors.powervs.workspaces import discover_workspaces


def collect_sap_profiles(api_key: str, token: str, regions: list[str]) -> list[dict]:
    """Collect SAP profiles across all PowerVS workspaces."""
    workspaces = discover_workspaces(token, regions)
    results = []

    for ws in workspaces:
        client = PowerVSClient(token, ws["region"], ws["guid"])
        try:
            data = client.get("sap")
        except Exception:
            continue

        items = data.get("profiles", [])
        for item in items:
            results.append({
                "profileID": item.get("profileID", ""),
                "type": item.get("type", ""),
                "cores": item.get("cores", 0),
                "memory": item.get("memory", 0),
                "saps": item.get("saps", 0),
                "certified": item.get("certified", False),
                "workspace": ws["name"],
                "zone": ws["zone"],
            })

    return results
