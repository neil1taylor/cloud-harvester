"""Collect VPC Network ACLs."""
from cloud_harvester.collectors.vpc.client import VpcClient, VPC_REGIONS


def collect_vpc_network_acls(api_key: str, token: str, regions: list[str]) -> list[dict]:
    """Collect VPC network ACLs across all regions."""
    client = VpcClient(token)
    target_regions = [r for r in VPC_REGIONS if not regions or any(reg in r for reg in regions)]

    results = []
    for region in target_regions:
        try:
            items = client.list_resources(region, "network_acls", "network_acls")
        except Exception:
            continue

        for item in items:
            results.append({
                "id": item.get("id", ""),
                "name": item.get("name", ""),
                "vpcName": item.get("vpc", {}).get("name", ""),
                "ruleCount": len(item.get("rules", [])),
                "subnetCount": len(item.get("subnets", [])),
                "region": region,
                "created_at": item.get("created_at", ""),
            })
    return results
