"""Discover PowerVS workspaces via IBM Cloud Resource Controller."""
import requests

from cloud_harvester.collectors.powervs.client import ZONE_TO_REGION

RESOURCE_CONTROLLER_URL = "https://resource-controller.cloud.ibm.com/v2/resource_instances"
POWER_IAAS_RESOURCE_ID = "abd259f0-9990-11e8-acb-aaef098ae67a"


def discover_workspaces(token: str, regions: list[str]) -> list[dict]:
    """Discover all PowerVS workspaces using the Resource Controller API."""
    headers = {"Authorization": f"Bearer {token}"}
    params = {
        "resource_id": POWER_IAAS_RESOURCE_ID,
        "type": "service_instance",
        "limit": 100,
    }

    workspaces = []
    url = RESOURCE_CONTROLLER_URL
    while url:
        resp = requests.get(url, headers=headers, params=params, timeout=60)
        if resp.status_code == 403:
            return []
        resp.raise_for_status()
        data = resp.json()

        for resource in data.get("resources", []):
            zone = resource.get("region_id", "")
            region = ZONE_TO_REGION.get(zone, zone)

            # Filter by requested regions if specified
            if regions and not any(r in region for r in regions):
                continue

            workspaces.append({
                "guid": resource.get("guid", ""),
                "name": resource.get("name", ""),
                "zone": zone,
                "region": region,
                "resourceGroupName": resource.get("resource_group_id", ""),
                "state": resource.get("state", ""),
                "createdAt": resource.get("created_at", ""),
            })

        next_url = data.get("next_url")
        if next_url:
            url = f"https://resource-controller.cloud.ibm.com{next_url}"
            params = {}  # next_url includes query params
        else:
            url = None

    return workspaces


def collect_workspaces(api_key: str, token: str, regions: list[str]) -> list[dict]:
    """Collect PowerVS workspace information."""
    return discover_workspaces(token, regions)
