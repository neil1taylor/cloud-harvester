"""Collect VCFaaS PVDCs."""
from cloud_harvester.collectors.vmware.client import VMwareClient, VCFAAS_REGIONS


def collect_pvdcs(api_key: str, token: str, regions: list[str]) -> list[dict]:
    """Collect VCFaaS PVDCs from all director sites across regions."""
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
                clusters = pvdc.get("clusters", [])
                results.append({
                    "id": pvdc.get("id", ""),
                    "name": pvdc.get("name", ""),
                    "datacenter": pvdc.get("data_center", pvdc.get("datacenter", "")),
                    "status": pvdc.get("status", ""),
                    "providerType": pvdc.get("provider_type", pvdc.get("providerType", "")),
                    "clusterCount": len(clusters) if isinstance(clusters, list) else 0,
                    "directorSiteId": site_id,
                })

    return results
