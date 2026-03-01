"""Collect VCFaaS virtual data centres (vDCs)."""
from cloud_harvester.collectors.vmware.client import VMwareClient, VCFAAS_REGIONS


def collect_vdcs(api_key: str, token: str, regions: list[str]) -> list[dict]:
    """Collect VCFaaS vDCs across all regions."""
    client = VMwareClient(token)
    target_regions = [r for r in VCFAAS_REGIONS if not regions or any(reg in r for reg in regions)]

    results = []
    for region in target_regions:
        try:
            vdcs = client.get_vcfaas_vdcs(region)
        except Exception:
            continue

        for vdc in vdcs:
            results.append({
                "id": vdc.get("id", ""),
                "name": vdc.get("name", ""),
                "status": vdc.get("status", ""),
                "directorSiteName": vdc.get("director_site", {}).get("name", "")
                    if isinstance(vdc.get("director_site"), dict)
                    else vdc.get("director_site_name", vdc.get("directorSiteName", "")),
                "cpu": vdc.get("cpu", ""),
                "ram": vdc.get("ram", ""),
                "disk": vdc.get("disk", ""),
                "region": region,
                "type": vdc.get("type", ""),
                "createdAt": vdc.get("created_at", vdc.get("createdAt", "")),
            })

    return results
