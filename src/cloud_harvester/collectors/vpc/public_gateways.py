"""Collect VPC Public Gateways."""
from cloud_harvester.collectors.vpc.client import VpcClient, VPC_REGIONS


def collect_vpc_public_gateways(api_key: str, token: str, regions: list[str]) -> list[dict]:
    """Collect VPC public gateways across all regions."""
    client = VpcClient(token)
    target_regions = [r for r in VPC_REGIONS if not regions or any(reg in r for reg in regions)]

    results = []
    for region in target_regions:
        try:
            items = client.list_resources(region, "public_gateways", "public_gateways")
        except Exception:
            continue

        for item in items:
            results.append({
                "id": item.get("id", ""),
                "name": item.get("name", ""),
                "status": item.get("status", ""),
                "vpcName": item.get("vpc", {}).get("name", ""),
                "floatingIp": item.get("floating_ip", {}).get("address", ""),
                "zone": item.get("zone", {}).get("name", ""),
                "region": region,
                "created_at": item.get("created_at", ""),
            })
    return results
