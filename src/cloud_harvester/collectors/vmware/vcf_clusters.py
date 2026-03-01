"""Collect VCFaaS clusters."""
from cloud_harvester.collectors.vmware.client import VMwareClient, VCFAAS_REGIONS


def collect_vcf_clusters(api_key: str, token: str, regions: list[str]) -> list[dict]:
    """Collect VCFaaS clusters from all PVDCs across regions."""
    client = VMwareClient(token)
    target_regions = [r for r in VCFAAS_REGIONS if not regions or any(reg in r for reg in regions)]

    results = []
    for region in target_regions:
        try:
            sites = client.get_vcfaas_director_sites(region)
        except Exception:
            continue

        for site in sites:
            site_id = site.get("id", "")
            if not site_id:
                continue

            try:
                pvdcs = client.get_vcfaas_pvdcs(region, site_id)
            except Exception:
                continue

            for pvdc in pvdcs:
                pvdc_id = pvdc.get("id", "")
                if not pvdc_id:
                    continue

                try:
                    clusters = client.get_vcfaas_clusters(region, site_id, pvdc_id)
                except Exception:
                    continue

                for cluster in clusters:
                    hosts = cluster.get("hosts", cluster.get("host_count", 0))
                    host_count = len(hosts) if isinstance(hosts, list) else hosts

                    results.append({
                        "id": cluster.get("id", ""),
                        "name": cluster.get("name", ""),
                        "hostCount": host_count,
                        "status": cluster.get("status", ""),
                        "datacenter": cluster.get("data_center", cluster.get("datacenter", "")),
                        "hostProfile": cluster.get("host_profile", cluster.get("hostProfile", "")),
                        "storageType": cluster.get("storage_type", cluster.get("storageType", "")),
                        "pvdcId": pvdc_id,
                    })

    return results
