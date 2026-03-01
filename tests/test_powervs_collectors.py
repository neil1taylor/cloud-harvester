"""Tests for PowerVS infrastructure collectors."""
from unittest.mock import patch, MagicMock
from cloud_harvester.collectors.powervs.instances import collect_instances
from cloud_harvester.collectors.powervs.workspaces import collect_workspaces


MOCK_WORKSPACES = [
    {
        "guid": "ws-abc-123",
        "name": "my-power-workspace",
        "zone": "dal12",
        "region": "us-south",
        "resourceGroupName": "default",
        "state": "active",
        "createdAt": "2025-01-10T08:00:00Z",
    }
]


def test_collect_instances():
    """Test collect_instances with mocked PowerVSClient and workspace discovery."""
    mock_client = MagicMock()
    mock_client.get.return_value = {
        "pvmInstances": [
            {
                "pvmInstanceID": "pvm-001",
                "serverName": "aix-prod-01",
                "status": "ACTIVE",
                "sysType": "s922",
                "processors": 4,
                "procType": "shared",
                "memory": 32,
                "osType": "aix",
                "networks": [{"ipAddress": "192.168.1.10"}],
                "storageType": "tier1",
                "creationDate": "2025-02-01T12:00:00Z",
            }
        ]
    }

    with patch(
        "cloud_harvester.collectors.powervs.instances.discover_workspaces",
        return_value=MOCK_WORKSPACES,
    ), patch(
        "cloud_harvester.collectors.powervs.instances.PowerVSClient",
        return_value=mock_client,
    ):
        result = collect_instances("test-key", "test-token", [])

    assert len(result) == 1
    first = result[0]
    assert first["pvmInstanceID"] == "pvm-001"
    assert first["serverName"] == "aix-prod-01"
    assert first["status"] == "ACTIVE"
    assert first["sysType"] == "s922"
    assert first["processors"] == 4
    assert first["procType"] == "shared"
    assert first["memory"] == 32
    assert first["osType"] == "aix"
    assert first["primaryIp"] == "192.168.1.10"
    assert first["storageType"] == "tier1"
    assert first["workspace"] == "my-power-workspace"
    assert first["zone"] == "dal12"
    assert first["creationDate"] == "2025-02-01T12:00:00Z"


def test_collect_workspaces():
    """Test collect_workspaces with mocked resource controller API."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "resources": [
            {
                "guid": "ws-abc-123",
                "name": "my-power-workspace",
                "region_id": "dal12",
                "resource_group_id": "rg-001",
                "state": "active",
                "created_at": "2025-01-10T08:00:00Z",
            }
        ],
        "next_url": None,
    }
    mock_response.raise_for_status = MagicMock()

    with patch(
        "cloud_harvester.collectors.powervs.workspaces.requests.get",
        return_value=mock_response,
    ):
        result = collect_workspaces("test-key", "test-token", [])

    assert len(result) == 1
    first = result[0]
    assert first["guid"] == "ws-abc-123"
    assert first["name"] == "my-power-workspace"
    assert first["zone"] == "dal12"
    assert first["region"] == "us-south"
    assert first["state"] == "active"
    assert first["createdAt"] == "2025-01-10T08:00:00Z"
