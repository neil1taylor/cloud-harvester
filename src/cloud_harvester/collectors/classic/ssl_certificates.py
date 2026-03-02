"""Collect IBM Cloud Classic SSL Certificates."""
import SoftLayer

OBJECT_MASK = (
    "mask[id,commonName,organizationName,validityBegin,"
    "validityDays,validityEnd,createDate,notes]"
)


def _create_sl_client(api_key):
    return SoftLayer.create_client_from_env(username='apikey', api_key=api_key)


def collect_ssl_certificates(api_key: str, token: str, regions: list[str]) -> list[dict]:
    """Collect all SSL certificates."""
    client = _create_sl_client(api_key)
    account = client["SoftLayer_Account"]

    try:
        certs = account.getSecurityCertificates(mask=OBJECT_MASK)
    except Exception:
        return []

    results = []
    for cert in certs:
        results.append({
            "id": cert.get("id"),
            "commonName": cert.get("commonName", ""),
            "organizationName": cert.get("organizationName", ""),
            "validityBegin": cert.get("validityBegin", ""),
            "validityDays": cert.get("validityDays", 0),
            "validityEnd": cert.get("validityEnd", ""),
            "createDate": cert.get("createDate", ""),
            "notes": cert.get("notes", "") or "",
        })

    return results
