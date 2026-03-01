"""Collect VPC Bare Metal Servers."""
from cloud_harvester.collectors.vpc.client import VpcClient, VPC_REGIONS


def collect_vpc_bare_metal(api_key: str, token: str, regions: list[str]) -> list[dict]:
    """Collect VPC bare metal servers across all regions."""
    client = VpcClient(token)
    target_regions = [r for r in VPC_REGIONS if not regions or any(reg in r for reg in regions)]

    results = []
    for region in target_regions:
        try:
            items = client.list_resources(region, "bare_metal_servers", "bare_metal_servers")
        except Exception:
            continue

        for item in items:
            results.append({
                "id": item.get("id", ""),
                "name": item.get("name", ""),
                "status": item.get("status", ""),
                "profile": item.get("profile", {}).get("name", ""),
                "zone": item.get("zone", {}).get("name", ""),
                "vpcName": item.get("vpc", {}).get("name", ""),
                "region": region,
                "created_at": item.get("created_at", ""),
                "resourceGroup": item.get("resource_group", {}).get("name", ""),
            })
    return results
