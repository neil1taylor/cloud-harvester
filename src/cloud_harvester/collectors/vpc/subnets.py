"""Collect VPC Subnets."""
from cloud_harvester.collectors.vpc.client import VpcClient, VPC_REGIONS


def collect_vpc_subnets(api_key: str, token: str, regions: list[str]) -> list[dict]:
    """Collect VPC subnets across all regions."""
    client = VpcClient(token)
    target_regions = [r for r in VPC_REGIONS if not regions or any(reg in r for reg in regions)]

    results = []
    for region in target_regions:
        try:
            items = client.list_resources(region, "subnets", "subnets")
        except Exception:
            continue

        for item in items:
            results.append({
                "id": item.get("id", ""),
                "name": item.get("name", ""),
                "status": item.get("status", ""),
                "cidr": item.get("ipv4_cidr_block", ""),
                "availableIps": item.get("available_ipv4_address_count", 0),
                "totalIps": item.get("total_ipv4_address_count", 0),
                "zone": item.get("zone", {}).get("name", ""),
                "vpcName": item.get("vpc", {}).get("name", ""),
                "region": region,
                "created_at": item.get("created_at", ""),
            })
    return results
