"""Collect VPC Flow Log Collectors."""
from cloud_harvester.collectors.vpc.client import VpcClient, VPC_REGIONS


def collect_vpc_flow_logs(api_key: str, token: str, regions: list[str]) -> list[dict]:
    """Collect VPC flow log collectors across all regions."""
    client = VpcClient(token)
    target_regions = [r for r in VPC_REGIONS if not regions or any(reg in r for reg in regions)]

    results = []
    for region in target_regions:
        try:
            items = client.list_resources(
                region, "flow_log_collectors", "flow_log_collectors"
            )
        except Exception:
            continue

        for item in items:
            target = item.get("target", {})
            target_name = target.get("name", "") or target.get("id", "")
            bucket = item.get("storage_bucket", {})
            bucket_name = bucket.get("name", "") if isinstance(bucket, dict) else str(bucket)
            results.append({
                "id": item.get("id", ""),
                "name": item.get("name", ""),
                "active": item.get("active", False),
                "lifecycleState": item.get("lifecycle_state", ""),
                "target": target_name,
                "storageBucket": bucket_name,
                "region": region,
                "created_at": item.get("created_at", ""),
            })
    return results
