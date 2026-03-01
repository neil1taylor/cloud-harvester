"""Collect VPCs."""
from cloud_harvester.collectors.vpc.client import VpcClient, VPC_REGIONS


def collect_vpcs(api_key: str, token: str, regions: list[str]) -> list[dict]:
    """Collect VPCs across all regions."""
    client = VpcClient(token)
    target_regions = [r for r in VPC_REGIONS if not regions or any(reg in r for reg in regions)]

    results = []
    for region in target_regions:
        try:
            items = client.list_resources(region, "vpcs", "vpcs")
        except Exception:
            continue

        for item in items:
            results.append({
                "id": item.get("id", ""),
                "name": item.get("name", ""),
                "status": item.get("status", ""),
                "classicAccess": item.get("classic_access", False),
                "region": region,
                "created_at": item.get("created_at", ""),
                "resourceGroup": item.get("resource_group", {}).get("name", ""),
            })
    return results
