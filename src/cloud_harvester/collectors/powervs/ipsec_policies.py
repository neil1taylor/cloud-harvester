"""Collect PowerVS IPSec policies."""
from cloud_harvester.collectors.powervs.client import PowerVSClient
from cloud_harvester.collectors.powervs.workspaces import discover_workspaces


def collect_ipsec_policies(api_key: str, token: str, regions: list[str]) -> list[dict]:
    """Collect IPSec policies across all PowerVS workspaces."""
    workspaces = discover_workspaces(token, regions)
    results = []

    for ws in workspaces:
        client = PowerVSClient(token, ws["region"], ws["guid"])
        try:
            data = client.get("vpn/ipsec-policies")
        except Exception:
            continue

        items = data.get("ipsecPolicies", [])
        for item in items:
            results.append({
                "id": item.get("id", ""),
                "name": item.get("name", ""),
                "encryption": item.get("encryption", ""),
                "dhGroup": item.get("dhGroup", 0),
                "authentication": item.get("authentication", ""),
                "pfs": item.get("pfs", False),
                "workspace": ws["name"],
                "zone": ws["zone"],
            })

    return results
