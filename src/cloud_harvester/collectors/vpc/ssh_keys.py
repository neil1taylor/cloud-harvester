"""Collect VPC SSH Keys."""
from cloud_harvester.collectors.vpc.client import VpcClient, VPC_REGIONS


def collect_vpc_ssh_keys(api_key: str, token: str, regions: list[str]) -> list[dict]:
    """Collect VPC SSH keys across all regions."""
    client = VpcClient(token)
    target_regions = [r for r in VPC_REGIONS if not regions or any(reg in r for reg in regions)]

    results = []
    for region in target_regions:
        try:
            items = client.list_resources(region, "keys", "keys")
        except Exception:
            continue

        for item in items:
            results.append({
                "id": item.get("id", ""),
                "name": item.get("name", ""),
                "type": item.get("type", ""),
                "fingerprint": item.get("fingerprint", ""),
                "length": item.get("length", 0),
                "region": region,
                "created_at": item.get("created_at", ""),
            })
    return results
