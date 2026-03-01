"""Compute relationships between Classic infrastructure resources."""
from cloud_harvester.utils.formatting import safe_string


def collect_relationships(api_key: str, token: str, regions: list[str], context: dict | None = None) -> list[dict]:
    """Compute relationships from all collected Classic data.

    The context dict should contain all previously collected data keyed by
    resource type (e.g., "virtualServers", "vlans", "subnets", etc.).
    """
    if not context:
        return []

    results = []

    # VSI -> VLAN relationships
    for vsi in context.get("virtualServers", []):
        vlan_str = vsi.get("networkVlans", "")
        if vlan_str:
            for vlan_num in vlan_str.split(", "):
                vlan_num = vlan_num.strip()
                if vlan_num:
                    results.append({
                        "parentType": "virtualServer",
                        "parentId": vsi.get("id", 0),
                        "parentName": vsi.get("hostname", ""),
                        "childType": "vlan",
                        "childId": 0,
                        "childName": f"VLAN {vlan_num}",
                        "relationshipField": "networkVlans",
                    })

    # Bare Metal -> VLAN relationships
    for bm in context.get("bareMetal", []):
        vlan_str = bm.get("networkVlans", "")
        if vlan_str:
            for vlan_num in vlan_str.split(", "):
                vlan_num = vlan_num.strip()
                if vlan_num:
                    results.append({
                        "parentType": "bareMetal",
                        "parentId": bm.get("id", 0),
                        "parentName": bm.get("hostname", ""),
                        "childType": "vlan",
                        "childId": 0,
                        "childName": f"VLAN {vlan_num}",
                        "relationshipField": "networkVlans",
                    })

    # VLAN -> Subnet relationships
    vlans = context.get("vlans", [])
    subnets = context.get("subnets", [])
    for subnet in subnets:
        vlan_num = subnet.get("vlanNumber", 0)
        if vlan_num:
            # Find matching VLAN
            matching_vlan = next(
                (v for v in vlans if v.get("vlanNumber") == vlan_num), None
            )
            results.append({
                "parentType": "vlan",
                "parentId": matching_vlan.get("id", 0) if matching_vlan else 0,
                "parentName": f"VLAN {vlan_num}",
                "childType": "subnet",
                "childId": subnet.get("id", 0),
                "childName": subnet.get("networkIdentifier", ""),
                "relationshipField": "subnets",
            })

    # Gateway -> VLAN relationships
    for gw in context.get("gateways", []):
        gw_id = gw.get("id", 0)
        gw_name = gw.get("name", "")
        # Gateways are associated with VLANs through insideVlanCount
        if gw.get("insideVlanCount", 0) > 0:
            results.append({
                "parentType": "gateway",
                "parentId": gw_id,
                "parentName": gw_name,
                "childType": "vlan",
                "childId": 0,
                "childName": f"{gw.get('insideVlanCount', 0)} VLANs",
                "relationshipField": "insideVlans",
            })

    # Firewall -> VLAN relationships
    for fw in context.get("firewalls", []):
        vlan_num = fw.get("vlanNumber", 0)
        if vlan_num:
            results.append({
                "parentType": "firewall",
                "parentId": fw.get("id", 0),
                "parentName": fw.get("primaryIpAddress", ""),
                "childType": "vlan",
                "childId": 0,
                "childName": f"VLAN {vlan_num}",
                "relationshipField": "networkVlan",
            })

    # Block Storage -> VSI/Hardware relationships
    for bs in context.get("blockStorage", []):
        allowed_vsis = bs.get("allowedVirtualGuests", "")
        if allowed_vsis:
            for entry in allowed_vsis.split(", "):
                entry = entry.strip()
                if entry:
                    results.append({
                        "parentType": "blockStorage",
                        "parentId": bs.get("id", 0),
                        "parentName": bs.get("username", ""),
                        "childType": "virtualServer",
                        "childId": 0,
                        "childName": entry,
                        "relationshipField": "allowedVirtualGuests",
                    })

    # File Storage -> VSI/Hardware relationships
    for fs in context.get("fileStorage", []):
        allowed_vsis = fs.get("allowedVirtualGuests", "")
        if allowed_vsis:
            for entry in allowed_vsis.split(", "):
                entry = entry.strip()
                if entry:
                    results.append({
                        "parentType": "fileStorage",
                        "parentId": fs.get("id", 0),
                        "parentName": fs.get("username", ""),
                        "childType": "virtualServer",
                        "childId": 0,
                        "childName": entry,
                        "relationshipField": "allowedVirtualGuests",
                    })

    # Security Group -> Rule count (informational)
    for sg in context.get("securityGroups", []):
        if sg.get("bindingCount", 0) > 0:
            results.append({
                "parentType": "securityGroup",
                "parentId": sg.get("id", 0),
                "parentName": sg.get("name", ""),
                "childType": "networkComponent",
                "childId": 0,
                "childName": f"{sg.get('bindingCount', 0)} bindings",
                "relationshipField": "networkComponentBindings",
            })

    return results
