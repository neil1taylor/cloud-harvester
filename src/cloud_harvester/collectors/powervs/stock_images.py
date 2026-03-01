"""Collect PowerVS stock images."""
from cloud_harvester.collectors.powervs.client import PowerVSClient
from cloud_harvester.collectors.powervs.workspaces import discover_workspaces


def collect_stock_images(api_key: str, token: str, regions: list[str]) -> list[dict]:
    """Collect stock images across all PowerVS workspaces."""
    workspaces = discover_workspaces(token, regions)
    results = []

    for ws in workspaces:
        client = PowerVSClient(token, ws["region"], ws["guid"])
        try:
            data = client.get("stock-images")
        except Exception:
            continue

        items = data.get("images", [])
        for item in items:
            specifications = item.get("specifications", {})
            results.append({
                "imageID": item.get("imageID", ""),
                "name": item.get("name", ""),
                "state": item.get("state", ""),
                "operatingSystem": specifications.get("operatingSystem", ""),
                "architecture": specifications.get("architecture", ""),
                "storageType": item.get("storageType", ""),
                "workspace": ws["name"],
                "zone": ws["zone"],
            })

    return results
