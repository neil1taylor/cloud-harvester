"""Collect VPC VPN Gateways."""
from cloud_harvester.collectors.vpc.client import VpcClient, VPC_REGIONS


def collect_vpc_vpn_gateways(api_key: str, token: str, regions: list[str]) -> list[dict]:
    """Collect VPC VPN gateways across all regions."""
    client = VpcClient(token)
    target_regions = [r for r in VPC_REGIONS if not regions or any(reg in r for reg in regions)]

    results = []
    for region in target_regions:
        try:
            items = client.list_resources(region, "vpn_gateways", "vpn_gateways")
        except Exception:
            continue

        for item in items:
            results.append({
                "id": item.get("id", ""),
                "name": item.get("name", ""),
                "status": item.get("status", ""),
                "mode": item.get("mode", ""),
                "subnet": item.get("subnet", {}).get("name", ""),
                "region": region,
                "created_at": item.get("created_at", ""),
            })
    return results
