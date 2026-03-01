"""Collect IBM Cloud Classic Security Groups and Rules."""
import SoftLayer
from cloud_harvester.utils.formatting import safe_string

OBJECT_MASK = (
    "mask[id,name,description,createDate,modifyDate,"
    "rules[id,direction,protocol,portRangeMin,portRangeMax,"
    "remoteIp,remoteGroupId],networkComponentBindings]"
)


def _create_sl_client(api_key):
    return SoftLayer.create_client_from_env(api_key=api_key)


def collect_security_groups(api_key: str, token: str, regions: list[str]) -> list[dict]:
    """Collect all security groups."""
    client = _create_sl_client(api_key)
    account = client["SoftLayer_Account"]

    try:
        groups = account.getSecurityGroups(mask=OBJECT_MASK)
    except Exception:
        return []

    results = []
    for sg in groups:
        results.append({
            "id": sg.get("id"),
            "name": sg.get("name", ""),
            "description": sg.get("description", "") or "",
            "createDate": sg.get("createDate", ""),
            "modifyDate": sg.get("modifyDate", ""),
            "ruleCount": len(sg.get("rules", [])),
            "bindingCount": len(sg.get("networkComponentBindings", [])),
        })

    return results


def collect_security_group_rules(api_key: str, token: str, regions: list[str]) -> list[dict]:
    """Collect all security group rules (flattened from groups)."""
    client = _create_sl_client(api_key)
    account = client["SoftLayer_Account"]

    try:
        groups = account.getSecurityGroups(mask=OBJECT_MASK)
    except Exception:
        return []

    results = []
    for sg in groups:
        sg_id = sg.get("id")
        sg_name = sg.get("name", "")
        for rule in sg.get("rules", []):
            results.append({
                "securityGroupId": sg_id,
                "securityGroupName": sg_name,
                "id": rule.get("id"),
                "direction": rule.get("direction", ""),
                "protocol": rule.get("protocol", ""),
                "portRangeMin": rule.get("portRangeMin"),
                "portRangeMax": rule.get("portRangeMax"),
                "remoteIp": rule.get("remoteIp", ""),
                "remoteGroupId": rule.get("remoteGroupId"),
            })

    return results
