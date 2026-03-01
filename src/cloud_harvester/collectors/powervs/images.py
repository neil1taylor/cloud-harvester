"""Collect PowerVS workspace images."""
from cloud_harvester.collectors.powervs.client import PowerVSClient
from cloud_harvester.collectors.powervs.workspaces import discover_workspaces


def collect_images(api_key: str, token: str, regions: list[str]) -> list[dict]:
    """Collect workspace images across all PowerVS workspaces."""
    workspaces = discover_workspaces(token, regions)
    results = []

    for ws in workspaces:
        client = PowerVSClient(token, ws["region"], ws["guid"])
        try:
            data = client.get("images")
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
                "size": item.get("size", 0),
                "storageType": item.get("storageType", ""),
                "workspace": ws["name"],
                "zone": ws["zone"],
                "creationDate": item.get("creationDate", ""),
            })

    return results
