"""Tests for Classic infrastructure relationship builder."""
from cloud_harvester.collectors.classic.relationships import collect_relationships


def test_empty_context_returns_empty():
    """When context is None or empty, no relationships should be produced."""
    assert collect_relationships("key", "token", []) == []
    assert collect_relationships("key", "token", [], context=None) == []
    assert collect_relationships("key", "token", [], context={}) == []


def test_vsi_to_vlan_relationships():
    """Virtual servers with networkVlans produce VSI -> VLAN rows."""
    context = {
        "virtualServers": [
            {"id": 100, "hostname": "web01", "networkVlans": "1234, 5678"},
        ],
    }
    result = collect_relationships("key", "token", [], context=context)
    assert len(result) == 2
    assert result[0] == {
        "parentType": "virtualServer",
        "parentId": 100,
        "parentName": "web01",
        "childType": "vlan",
        "childId": 0,
        "childName": "VLAN 1234",
        "relationshipField": "networkVlans",
    }
    assert result[1]["childName"] == "VLAN 5678"


def test_bare_metal_to_vlan_relationships():
    """Bare metal servers with networkVlans produce BM -> VLAN rows."""
    context = {
        "bareMetal": [
            {"id": 200, "hostname": "bm01", "networkVlans": "900"},
        ],
    }
    result = collect_relationships("key", "token", [], context=context)
    assert len(result) == 1
    assert result[0]["parentType"] == "bareMetal"
    assert result[0]["parentId"] == 200
    assert result[0]["parentName"] == "bm01"
    assert result[0]["childType"] == "vlan"
    assert result[0]["childName"] == "VLAN 900"
    assert result[0]["relationshipField"] == "networkVlans"


def test_vlan_to_subnet_relationships():
    """Subnets with a vlanNumber produce VLAN -> Subnet rows, matching VLAN id when available."""
    context = {
        "vlans": [
            {"id": 10, "vlanNumber": 1234},
            {"id": 11, "vlanNumber": 5678},
        ],
        "subnets": [
            {"id": 300, "networkIdentifier": "10.0.0.0/24", "vlanNumber": 1234},
            {"id": 301, "networkIdentifier": "172.16.0.0/16", "vlanNumber": 5678},
        ],
    }
    result = collect_relationships("key", "token", [], context=context)
    assert len(result) == 2

    first = result[0]
    assert first["parentType"] == "vlan"
    assert first["parentId"] == 10
    assert first["parentName"] == "VLAN 1234"
    assert first["childType"] == "subnet"
    assert first["childId"] == 300
    assert first["childName"] == "10.0.0.0/24"
    assert first["relationshipField"] == "subnets"

    second = result[1]
    assert second["parentId"] == 11
    assert second["childId"] == 301


def test_vlan_to_subnet_no_matching_vlan():
    """When a subnet references a VLAN that is not in the vlans list, parentId should be 0."""
    context = {
        "vlans": [],
        "subnets": [
            {"id": 400, "networkIdentifier": "192.168.0.0/24", "vlanNumber": 9999},
        ],
    }
    result = collect_relationships("key", "token", [], context=context)
    assert len(result) == 1
    assert result[0]["parentId"] == 0
    assert result[0]["parentName"] == "VLAN 9999"


def test_gateway_to_vlan_relationships():
    """Gateways with insideVlanCount > 0 produce Gateway -> VLAN rows."""
    context = {
        "gateways": [
            {"id": 500, "name": "gw01", "insideVlanCount": 3},
            {"id": 501, "name": "gw02", "insideVlanCount": 0},
        ],
    }
    result = collect_relationships("key", "token", [], context=context)
    # Only gw01 has insideVlanCount > 0
    assert len(result) == 1
    assert result[0]["parentType"] == "gateway"
    assert result[0]["parentId"] == 500
    assert result[0]["parentName"] == "gw01"
    assert result[0]["childType"] == "vlan"
    assert result[0]["childName"] == "3 VLANs"
    assert result[0]["relationshipField"] == "insideVlans"


def test_firewall_to_vlan_relationships():
    """Firewalls with a vlanNumber produce Firewall -> VLAN rows."""
    context = {
        "firewalls": [
            {"id": 600, "primaryIpAddress": "10.0.0.5", "vlanNumber": 4567},
        ],
    }
    result = collect_relationships("key", "token", [], context=context)
    assert len(result) == 1
    assert result[0]["parentType"] == "firewall"
    assert result[0]["parentId"] == 600
    assert result[0]["parentName"] == "10.0.0.5"
    assert result[0]["childType"] == "vlan"
    assert result[0]["childName"] == "VLAN 4567"
    assert result[0]["relationshipField"] == "networkVlan"


def test_block_storage_to_vsi_relationships():
    """Block storage with allowedVirtualGuests produces BlockStorage -> VSI rows."""
    context = {
        "blockStorage": [
            {"id": 700, "username": "SL01SEL-1", "allowedVirtualGuests": "web01, web02"},
        ],
    }
    result = collect_relationships("key", "token", [], context=context)
    assert len(result) == 2
    assert result[0]["parentType"] == "blockStorage"
    assert result[0]["parentId"] == 700
    assert result[0]["parentName"] == "SL01SEL-1"
    assert result[0]["childType"] == "virtualServer"
    assert result[0]["childName"] == "web01"
    assert result[0]["relationshipField"] == "allowedVirtualGuests"
    assert result[1]["childName"] == "web02"


def test_file_storage_to_vsi_relationships():
    """File storage with allowedVirtualGuests produces FileStorage -> VSI rows."""
    context = {
        "fileStorage": [
            {"id": 800, "username": "SL01SEL-2", "allowedVirtualGuests": "db01"},
        ],
    }
    result = collect_relationships("key", "token", [], context=context)
    assert len(result) == 1
    assert result[0]["parentType"] == "fileStorage"
    assert result[0]["parentId"] == 800
    assert result[0]["parentName"] == "SL01SEL-2"
    assert result[0]["childType"] == "virtualServer"
    assert result[0]["childName"] == "db01"
    assert result[0]["relationshipField"] == "allowedVirtualGuests"


def test_security_group_bindings():
    """Security groups with bindingCount > 0 produce SecurityGroup -> networkComponent rows."""
    context = {
        "securityGroups": [
            {"id": 900, "name": "sg-allow-ssh", "bindingCount": 5},
            {"id": 901, "name": "sg-no-bindings", "bindingCount": 0},
        ],
    }
    result = collect_relationships("key", "token", [], context=context)
    # Only sg-allow-ssh has bindings
    assert len(result) == 1
    assert result[0]["parentType"] == "securityGroup"
    assert result[0]["parentId"] == 900
    assert result[0]["parentName"] == "sg-allow-ssh"
    assert result[0]["childType"] == "networkComponent"
    assert result[0]["childName"] == "5 bindings"
    assert result[0]["relationshipField"] == "networkComponentBindings"


def test_combined_context_builds_all_relationships():
    """A full context with multiple resource types produces the expected total count."""
    context = {
        "virtualServers": [
            {"id": 1, "hostname": "vs1", "networkVlans": "100"},
        ],
        "bareMetal": [
            {"id": 2, "hostname": "bm1", "networkVlans": "200"},
        ],
        "vlans": [
            {"id": 10, "vlanNumber": 100},
        ],
        "subnets": [
            {"id": 20, "networkIdentifier": "10.0.0.0/24", "vlanNumber": 100},
        ],
        "gateways": [
            {"id": 30, "name": "gw1", "insideVlanCount": 2},
        ],
        "firewalls": [
            {"id": 40, "primaryIpAddress": "10.0.0.1", "vlanNumber": 100},
        ],
        "blockStorage": [
            {"id": 50, "username": "bs1", "allowedVirtualGuests": "vs1"},
        ],
        "fileStorage": [
            {"id": 60, "username": "fs1", "allowedVirtualGuests": "vs1"},
        ],
        "securityGroups": [
            {"id": 70, "name": "sg1", "bindingCount": 1},
        ],
    }
    result = collect_relationships("key", "token", [], context=context)
    # 1 VSI->VLAN + 1 BM->VLAN + 1 VLAN->Subnet + 1 GW->VLAN + 1 FW->VLAN
    # + 1 Block->VSI + 1 File->VSI + 1 SG->NC = 8
    assert len(result) == 8

    parent_types = [r["parentType"] for r in result]
    assert "virtualServer" in parent_types
    assert "bareMetal" in parent_types
    assert "vlan" in parent_types
    assert "gateway" in parent_types
    assert "firewall" in parent_types
    assert "blockStorage" in parent_types
    assert "fileStorage" in parent_types
    assert "securityGroup" in parent_types


def test_vsi_with_empty_vlan_string():
    """A VSI with an empty networkVlans string should not produce any relationships."""
    context = {
        "virtualServers": [
            {"id": 1, "hostname": "vs-no-vlan", "networkVlans": ""},
        ],
    }
    result = collect_relationships("key", "token", [], context=context)
    assert result == []


def test_block_storage_empty_allowed_guests():
    """Block storage with no allowed guests should not produce any relationships."""
    context = {
        "blockStorage": [
            {"id": 1, "username": "bs-empty", "allowedVirtualGuests": ""},
        ],
    }
    result = collect_relationships("key", "token", [], context=context)
    assert result == []
