"""Collect VPC Private Images."""
from cloud_harvester.collectors.vpc.client import VpcClient, VPC_REGIONS


def collect_vpc_images(api_key: str, token: str, regions: list[str]) -> list[dict]:
    """Collect VPC private images across all regions."""
    client = VpcClient(token)
    target_regions = [r for r in VPC_REGIONS if not regions or any(reg in r for reg in regions)]

    results = []
    for region in target_regions:
        try:
            items = client.list_resources(
                region, "images?visibility=private", "images"
            )
        except Exception:
            continue

        for item in items:
            os_info = item.get("operating_system", {})
            os_name = os_info.get("display_name", "") or os_info.get("name", "")
            arch = os_info.get("architecture", "") or item.get("architecture", "")
            results.append({
                "id": item.get("id", ""),
                "name": item.get("name", ""),
                "status": item.get("status", ""),
                "os": os_name,
                "architecture": arch,
                "region": region,
                "created_at": item.get("created_at", ""),
            })
    return results
