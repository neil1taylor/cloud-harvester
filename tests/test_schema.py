# tests/test_schema.py
from cloud_harvester.schema import CLASSIC_SCHEMAS, VPC_SCHEMAS, POWERVS_SCHEMAS, VMWARE_SCHEMAS


def test_classic_virtual_servers_schema():
    schema = CLASSIC_SCHEMAS["virtualServers"]
    assert schema.worksheet_name == "vVirtualServers"
    assert schema.domain == "classic"
    headers = [c.header for c in schema.columns]
    assert "ID" in headers
    assert "Hostname" in headers
    assert "Primary IP" in headers
    assert "Datacenter" in headers


def test_vpc_instances_schema():
    schema = VPC_SCHEMAS["vpcInstances"]
    assert schema.worksheet_name == "vVpcInstances"
    assert schema.domain == "vpc"
    headers = [c.header for c in schema.columns]
    assert "ID" in headers
    assert "Name" in headers
    assert "Profile" in headers


def test_powervs_instances_schema():
    schema = POWERVS_SCHEMAS["pvsInstances"]
    assert schema.worksheet_name == "pPvsInstances"
    assert schema.domain == "powervs"


def test_all_schemas_have_required_fields():
    all_schemas = {**CLASSIC_SCHEMAS, **VPC_SCHEMAS, **POWERVS_SCHEMAS, **VMWARE_SCHEMAS}
    for key, schema in all_schemas.items():
        assert schema.worksheet_name, f"{key} missing worksheet_name"
        assert schema.domain, f"{key} missing domain"
        assert len(schema.columns) > 0, f"{key} has no columns"
        for col in schema.columns:
            assert col.header, f"{key} column missing header"
            assert col.field, f"{key} column missing field"
            assert col.data_type in ("string", "number", "boolean", "date", "currency", "array", "bytes"), \
                f"{key} column {col.field} has invalid data_type: {col.data_type}"
