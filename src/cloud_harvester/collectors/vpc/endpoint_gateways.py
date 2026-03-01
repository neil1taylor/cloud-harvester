"""Collect VPC Endpoint Gateways (VPE)."""
from cloud_harvester.collectors.vpc.client import VpcClient, VPC_REGIONS


def collect_vpc_endpoint_gateways(api_key: str, token: str, regions: list[str]) -> list[dict]:
    """Collect VPC endpoint gateways across all regions."""
    client = VpcClient(token)
    target_regions = [r for r in VPC_REGIONS if not regions or any(reg in r for reg in regions)]

    results = []
    for region in target_regions:
        try:
            items = client.list_resources(region, "endpoint_gateways", "endpoint_gateways")
        except Exception:
            continue

        for item in items:
            target = item.get("target", {})
            target_name = target.get("name", "") or target.get("resource_type", "")
            results.append({
                "id": item.get("id", ""),
                "name": item.get("name", ""),
                "lifecycleState": item.get("lifecycle_state", ""),
                "healthState": item.get("health_state", ""),
                "target": target_name,
                "vpcName": item.get("vpc", {}).get("name", ""),
                "region": region,
                "created_at": item.get("created_at", ""),
            })
    return results
