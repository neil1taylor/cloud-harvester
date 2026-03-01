"""Collect VPC Security Groups."""
from cloud_harvester.collectors.vpc.client import VpcClient, VPC_REGIONS


def collect_vpc_security_groups(api_key: str, token: str, regions: list[str]) -> list[dict]:
    """Collect VPC security groups across all regions."""
    client = VpcClient(token)
    target_regions = [r for r in VPC_REGIONS if not regions or any(reg in r for reg in regions)]

    results = []
    for region in target_regions:
        try:
            items = client.list_resources(region, "security_groups", "security_groups")
        except Exception:
            continue

        for item in items:
            results.append({
                "id": item.get("id", ""),
                "name": item.get("name", ""),
                "vpcName": item.get("vpc", {}).get("name", ""),
                "ruleCount": len(item.get("rules", [])),
                "targetCount": len(item.get("targets", [])),
                "region": region,
                "created_at": item.get("created_at", ""),
            })
    return results
