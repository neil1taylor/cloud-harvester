"""Collect VPC Instances."""
from cloud_harvester.collectors.vpc.client import VpcClient, VPC_REGIONS


def collect_vpc_instances(api_key: str, token: str, regions: list[str]) -> list[dict]:
    """Collect VPC instances across all regions."""
    client = VpcClient(token)
    target_regions = [r for r in VPC_REGIONS if not regions or any(reg in r for reg in regions)]

    results = []
    for region in target_regions:
        try:
            items = client.list_resources(region, "instances", "instances")
        except Exception:
            continue

        for item in items:
            results.append({
                "id": item.get("id", ""),
                "name": item.get("name", ""),
                "status": item.get("status", ""),
                "profile": item.get("profile", {}).get("name", ""),
                "vcpu": item.get("vcpu", {}).get("count", 0),
                "memory": item.get("memory", 0),
                "zone": item.get("zone", {}).get("name", ""),
                "vpcName": item.get("vpc", {}).get("name", ""),
                "primaryIp": item.get("primary_network_interface", {}).get("primary_ip", {}).get("address", ""),
                "region": region,
                "created_at": item.get("created_at", ""),
                "resourceGroup": item.get("resource_group", {}).get("name", ""),
            })
    return results
