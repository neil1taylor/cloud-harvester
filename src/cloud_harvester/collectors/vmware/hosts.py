"""Collect VCF for Classic hosts."""
from cloud_harvester.collectors.vmware.client import VMwareClient


def collect_vmware_hosts(api_key: str, token: str, regions: list[str]) -> list[dict]:
    """Collect VMware ESXi hosts from all clusters."""
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
            cluster_name = cluster.get("name", "")

            # Hosts can be in "hosts", "esxi_hosts", or "nodes"
            hosts = (
                cluster.get("hosts")
                or cluster.get("esxi_hosts")
                or cluster.get("nodes")
                or []
            )

            # If no inline hosts, try fetching cluster detail
            if not hosts and cluster_id:
                try:
                    cluster_detail = client.get_cluster_detail(instance_id, cluster_id)
                    hosts = (
                        cluster_detail.get("hosts")
                        or cluster_detail.get("esxi_hosts")
                        or cluster_detail.get("nodes")
                        or []
                    )
                except Exception:
                    pass

            for host in hosts:
                results.append({
                    "hostname": host.get("hostname", host.get("name", "")),
                    "publicIp": host.get("public_ip", host.get("publicIp", "")),
                    "privateIp": host.get("private_ip", host.get("privateIp", "")),
                    "status": host.get("status", ""),
                    "serverId": host.get("server_id", host.get("serverId", "")),
                    "version": host.get("version", ""),
                    "memory": host.get("memory", 0),
                    "cpus": host.get("cpus", host.get("cpu", 0)),
                    "clusterName": cluster_name,
                    "location": location,
                    "instanceId": instance_id,
                    "clusterId": cluster_id,
                })

    return results
