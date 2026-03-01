"""Collect VPC Dedicated Hosts."""
from cloud_harvester.collectors.vpc.client import VpcClient, VPC_REGIONS


def collect_vpc_dedicated_hosts(api_key: str, token: str, regions: list[str]) -> list[dict]:
    """Collect VPC dedicated hosts across all regions."""
    client = VpcClient(token)
    target_regions = [r for r in VPC_REGIONS if not regions or any(reg in r for reg in regions)]

    results = []
    for region in target_regions:
        try:
            items = client.list_resources(region, "dedicated_hosts", "dedicated_hosts")
        except Exception:
            continue

        for item in items:
            results.append({
                "id": item.get("id", ""),
                "name": item.get("name", ""),
                "state": item.get("state", ""),
                "profile": item.get("profile", {}).get("name", ""),
                "zone": item.get("zone", {}).get("name", ""),
                "vcpu": item.get("vcpu", {}).get("count", 0),
                "memory": item.get("memory", 0),
                "instanceCount": len(item.get("instances", [])),
                "region": region,
                "created_at": item.get("created_at", ""),
            })
    return results
