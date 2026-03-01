"""Collect VPC Block Storage Volumes."""
from cloud_harvester.collectors.vpc.client import VpcClient, VPC_REGIONS


def collect_vpc_volumes(api_key: str, token: str, regions: list[str]) -> list[dict]:
    """Collect VPC block storage volumes across all regions."""
    client = VpcClient(token)
    target_regions = [r for r in VPC_REGIONS if not regions or any(reg in r for reg in regions)]

    results = []
    for region in target_regions:
        try:
            items = client.list_resources(region, "volumes", "volumes")
        except Exception:
            continue

        for item in items:
            results.append({
                "id": item.get("id", ""),
                "name": item.get("name", ""),
                "status": item.get("status", ""),
                "capacity": item.get("capacity", 0),
                "iops": item.get("iops", 0),
                "profile": item.get("profile", {}).get("name", ""),
                "encryption": item.get("encryption", ""),
                "zone": item.get("zone", {}).get("name", ""),
                "region": region,
                "created_at": item.get("created_at", ""),
            })
    return results
