"""Tests for classic infrastructure collectors."""
from unittest.mock import patch, MagicMock
from cloud_harvester.collectors.classic.virtual_servers import collect_virtual_servers
from cloud_harvester.collectors.classic.bare_metal import collect_bare_metal
from cloud_harvester.collectors.classic.block_storage import collect_block_storage


def test_collect_virtual_servers():
    mock_client = MagicMock()
    mock_client.__getitem__ = MagicMock(return_value=MagicMock())
    mock_account = mock_client["SoftLayer_Account"]
    mock_account.getVirtualGuests.return_value = [
        {
            "id": 123,
            "hostname": "web01",
            "domain": "test.com",
            "fullyQualifiedDomainName": "web01.test.com",
            "primaryIpAddress": "10.0.0.1",
            "primaryBackendIpAddress": "10.0.0.2",
            "maxCpu": 4,
            "maxMemory": 8192,
            "startCpus": 4,
            "status": {"keyName": "ACTIVE"},
            "powerState": {"keyName": "RUNNING"},
            "datacenter": {"name": "dal13"},
            "operatingSystem": {"softwareDescription": {"name": "Ubuntu", "version": "22.04"}},
            "hourlyBillingFlag": False,
            "createDate": "2025-01-01T00:00:00",
            "modifyDate": "2025-02-01T00:00:00",
            "billingItem": {"recurringFee": "150.00"},
            "networkVlans": [{"vlanNumber": 1234}],
            "blockDevices": [{"diskImage": {"capacity": 100}}],
            "tagReferences": [{"tag": {"name": "web"}}],
            "notes": "test",
            "privateNetworkOnlyFlag": False,
            "localDiskFlag": False,
            "dedicatedAccountHostOnlyFlag": False,
            "placementGroupId": None,
        }
    ]

    with patch("cloud_harvester.collectors.classic.virtual_servers._create_sl_client", return_value=mock_client):
        result = collect_virtual_servers("test-key", "token", [])
    assert len(result) == 1
    assert result[0]["id"] == 123
    assert result[0]["hostname"] == "web01"
    assert result[0]["datacenter"] == "dal13"
    assert result[0]["hourlyBilling"] == "No"
    assert result[0]["os"] == "Ubuntu 22.04"
    assert result[0]["status"] == "ACTIVE"
    assert result[0]["powerState"] == "RUNNING"
    assert result[0]["recurringFee"] == "150.00"
    assert result[0]["costBasis"] == "Monthly"
    assert result[0]["diskGb"] == 100
    assert result[0]["networkVlans"] == "1234"
    assert result[0]["tags"] == "web"
    assert result[0]["privateNetworkOnly"] == "No"
    assert result[0]["localDisk"] == "No"
    assert result[0]["dedicated"] == "No"


def test_collect_virtual_servers_region_filter():
    mock_client = MagicMock()
    mock_client.__getitem__ = MagicMock(return_value=MagicMock())
    mock_account = mock_client["SoftLayer_Account"]
    mock_account.getVirtualGuests.return_value = [
        {
            "id": 1,
            "hostname": "dal-vm",
            "domain": "test.com",
            "fullyQualifiedDomainName": "dal-vm.test.com",
            "datacenter": {"name": "dal13"},
            "status": {},
            "powerState": {},
            "operatingSystem": {},
            "billingItem": {},
            "networkVlans": [],
            "blockDevices": [],
            "tagReferences": [],
        },
        {
            "id": 2,
            "hostname": "wdc-vm",
            "domain": "test.com",
            "fullyQualifiedDomainName": "wdc-vm.test.com",
            "datacenter": {"name": "wdc04"},
            "status": {},
            "powerState": {},
            "operatingSystem": {},
            "billingItem": {},
            "networkVlans": [],
            "blockDevices": [],
            "tagReferences": [],
        },
    ]

    with patch("cloud_harvester.collectors.classic.virtual_servers._create_sl_client", return_value=mock_client):
        result = collect_virtual_servers("test-key", "token", ["dal"])
    assert len(result) == 1
    assert result[0]["hostname"] == "dal-vm"


def test_collect_bare_metal():
    mock_client = MagicMock()
    mock_client.__getitem__ = MagicMock(return_value=MagicMock())
    mock_account = mock_client["SoftLayer_Account"]
    mock_account.getHardware.return_value = [
        {
            "id": 456,
            "hostname": "bm01",
            "domain": "test.com",
            "fullyQualifiedDomainName": "bm01.test.com",
            "manufacturerSerialNumber": "SN123",
            "primaryIpAddress": "10.0.1.1",
            "primaryBackendIpAddress": "10.0.1.2",
            "processorPhysicalCoreAmount": 16,
            "memoryCapacity": 64,
            "datacenter": {"name": "wdc04"},
            "operatingSystem": {"softwareDescription": {"name": "RHEL", "version": "8"}},
            "billingItem": {"recurringFee": "500.00"},
            "provisionDate": "2025-01-15T00:00:00",
            "powerSupplyCount": 2,
            "networkGatewayMemberFlag": False,
            "networkVlans": [],
            "tagReferences": [],
            "notes": "",
            "hardDrives": [],
            "networkComponents": [],
        }
    ]

    with patch("cloud_harvester.collectors.classic.bare_metal._create_sl_client", return_value=mock_client):
        result = collect_bare_metal("test-key", "token", [])
    assert len(result) == 1
    assert result[0]["id"] == 456
    assert result[0]["hostname"] == "bm01"
    assert result[0]["datacenter"] == "wdc04"
    assert result[0]["os"] == "RHEL 8"
    assert result[0]["serialNumber"] == "SN123"
    assert result[0]["cores"] == 16
    assert result[0]["memory"] == 64
    assert result[0]["recurringFee"] == "500.00"
    assert result[0]["gatewayMember"] == "No"
    assert result[0]["vmwareRole"] == ""


def test_collect_bare_metal_vmware_detection():
    mock_client = MagicMock()
    mock_client.__getitem__ = MagicMock(return_value=MagicMock())
    mock_account = mock_client["SoftLayer_Account"]
    mock_account.getHardware.return_value = [
        {
            "id": 789,
            "hostname": "esxi-host01",
            "domain": "vmware.test.com",
            "fullyQualifiedDomainName": "esxi-host01.vmware.test.com",
            "manufacturerSerialNumber": "SN456",
            "primaryIpAddress": "10.0.2.1",
            "primaryBackendIpAddress": "10.0.2.2",
            "processorPhysicalCoreAmount": 32,
            "memoryCapacity": 256,
            "datacenter": {"name": "dal13"},
            "operatingSystem": {"softwareDescription": {"name": "VMware ESXi", "version": "7.0"}},
            "billingItem": {"recurringFee": "1500.00"},
            "provisionDate": "2025-03-01T00:00:00",
            "powerSupplyCount": 2,
            "networkGatewayMemberFlag": False,
            "networkVlans": [{"vlanNumber": 100}, {"vlanNumber": 200}],
            "tagReferences": [{"tag": {"name": "vmware"}}, {"tag": {"name": "production"}}],
            "notes": "ESXi host",
            "hardDrives": [{"capacity": 960}, {"capacity": 960}],
            "networkComponents": [
                {"speed": 10000, "status": "ACTIVE"},
                {"speed": 1000, "status": "ACTIVE"},
            ],
        }
    ]

    with patch("cloud_harvester.collectors.classic.bare_metal._create_sl_client", return_value=mock_client):
        result = collect_bare_metal("test-key", "token", [])
    assert len(result) == 1
    assert result[0]["vmwareRole"] == "ESXi Host"
    assert result[0]["tags"] == "vmware, production"
    assert result[0]["networkVlans"] == "100, 200"
    assert "960" in result[0]["hardDrives"]
    assert "10000Mbps" in result[0]["networkComponents"]


def test_collect_block_storage():
    mock_client = MagicMock()
    mock_client.__getitem__ = MagicMock(return_value=MagicMock())
    mock_account = mock_client["SoftLayer_Account"]
    mock_account.getIscsiNetworkStorage.return_value = [
        {
            "id": 721685964,
            "username": "IBM02SEL1041833-888",
            "capacityGb": 20,
            "iops": "100",
            "storageType": {"keyName": "endurance_block_storage"},
            "storageTierLevel": "LOW_INTENSITY_TIER",
            "serviceResourceBackendIpAddress": "198.51.100.42",
            "lunId": 0,
            "snapshotCapacityGb": 5,
            "hasEncryptionAtRest": True,
            "serviceResource": {"datacenter": {"name": "dal13"}},
            "parentVolume": {"snapshotSizeBytes": 163840},
            "replicationStatus": "REPLICATION_PROVISIONING_COMPLETED",
            "billingItem": {"recurringFee": "10.00"},
            "createDate": "2025-10-01T00:00:00",
            "notes": "test volume",
            "allowedVirtualGuests": [{"id": 123, "hostname": "web01"}],
            "allowedHardware": [{"id": 456, "hostname": "bm01"}],
            "allowedSubnets": [
                {"id": 1, "networkIdentifier": "10.0.0.0", "cidr": 24},
                {"id": 2, "networkIdentifier": "10.0.1.0", "cidr": 28},
            ],
            "replicationPartners": [
                {
                    "id": 721870496,
                    "username": "IBM02SEL1041833_888_REP_1",
                    "serviceResourceBackendIpAddress": "198.51.100.43",
                    "serviceResource": {"datacenter": {"name": "dal14"}},
                    "replicationSchedule": {"type": {"keyname": "REPLICATION_HOURLY"}},
                },
            ],
        }
    ]
    mock_account.getNetworkStorage.return_value = []

    with patch("cloud_harvester.collectors.classic.block_storage._create_sl_client", return_value=mock_client):
        result = collect_block_storage("test-key", "token", [])

    assert len(result) == 1
    r = result[0]
    assert r["id"] == 721685964
    assert r["datacenter"] == "dal13"
    assert r["encrypted"] is True
    assert r["allowedSubnets"] == "10.0.0.0/24, 10.0.1.0/28"
    assert r["snapshotSizeBytes"] == 163840
    assert r["replicationStatus"] == "REPLICATION_PROVISIONING_COMPLETED"
    assert "dal14" in r["replicationPartners"]
    assert "REPLICATION_HOURLY" in r["replicationPartners"]


def test_collect_block_storage_missing_new_fields():
    """New fields default gracefully when absent from API response."""
    mock_client = MagicMock()
    mock_client.__getitem__ = MagicMock(return_value=MagicMock())
    mock_account = mock_client["SoftLayer_Account"]
    mock_account.getIscsiNetworkStorage.return_value = [
        {
            "id": 100,
            "username": "test-vol",
            "storageType": {"keyName": "performance_block_storage"},
        }
    ]
    mock_account.getNetworkStorage.return_value = []

    with patch("cloud_harvester.collectors.classic.block_storage._create_sl_client", return_value=mock_client):
        result = collect_block_storage("test-key", "token", [])

    assert len(result) == 1
    r = result[0]
    assert r["datacenter"] == ""
    assert r["encrypted"] is False
    assert r["allowedSubnets"] == ""
    assert r["snapshotSizeBytes"] == 0
    assert r["replicationStatus"] == ""
