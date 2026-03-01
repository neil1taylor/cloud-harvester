"""Tests for VPC infrastructure collectors."""
from unittest.mock import patch, MagicMock
from cloud_harvester.collectors.vpc.instances import collect_vpc_instances
from cloud_harvester.collectors.vpc.vpcs import collect_vpcs


def test_collect_vpc_instances():
    """Test collect_vpc_instances with mocked VpcClient."""
    mock_client = MagicMock()
    mock_client.list_resources.return_value = [
        {
            "id": "0717-abc123",
            "name": "web-server-01",
            "status": "running",
            "profile": {"name": "bx2-4x16"},
            "vcpu": {"count": 4},
            "memory": 16,
            "zone": {"name": "us-south-1"},
            "vpc": {"name": "my-vpc"},
            "primary_network_interface": {
                "primary_ip": {"address": "10.240.0.5"},
            },
            "created_at": "2025-01-15T10:30:00Z",
            "resource_group": {"name": "default"},
        }
    ]

    with patch(
        "cloud_harvester.collectors.vpc.instances.VpcClient",
        return_value=mock_client,
    ):
        result = collect_vpc_instances("test-key", "test-token", [])

    assert len(result) > 0
    first = result[0]
    assert first["id"] == "0717-abc123"
    assert first["name"] == "web-server-01"
    assert first["status"] == "running"
    assert first["profile"] == "bx2-4x16"
    assert first["vcpu"] == 4
    assert first["memory"] == 16
    assert first["zone"] == "us-south-1"
    assert first["vpcName"] == "my-vpc"
    assert first["primaryIp"] == "10.240.0.5"
    assert first["region"] == "us-south"
    assert first["created_at"] == "2025-01-15T10:30:00Z"
    assert first["resourceGroup"] == "default"


def test_collect_vpcs():
    """Test collect_vpcs with mocked VpcClient."""
    mock_client = MagicMock()
    mock_client.list_resources.return_value = [
        {
            "id": "r006-def456",
            "name": "prod-vpc",
            "status": "available",
            "classic_access": True,
            "created_at": "2024-12-01T08:00:00Z",
            "resource_group": {"name": "production"},
        }
    ]

    with patch(
        "cloud_harvester.collectors.vpc.vpcs.VpcClient",
        return_value=mock_client,
    ):
        result = collect_vpcs("test-key", "test-token", ["us-south"])

    assert len(result) > 0
    first = result[0]
    assert first["id"] == "r006-def456"
    assert first["name"] == "prod-vpc"
    assert first["status"] == "available"
    assert first["classicAccess"] is True
    assert first["region"] == "us-south"
    assert first["created_at"] == "2024-12-01T08:00:00Z"
    assert first["resourceGroup"] == "production"
