"""Tests for VMware/VCF infrastructure collectors."""
from unittest.mock import patch, MagicMock
from cloud_harvester.collectors.vmware.instances import collect_vmware_instances
from cloud_harvester.collectors.vmware.hosts import collect_vmware_hosts
from cloud_harvester.collectors.vmware.cross_references import collect_vmware_cross_references


MOCK_VCENTER_LIST = [
    {
        "id": "vc-001",
        "name": "vcenter-dallas",
        "location": "dal10",
        "status": "ReadyToUse",
        "deploy_type": "single-node",
        "domain_type": "primary",
        "nsx_type": "nsx-t",
        "version": "7.0u3",
        "creator": "admin@ibm.com",
        "crn": "crn:v1:bluemix:public:vmware:dal10:a/abc123::vcenter:vc-001",
    }
]

MOCK_VCENTER_DETAIL = {
    "id": "vc-001",
    "name": "vcenter-dallas",
    "version": "7.0u3",
    "creator": "admin@ibm.com",
    "crn": "crn:v1:bluemix:public:vmware:dal10:a/abc123::vcenter:vc-001",
    "clusters": [
        {
            "id": "cl-001",
            "name": "mgmt-cluster",
            "status": "ReadyToUse",
            "storage_type": "vSAN",
            "hosts": [
                {
                    "hostname": "esxi-host-01",
                    "public_ip": "169.60.100.1",
                    "private_ip": "10.200.50.1",
                    "status": "Ready",
                    "server_id": "bm-12345",
                    "version": "7.0.3",
                    "memory": 512,
                    "cpus": 32,
                },
                {
                    "hostname": "esxi-host-02",
                    "public_ip": "169.60.100.2",
                    "private_ip": "10.200.50.2",
                    "status": "Ready",
                    "server_id": "bm-12346",
                    "version": "7.0.3",
                    "memory": 512,
                    "cpus": 32,
                },
            ],
        }
    ],
}


def test_collect_vmware_instances():
    """Test collect_vmware_instances with mocked VMwareClient."""
    mock_client = MagicMock()
    mock_client.get_vcenter_instances.return_value = MOCK_VCENTER_LIST
    mock_client.get_vcenter_detail.return_value = MOCK_VCENTER_DETAIL

    with patch(
        "cloud_harvester.collectors.vmware.instances.VMwareClient",
        return_value=mock_client,
    ):
        result = collect_vmware_instances("test-key", "test-token", [])

    assert len(result) == 1
    inst = result[0]
    assert inst["id"] == "vc-001"
    assert inst["name"] == "vcenter-dallas"
    assert inst["location"] == "dal10"
    assert inst["status"] == "ReadyToUse"
    assert inst["deployType"] == "single-node"
    assert inst["domainType"] == "primary"
    assert inst["nsxType"] == "nsx-t"
    assert inst["version"] == "7.0u3"
    assert inst["clusterCount"] == 1
    assert inst["creator"] == "admin@ibm.com"
    assert inst["crn"] == "crn:v1:bluemix:public:vmware:dal10:a/abc123::vcenter:vc-001"


def test_collect_vmware_hosts():
    """Test collect_vmware_hosts with mocked VMwareClient."""
    mock_client = MagicMock()
    mock_client.get_vcenter_instances.return_value = MOCK_VCENTER_LIST
    mock_client.get_vcenter_detail.return_value = MOCK_VCENTER_DETAIL

    with patch(
        "cloud_harvester.collectors.vmware.hosts.VMwareClient",
        return_value=mock_client,
    ):
        result = collect_vmware_hosts("test-key", "test-token", [])

    assert len(result) == 2

    first = result[0]
    assert first["hostname"] == "esxi-host-01"
    assert first["publicIp"] == "169.60.100.1"
    assert first["privateIp"] == "10.200.50.1"
    assert first["status"] == "Ready"
    assert first["serverId"] == "bm-12345"
    assert first["version"] == "7.0.3"
    assert first["memory"] == 512
    assert first["cpus"] == 32
    assert first["clusterName"] == "mgmt-cluster"
    assert first["location"] == "dal10"
    assert first["instanceId"] == "vc-001"
    assert first["clusterId"] == "cl-001"

    second = result[1]
    assert second["hostname"] == "esxi-host-02"
    assert second["privateIp"] == "10.200.50.2"


def test_collect_vmware_cross_references():
    """Test cross-reference matching between classic bare metal and VMware hosts."""
    context = {
        "bareMetal": [
            {
                "id": 12345,
                "hostname": "esxi-host-01",
                "backendIp": "10.200.50.1",
                "vmwareRole": "ESXi Host",
            },
            {
                "id": 99999,
                "hostname": "web-server-01",
                "backendIp": "10.200.60.1",
                "vmwareRole": "",
            },
        ],
        "vmwareHosts": [
            {
                "hostname": "esxi-host-01",
                "privateIp": "10.200.50.1",
                "clusterId": "cl-001",
            },
        ],
    }

    result = collect_vmware_cross_references("test-key", "test-token", [], context=context)

    # Only the bare metal with a vmwareRole should appear
    assert len(result) == 1
    ref = result[0]
    assert ref["classicResourceType"] == "bareMetal"
    assert ref["classicResourceId"] == "12345"
    assert ref["classicResourceName"] == "esxi-host-01"
    assert ref["vmwareRole"] == "ESXi Host"
    assert ref["vmwareResourceType"] == "vmwareHost"
    assert ref["vmwareResourceName"] == "esxi-host-01"


def test_collect_vmware_cross_references_no_context():
    """Test cross-references returns empty list when no context provided."""
    result = collect_vmware_cross_references("test-key", "test-token", [])
    assert result == []

    result = collect_vmware_cross_references("test-key", "test-token", [], context={})
    assert result == []
