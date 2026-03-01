"""Collect IBM Cloud Classic DNS Domains and Records."""
import SoftLayer
from cloud_harvester.utils.formatting import safe_string

OBJECT_MASK = (
    "mask[id,name,serial,updateDate,"
    "resourceRecords[id,host,type,data,ttl,priority]]"
)


def _create_sl_client(api_key):
    return SoftLayer.create_client_from_env(username='apikey', api_key=api_key)


def _fetch_domains(api_key):
    """Fetch domains from the SoftLayer API."""
    client = _create_sl_client(api_key)
    account = client["SoftLayer_Account"]
    try:
        return account.getDomains(mask=OBJECT_MASK)
    except Exception:
        return []


def collect_dns_domains(api_key: str, token: str, regions: list[str]) -> list[dict]:
    """Collect all DNS domains."""
    domains = _fetch_domains(api_key)

    results = []
    for domain in domains:
        results.append({
            "id": domain.get("id"),
            "name": domain.get("name", ""),
            "serial": domain.get("serial", 0),
            "updateDate": domain.get("updateDate", ""),
            "recordCount": len(domain.get("resourceRecords", [])),
        })

    return results


def collect_dns_records(api_key: str, token: str, regions: list[str]) -> list[dict]:
    """Collect all DNS records (flattened from domains)."""
    domains = _fetch_domains(api_key)

    results = []
    for domain in domains:
        domain_id = domain.get("id")
        domain_name = domain.get("name", "")
        for record in domain.get("resourceRecords", []):
            results.append({
                "domainId": domain_id,
                "domainName": domain_name,
                "id": record.get("id"),
                "host": record.get("host", ""),
                "type": record.get("type", ""),
                "data": record.get("data", ""),
                "ttl": record.get("ttl", 0),
                "priority": record.get("priority"),
            })

    return results
