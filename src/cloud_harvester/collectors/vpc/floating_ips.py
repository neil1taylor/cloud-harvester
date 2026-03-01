"""Collect VPC Floating IPs."""
from cloud_harvester.collectors.vpc.client import VpcClient, VPC_REGIONS


def collect_vpc_floating_ips(api_key: str, token: str, regions: list[str]) -> list[dict]:
    """Collect VPC floating IPs across all regions."""
    client = VpcClient(token)
    target_regions = [r for r in VPC_REGIONS if not regions or any(reg in r for reg in regions)]

    results = []
    for region in target_regions:
        try:
            items = client.list_resources(region, "floating_ips", "floating_ips")
        except Exception:
            continue

        for item in items:
            target = item.get("target", {})
            target_name = target.get("name", "") if target else ""
            results.append({
                "id": item.get("id", ""),
                "name": item.get("name", ""),
                "address": item.get("address", ""),
                "status": item.get("status", ""),
                "target": target_name,
                "zone": item.get("zone", {}).get("name", ""),
                "region": region,
                "created_at": item.get("created_at", ""),
            })
    return results
