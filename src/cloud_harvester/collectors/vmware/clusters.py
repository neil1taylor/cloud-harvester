"""Collect VCF for Classic clusters."""
from cloud_harvester.collectors.vmware.client import VMwareClient


def collect_vmware_clusters(api_key: str, token: str, regions: list[str]) -> list[dict]:
    """Collect VMware clusters from all vCenter instances."""
    client = VMwareClient(token)

    try:
        instances = client.get_vcenter_instances()
    except Exception:
        return []

    results = []
    for inst in instances:
        instance_id = inst.get("id", "")
        if not instance_id:
            continue

        try:
            detail = client.get_vcenter_detail(instance_id)
        except Exception:
            continue

        location = inst.get("location", inst.get("datacenter", ""))
        clusters = detail.get("clusters", [])

        for cluster in clusters:
            cluster_id = cluster.get("id", cluster.get("cluster_id", ""))

            # Try to get host count from cluster detail or inline data
            hosts = (
                cluster.get("hosts", [])
                or cluster.get("esxi_hosts", [])
                or cluster.get("nodes", [])
            )

            results.append({
                "id": cluster_id,
                "name": cluster.get("name", ""),
                "location": cluster.get("location", location),
                "status": cluster.get("status", ""),
                "hostCount": len(hosts) if isinstance(hosts, list) else 0,
                "storageType": cluster.get("storage_type", cluster.get("storageType", "")),
                "instanceId": instance_id,
            })

    return results
