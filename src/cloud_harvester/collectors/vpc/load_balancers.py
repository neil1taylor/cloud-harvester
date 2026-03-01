"""Collect VPC Load Balancers."""
from cloud_harvester.collectors.vpc.client import VpcClient, VPC_REGIONS


def collect_vpc_load_balancers(api_key: str, token: str, regions: list[str]) -> list[dict]:
    """Collect VPC load balancers across all regions."""
    client = VpcClient(token)
    target_regions = [r for r in VPC_REGIONS if not regions or any(reg in r for reg in regions)]

    results = []
    for region in target_regions:
        try:
            items = client.list_resources(region, "load_balancers", "load_balancers")
        except Exception:
            continue

        for item in items:
            results.append({
                "id": item.get("id", ""),
                "name": item.get("name", ""),
                "hostname": item.get("hostname", ""),
                "isPublic": item.get("is_public", False),
                "operatingStatus": item.get("operating_status", ""),
                "provisioningStatus": item.get("provisioning_status", ""),
                "region": region,
                "created_at": item.get("created_at", ""),
            })
    return results
