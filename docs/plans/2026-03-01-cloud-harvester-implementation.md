# cloud-harvester Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build a Python CLI tool that collects IBM Cloud infrastructure data (Classic, VPC, PowerVS, VMware) and produces XLSX files compatible with the classic_analyser app.

**Architecture:** Plugin-based collectors with a standard interface. Each resource type is a separate module. Collection runs in parallel within each domain. Results are cached for resume support. Output is XLSX with exact schema matching classic_analyser.

**Tech Stack:** Python 3.11+, click, softlayer, ibm-cloud-sdk-core, ibm-vpc, ibm-platform-services, openpyxl, rich

---

## Phase 1: Project Scaffolding

### Task 1: Initialize Python project with pyproject.toml

**Files:**
- Create: `pyproject.toml`
- Create: `src/cloud_harvester/__init__.py`
- Create: `tests/__init__.py`

**Step 1: Create pyproject.toml**

```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "cloud-harvester"
version = "0.1.0"
description = "Collect IBM Cloud infrastructure data into XLSX for classic_analyser"
requires-python = ">=3.11"
dependencies = [
    "click>=8.1",
    "softlayer>=6.1",
    "ibm-cloud-sdk-core>=3.16",
    "ibm-vpc>=0.20",
    "ibm-platform-services>=0.50",
    "openpyxl>=3.1",
    "rich>=13.0",
    "requests>=2.31",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.4",
    "pytest-cov>=4.1",
    "ruff>=0.1",
]

[project.scripts]
cloud-harvester = "cloud_harvester.cli:main"

[tool.pytest.ini_options]
testpaths = ["tests"]

[tool.ruff]
target-version = "py311"
line-length = 120
```

**Step 2: Create package init**

```python
# src/cloud_harvester/__init__.py
__version__ = "0.1.0"
```

**Step 3: Create tests init**

```python
# tests/__init__.py
```

**Step 4: Install in dev mode**

Run: `cd <project-root> && python3 -m venv .venv && source .venv/bin/activate && pip install -e ".[dev]"`

**Step 5: Verify installation**

Run: `source .venv/bin/activate && python -c "import cloud_harvester; print(cloud_harvester.__version__)"`
Expected: `0.1.0`

**Step 6: Create .gitignore**

```
.venv/
__pycache__/
*.pyc
*.egg-info/
dist/
build/
.cloud-harvester-cache/
*.xlsx
.ruff_cache/
```

**Step 7: Commit**

```bash
git add pyproject.toml src/ tests/ .gitignore
git commit -m "feat: initialize cloud-harvester Python project"
```

---

## Phase 2: Core Infrastructure

### Task 2: Authentication module

**Files:**
- Create: `src/cloud_harvester/auth.py`
- Create: `tests/test_auth.py`

**Step 1: Write the failing test**

```python
# tests/test_auth.py
from unittest.mock import patch, MagicMock
from cloud_harvester.auth import authenticate, discover_accounts


def test_authenticate_returns_token():
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "access_token": "test-token",
        "token_type": "Bearer",
        "expires_in": 3600,
    }

    with patch("cloud_harvester.auth.requests.post", return_value=mock_response):
        token = authenticate("test-api-key")
        assert token == "test-token"


def test_authenticate_raises_on_invalid_key():
    mock_response = MagicMock()
    mock_response.status_code = 400
    mock_response.raise_for_status.side_effect = Exception("Bad Request")

    with patch("cloud_harvester.auth.requests.post", return_value=mock_response):
        try:
            authenticate("bad-key")
            assert False, "Should have raised"
        except Exception:
            pass
```

**Step 2: Run test to verify it fails**

Run: `source .venv/bin/activate && pytest tests/test_auth.py -v`
Expected: FAIL (module not found)

**Step 3: Write implementation**

```python
# src/cloud_harvester/auth.py
import requests

IAM_TOKEN_URL = "https://iam.cloud.ibm.com/identity/token"


def authenticate(api_key: str) -> str:
    """Exchange IBM Cloud API key for IAM bearer token."""
    response = requests.post(
        IAM_TOKEN_URL,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        data={
            "grant_type": "urn:ibm:params:oauth:grant-type:apikey",
            "apikey": api_key,
        },
        timeout=30,
    )
    response.raise_for_status()
    return response.json()["access_token"]


def discover_accounts(api_key: str) -> list[dict]:
    """Discover all accounts accessible with this API key."""
    token = authenticate(api_key)
    response = requests.get(
        "https://accounts.cloud.ibm.com/v1/accounts",
        headers={"Authorization": f"Bearer {token}"},
        timeout=30,
    )
    response.raise_for_status()
    data = response.json()
    return data.get("resources", [])


def get_account_info(api_key: str) -> dict:
    """Get account info for the API key's owning account."""
    from ibm_platform_services import IamIdentityV1
    from ibm_cloud_sdk_core.authenticators import IAMAuthenticator

    authenticator = IAMAuthenticator(api_key)
    iam_identity = IamIdentityV1(authenticator=authenticator)
    api_key_details = iam_identity.get_api_keys_details(iam_api_key=api_key).get_result()
    account_id = api_key_details.get("account_id")

    token = authenticate(api_key)
    response = requests.get(
        f"https://accounts.cloud.ibm.com/v1/accounts/{account_id}",
        headers={"Authorization": f"Bearer {token}"},
        timeout=30,
    )
    response.raise_for_status()
    return response.json()
```

**Step 4: Run test to verify it passes**

Run: `source .venv/bin/activate && pytest tests/test_auth.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add src/cloud_harvester/auth.py tests/test_auth.py
git commit -m "feat: add IAM authentication and account discovery"
```

---

### Task 3: Schema definitions module

**Files:**
- Create: `src/cloud_harvester/schema.py`
- Create: `tests/test_schema.py`

This is the single source of truth for XLSX compatibility with classic_analyser. Column definitions must exactly match.

**Step 1: Write the failing test**

```python
# tests/test_schema.py
from cloud_harvester.schema import CLASSIC_SCHEMAS, VPC_SCHEMAS, POWERVS_SCHEMAS, VMWARE_SCHEMAS, ColumnDef


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
```

**Step 2: Run test to verify it fails**

Run: `source .venv/bin/activate && pytest tests/test_schema.py -v`
Expected: FAIL (module not found)

**Step 3: Write implementation**

```python
# src/cloud_harvester/schema.py
"""Column definitions matching classic_analyser's XLSX format exactly."""
from dataclasses import dataclass, field


@dataclass
class ColumnDef:
    header: str
    field: str
    data_type: str = "string"  # string, number, boolean, date, currency, array, bytes


@dataclass
class ResourceSchema:
    worksheet_name: str
    domain: str
    resource_type: str
    columns: list[ColumnDef] = field(default_factory=list)


# ──────────────────────────────────────────────
# CLASSIC INFRASTRUCTURE SCHEMAS (~25 types)
# ──────────────────────────────────────────────

CLASSIC_SCHEMAS: dict[str, ResourceSchema] = {
    "virtualServers": ResourceSchema(
        worksheet_name="vVirtualServers",
        domain="classic",
        resource_type="virtualServers",
        columns=[
            ColumnDef("ID", "id", "number"),
            ColumnDef("Hostname", "hostname"),
            ColumnDef("Domain", "domain"),
            ColumnDef("FQDN", "fqdn"),
            ColumnDef("Primary IP", "primaryIp"),
            ColumnDef("Backend IP", "backendIp"),
            ColumnDef("CPU", "maxCpu", "number"),
            ColumnDef("Memory (MB)", "maxMemory", "number"),
            ColumnDef("Status", "status"),
            ColumnDef("Power State", "powerState"),
            ColumnDef("Datacenter", "datacenter"),
            ColumnDef("OS", "os"),
            ColumnDef("Hourly Billing", "hourlyBilling"),
            ColumnDef("Create Date", "createDate", "date"),
            ColumnDef("Classic Monthly Fee", "recurringFee", "currency"),
            ColumnDef("Cost Basis", "costBasis"),
            ColumnDef("Notes", "notes"),
            ColumnDef("Private Only", "privateNetworkOnly"),
            ColumnDef("Local Disk", "localDisk"),
            ColumnDef("Start CPUs", "startCpus", "number"),
            ColumnDef("Modified", "modifyDate", "date"),
            ColumnDef("Dedicated", "dedicated"),
            ColumnDef("Placement Group", "placementGroupId", "number"),
            ColumnDef("Tags", "tags"),
            ColumnDef("Disk (GB)", "diskGb", "number"),
            ColumnDef("VLANs", "networkVlans"),
        ],
    ),
    "bareMetal": ResourceSchema(
        worksheet_name="vBareMetal",
        domain="classic",
        resource_type="bareMetal",
        columns=[
            ColumnDef("ID", "id", "number"),
            ColumnDef("Hostname", "hostname"),
            ColumnDef("Domain", "domain"),
            ColumnDef("FQDN", "fqdn"),
            ColumnDef("Serial Number", "serialNumber"),
            ColumnDef("Primary IP", "primaryIp"),
            ColumnDef("Backend IP", "backendIp"),
            ColumnDef("Cores", "cores", "number"),
            ColumnDef("Memory (GB)", "memory", "number"),
            ColumnDef("Datacenter", "datacenter"),
            ColumnDef("OS", "os"),
            ColumnDef("Classic Monthly Fee", "recurringFee", "currency"),
            ColumnDef("Provision Date", "provisionDate", "date"),
            ColumnDef("Power Supplies", "powerSupplyCount", "number"),
            ColumnDef("Gateway Member", "gatewayMember"),
            ColumnDef("VMware Role", "vmwareRole"),
            ColumnDef("Notes", "notes"),
            ColumnDef("Hard Drives", "hardDrives"),
            ColumnDef("Network Components", "networkComponents"),
            ColumnDef("VLANs", "networkVlans"),
            ColumnDef("Tags", "tags"),
        ],
    ),
    "vlans": ResourceSchema(
        worksheet_name="vVLANs",
        domain="classic",
        resource_type="vlans",
        columns=[
            ColumnDef("ID", "id", "number"),
            ColumnDef("VLAN Number", "vlanNumber", "number"),
            ColumnDef("Name", "name"),
            ColumnDef("Network Space", "networkSpace"),
            ColumnDef("Primary Router", "primaryRouter"),
            ColumnDef("Datacenter", "datacenter"),
            ColumnDef("Subnet Count", "subnetCount", "number"),
            ColumnDef("Firewall Components", "firewallComponents", "number"),
            ColumnDef("Gateway", "gateway"),
        ],
    ),
    "subnets": ResourceSchema(
        worksheet_name="vSubnets",
        domain="classic",
        resource_type="subnets",
        columns=[
            ColumnDef("ID", "id", "number"),
            ColumnDef("Network", "networkIdentifier"),
            ColumnDef("CIDR", "cidr", "number"),
            ColumnDef("Type", "subnetType"),
            ColumnDef("Gateway", "gateway"),
            ColumnDef("Broadcast", "broadcastAddress"),
            ColumnDef("Usable IPs", "usableIpAddressCount", "number"),
            ColumnDef("Total IPs", "totalIpAddresses", "number"),
            ColumnDef("VLAN", "vlanNumber", "number"),
            ColumnDef("Datacenter", "datacenter"),
        ],
    ),
    "gateways": ResourceSchema(
        worksheet_name="vGateways",
        domain="classic",
        resource_type="gateways",
        columns=[
            ColumnDef("ID", "id", "number"),
            ColumnDef("Name", "name"),
            ColumnDef("Network Space", "networkSpace"),
            ColumnDef("Status", "status"),
            ColumnDef("Public IP", "publicIp"),
            ColumnDef("Private IP", "privateIp"),
            ColumnDef("Members", "memberCount", "number"),
            ColumnDef("Inside VLANs", "insideVlanCount", "number"),
        ],
    ),
    "firewalls": ResourceSchema(
        worksheet_name="vFirewalls",
        domain="classic",
        resource_type="firewalls",
        columns=[
            ColumnDef("ID", "id", "number"),
            ColumnDef("Primary IP", "primaryIpAddress"),
            ColumnDef("Type", "firewallType"),
            ColumnDef("VLAN", "vlanNumber", "number"),
            ColumnDef("Datacenter", "datacenter"),
            ColumnDef("Classic Monthly Fee", "recurringFee", "currency"),
            ColumnDef("Rules", "ruleCount", "number"),
        ],
    ),
    "securityGroups": ResourceSchema(
        worksheet_name="vSecurityGroups",
        domain="classic",
        resource_type="securityGroups",
        columns=[
            ColumnDef("ID", "id", "number"),
            ColumnDef("Name", "name"),
            ColumnDef("Description", "description"),
            ColumnDef("Created", "createDate", "date"),
            ColumnDef("Modified", "modifyDate", "date"),
            ColumnDef("Rules", "ruleCount", "number"),
            ColumnDef("Bindings", "bindingCount", "number"),
        ],
    ),
    "securityGroupRules": ResourceSchema(
        worksheet_name="vSecurityGroupRules",
        domain="classic",
        resource_type="securityGroupRules",
        columns=[
            ColumnDef("Security Group ID", "securityGroupId", "number"),
            ColumnDef("Security Group Name", "securityGroupName"),
            ColumnDef("Rule ID", "id", "number"),
            ColumnDef("Direction", "direction"),
            ColumnDef("Protocol", "protocol"),
            ColumnDef("Port Min", "portRangeMin", "number"),
            ColumnDef("Port Max", "portRangeMax", "number"),
            ColumnDef("Remote IP", "remoteIp"),
            ColumnDef("Remote Group ID", "remoteGroupId", "number"),
        ],
    ),
    "loadBalancers": ResourceSchema(
        worksheet_name="vLoadBalancers",
        domain="classic",
        resource_type="loadBalancers",
        columns=[
            ColumnDef("ID", "id", "number"),
            ColumnDef("Name", "name"),
            ColumnDef("IP Address", "ipAddress"),
            ColumnDef("Type", "loadBalancerType"),
            ColumnDef("Connection Limit", "connectionLimit", "number"),
            ColumnDef("Classic Monthly Fee", "recurringFee", "currency"),
            ColumnDef("Virtual Servers", "virtualServers"),
        ],
    ),
    "blockStorage": ResourceSchema(
        worksheet_name="vBlockStorage",
        domain="classic",
        resource_type="blockStorage",
        columns=[
            ColumnDef("ID", "id", "number"),
            ColumnDef("Username", "username"),
            ColumnDef("Capacity (GB)", "capacityGb", "number"),
            ColumnDef("IOPS", "iops"),
            ColumnDef("Storage Type", "storageType"),
            ColumnDef("Tier", "storageTierLevel"),
            ColumnDef("Target IP", "targetIp"),
            ColumnDef("LUN ID", "lunId"),
            ColumnDef("Snapshot (GB)", "snapshotCapacityGb", "number"),
            ColumnDef("Classic Monthly Fee", "recurringFee", "currency"),
            ColumnDef("Create Date", "createDate", "date"),
            ColumnDef("Notes", "notes"),
            ColumnDef("Allowed VSIs", "allowedVirtualGuests"),
            ColumnDef("Allowed Hardware", "allowedHardware"),
            ColumnDef("Replication Partners", "replicationPartners"),
        ],
    ),
    "fileStorage": ResourceSchema(
        worksheet_name="vFileStorage",
        domain="classic",
        resource_type="fileStorage",
        columns=[
            ColumnDef("ID", "id", "number"),
            ColumnDef("Username", "username"),
            ColumnDef("Capacity (GB)", "capacityGb", "number"),
            ColumnDef("IOPS", "iops"),
            ColumnDef("Storage Type", "storageType"),
            ColumnDef("Tier", "storageTierLevel"),
            ColumnDef("Target IP", "targetIp"),
            ColumnDef("Mount Address", "mountAddress"),
            ColumnDef("Snapshot (GB)", "snapshotCapacityGb", "number"),
            ColumnDef("Classic Monthly Fee", "recurringFee", "currency"),
            ColumnDef("Create Date", "createDate", "date"),
            ColumnDef("Notes", "notes"),
            ColumnDef("Allowed VSIs", "allowedVirtualGuests"),
            ColumnDef("Allowed Hardware", "allowedHardware"),
            ColumnDef("Replication Partners", "replicationPartners"),
        ],
    ),
    "objectStorage": ResourceSchema(
        worksheet_name="vObjectStorage",
        domain="classic",
        resource_type="objectStorage",
        columns=[
            ColumnDef("ID", "id", "number"),
            ColumnDef("Username", "username"),
            ColumnDef("Storage Type", "storageType"),
            ColumnDef("Capacity (GB)", "capacityGb", "number"),
            ColumnDef("Bytes Used", "bytesUsed", "number"),
            ColumnDef("Classic Monthly Fee", "recurringFee", "currency"),
            ColumnDef("Create Date", "createDate", "date"),
        ],
    ),
    "sslCertificates": ResourceSchema(
        worksheet_name="vSSLCertificates",
        domain="classic",
        resource_type="sslCertificates",
        columns=[
            ColumnDef("ID", "id", "number"),
            ColumnDef("Common Name", "commonName"),
            ColumnDef("Organization", "organizationName"),
            ColumnDef("Valid From", "validityBegin", "date"),
            ColumnDef("Validity (Days)", "validityDays", "number"),
            ColumnDef("Valid Until", "validityEnd", "date"),
            ColumnDef("Create Date", "createDate", "date"),
            ColumnDef("Notes", "notes"),
        ],
    ),
    "sshKeys": ResourceSchema(
        worksheet_name="vSSHKeys",
        domain="classic",
        resource_type="sshKeys",
        columns=[
            ColumnDef("ID", "id", "number"),
            ColumnDef("Label", "label"),
            ColumnDef("Fingerprint", "fingerprint"),
            ColumnDef("Create Date", "createDate", "date"),
            ColumnDef("Modify Date", "modifyDate", "date"),
            ColumnDef("Notes", "notes"),
        ],
    ),
    "dnsDomains": ResourceSchema(
        worksheet_name="vDNSDomains",
        domain="classic",
        resource_type="dnsDomains",
        columns=[
            ColumnDef("ID", "id", "number"),
            ColumnDef("Name", "name"),
            ColumnDef("Serial", "serial", "number"),
            ColumnDef("Update Date", "updateDate", "date"),
            ColumnDef("Record Count", "recordCount", "number"),
        ],
    ),
    "dnsRecords": ResourceSchema(
        worksheet_name="vDNSRecords",
        domain="classic",
        resource_type="dnsRecords",
        columns=[
            ColumnDef("Domain ID", "domainId", "number"),
            ColumnDef("Domain", "domainName"),
            ColumnDef("ID", "id", "number"),
            ColumnDef("Host", "host"),
            ColumnDef("Type", "type"),
            ColumnDef("Data", "data"),
            ColumnDef("TTL", "ttl", "number"),
            ColumnDef("Priority", "priority", "number"),
        ],
    ),
    "images": ResourceSchema(
        worksheet_name="vImages",
        domain="classic",
        resource_type="images",
        columns=[
            ColumnDef("ID", "id", "number"),
            ColumnDef("Name", "name"),
            ColumnDef("Global ID", "globalIdentifier"),
            ColumnDef("Note", "note"),
            ColumnDef("Created", "createDate", "date"),
            ColumnDef("Status", "status"),
            ColumnDef("Datacenter", "datacenter"),
            ColumnDef("Parent ID", "parentId", "number"),
        ],
    ),
    "dedicatedHosts": ResourceSchema(
        worksheet_name="vDedicatedHosts",
        domain="classic",
        resource_type="dedicatedHosts",
        columns=[
            ColumnDef("ID", "id", "number"),
            ColumnDef("Name", "name"),
            ColumnDef("Created", "createDate", "date"),
            ColumnDef("Datacenter", "datacenter"),
            ColumnDef("CPU Count", "cpuCount", "number"),
            ColumnDef("Memory (GB)", "memoryCapacity", "number"),
            ColumnDef("Disk (GB)", "diskCapacity", "number"),
            ColumnDef("Guest Count", "guestCount", "number"),
        ],
    ),
    "placementGroups": ResourceSchema(
        worksheet_name="vPlacementGroups",
        domain="classic",
        resource_type="placementGroups",
        columns=[
            ColumnDef("ID", "id", "number"),
            ColumnDef("Name", "name"),
            ColumnDef("Created", "createDate", "date"),
            ColumnDef("Rule", "rule"),
            ColumnDef("Backend Router", "backendRouter"),
            ColumnDef("Guest Count", "guestCount", "number"),
        ],
    ),
    "reservedCapacity": ResourceSchema(
        worksheet_name="vReservedCapacity",
        domain="classic",
        resource_type="reservedCapacity",
        columns=[
            ColumnDef("ID", "id", "number"),
            ColumnDef("Name", "name"),
            ColumnDef("Created", "createDate", "date"),
            ColumnDef("Backend Router", "backendRouter"),
            ColumnDef("Instances", "instanceCount", "number"),
        ],
    ),
    "vpnTunnels": ResourceSchema(
        worksheet_name="vVPNTunnels",
        domain="classic",
        resource_type="vpnTunnels",
        columns=[
            ColumnDef("ID", "id", "number"),
            ColumnDef("Name", "name"),
            ColumnDef("Customer Peer IP", "customerPeerIpAddress"),
            ColumnDef("Internal Peer IP", "internalPeerIpAddress"),
            ColumnDef("P1 Auth", "phaseOneAuthentication"),
            ColumnDef("P1 Encryption", "phaseOneEncryption"),
            ColumnDef("P2 Auth", "phaseTwoAuthentication"),
            ColumnDef("P2 Encryption", "phaseTwoEncryption"),
            ColumnDef("Address Translations", "addressTranslations"),
            ColumnDef("Customer Subnets", "customerSubnets"),
            ColumnDef("Internal Subnets", "internalSubnets"),
        ],
    ),
    "billing": ResourceSchema(
        worksheet_name="vBilling",
        domain="classic",
        resource_type="billing",
        columns=[
            ColumnDef("ID", "id", "number"),
            ColumnDef("Description", "description"),
            ColumnDef("Category", "categoryCode"),
            ColumnDef("Classic Monthly Fee", "recurringFee", "currency"),
            ColumnDef("Create Date", "createDate", "date"),
            ColumnDef("Cancel Date", "cancellationDate", "date"),
            ColumnDef("Notes", "notes"),
        ],
    ),
    "users": ResourceSchema(
        worksheet_name="vUsers",
        domain="classic",
        resource_type="users",
        columns=[
            ColumnDef("ID", "id", "number"),
            ColumnDef("Username", "username"),
            ColumnDef("Email", "email"),
            ColumnDef("First Name", "firstName"),
            ColumnDef("Last Name", "lastName"),
            ColumnDef("Create Date", "createDate", "date"),
            ColumnDef("Status Date", "statusDate", "date"),
            ColumnDef("Status", "userStatus"),
            ColumnDef("Roles", "roles"),
            ColumnDef("Permissions", "permissions"),
        ],
    ),
    "eventLog": ResourceSchema(
        worksheet_name="vEventLog",
        domain="classic",
        resource_type="eventLog",
        columns=[
            ColumnDef("Event", "eventName"),
            ColumnDef("Date", "eventCreateDate", "date"),
            ColumnDef("User Type", "userType"),
            ColumnDef("User ID", "userId", "number"),
            ColumnDef("Username", "username"),
            ColumnDef("Object", "objectName"),
            ColumnDef("Object ID", "objectId", "number"),
            ColumnDef("Trace ID", "traceId"),
        ],
    ),
    "relationships": ResourceSchema(
        worksheet_name="vRelationships",
        domain="classic",
        resource_type="relationships",
        columns=[
            ColumnDef("Parent Type", "parentType"),
            ColumnDef("Parent ID", "parentId", "number"),
            ColumnDef("Parent Name", "parentName"),
            ColumnDef("Child Type", "childType"),
            ColumnDef("Child ID", "childId", "number"),
            ColumnDef("Child Name", "childName"),
            ColumnDef("Relationship Field", "relationshipField"),
        ],
    ),
}


# ──────────────────────────────────────────────
# VPC INFRASTRUCTURE SCHEMAS (~26 types)
# ──────────────────────────────────────────────

VPC_SCHEMAS: dict[str, ResourceSchema] = {
    "vpcInstances": ResourceSchema(
        worksheet_name="vVpcInstances",
        domain="vpc",
        resource_type="vpcInstances",
        columns=[
            ColumnDef("ID", "id"),
            ColumnDef("Name", "name"),
            ColumnDef("Status", "status"),
            ColumnDef("Profile", "profile"),
            ColumnDef("vCPUs", "vcpu", "number"),
            ColumnDef("Memory (GB)", "memory", "number"),
            ColumnDef("Zone", "zone"),
            ColumnDef("VPC", "vpcName"),
            ColumnDef("Primary IP", "primaryIp"),
            ColumnDef("Region", "region"),
            ColumnDef("Created", "created_at", "date"),
            ColumnDef("Resource Group", "resourceGroup"),
        ],
    ),
    "vpcBareMetalServers": ResourceSchema(
        worksheet_name="vVpcBareMetal",
        domain="vpc",
        resource_type="vpcBareMetalServers",
        columns=[
            ColumnDef("ID", "id"),
            ColumnDef("Name", "name"),
            ColumnDef("Status", "status"),
            ColumnDef("Profile", "profile"),
            ColumnDef("Zone", "zone"),
            ColumnDef("VPC", "vpcName"),
            ColumnDef("Region", "region"),
            ColumnDef("Created", "created_at", "date"),
            ColumnDef("Resource Group", "resourceGroup"),
        ],
    ),
    "vpcDedicatedHosts": ResourceSchema(
        worksheet_name="vVpcDedicatedHosts",
        domain="vpc",
        resource_type="vpcDedicatedHosts",
        columns=[
            ColumnDef("ID", "id"),
            ColumnDef("Name", "name"),
            ColumnDef("State", "state"),
            ColumnDef("Profile", "profile"),
            ColumnDef("Zone", "zone"),
            ColumnDef("vCPUs", "vcpu", "number"),
            ColumnDef("Memory (GB)", "memory", "number"),
            ColumnDef("Instances", "instanceCount", "number"),
            ColumnDef("Region", "region"),
            ColumnDef("Created", "created_at", "date"),
        ],
    ),
    "vpcPlacementGroups": ResourceSchema(
        worksheet_name="vVpcPlacementGroups",
        domain="vpc",
        resource_type="vpcPlacementGroups",
        columns=[
            ColumnDef("ID", "id"),
            ColumnDef("Name", "name"),
            ColumnDef("Strategy", "strategy"),
            ColumnDef("Region", "region"),
            ColumnDef("Created", "created_at", "date"),
            ColumnDef("Resource Group", "resourceGroup"),
        ],
    ),
    "vpcs": ResourceSchema(
        worksheet_name="vVpcs",
        domain="vpc",
        resource_type="vpcs",
        columns=[
            ColumnDef("ID", "id"),
            ColumnDef("Name", "name"),
            ColumnDef("Status", "status"),
            ColumnDef("Classic Access", "classicAccess", "boolean"),
            ColumnDef("Region", "region"),
            ColumnDef("Created", "created_at", "date"),
            ColumnDef("Resource Group", "resourceGroup"),
        ],
    ),
    "vpcSubnets": ResourceSchema(
        worksheet_name="vVpcSubnets",
        domain="vpc",
        resource_type="vpcSubnets",
        columns=[
            ColumnDef("ID", "id"),
            ColumnDef("Name", "name"),
            ColumnDef("Status", "status"),
            ColumnDef("CIDR", "cidr"),
            ColumnDef("Available IPs", "availableIps", "number"),
            ColumnDef("Total IPs", "totalIps", "number"),
            ColumnDef("Zone", "zone"),
            ColumnDef("VPC", "vpcName"),
            ColumnDef("Region", "region"),
            ColumnDef("Created", "created_at", "date"),
        ],
    ),
    "vpcSecurityGroups": ResourceSchema(
        worksheet_name="vVpcSecurityGroups",
        domain="vpc",
        resource_type="vpcSecurityGroups",
        columns=[
            ColumnDef("ID", "id"),
            ColumnDef("Name", "name"),
            ColumnDef("VPC", "vpcName"),
            ColumnDef("Rules", "ruleCount", "number"),
            ColumnDef("Targets", "targetCount", "number"),
            ColumnDef("Region", "region"),
            ColumnDef("Created", "created_at", "date"),
        ],
    ),
    "vpcFloatingIps": ResourceSchema(
        worksheet_name="vVpcFloatingIps",
        domain="vpc",
        resource_type="vpcFloatingIps",
        columns=[
            ColumnDef("ID", "id"),
            ColumnDef("Name", "name"),
            ColumnDef("Address", "address"),
            ColumnDef("Status", "status"),
            ColumnDef("Target", "target"),
            ColumnDef("Zone", "zone"),
            ColumnDef("Region", "region"),
            ColumnDef("Created", "created_at", "date"),
        ],
    ),
    "vpcPublicGateways": ResourceSchema(
        worksheet_name="vVpcPublicGateways",
        domain="vpc",
        resource_type="vpcPublicGateways",
        columns=[
            ColumnDef("ID", "id"),
            ColumnDef("Name", "name"),
            ColumnDef("Status", "status"),
            ColumnDef("VPC", "vpcName"),
            ColumnDef("Floating IP", "floatingIp"),
            ColumnDef("Zone", "zone"),
            ColumnDef("Region", "region"),
            ColumnDef("Created", "created_at", "date"),
        ],
    ),
    "vpcNetworkAcls": ResourceSchema(
        worksheet_name="vVpcNetworkAcls",
        domain="vpc",
        resource_type="vpcNetworkAcls",
        columns=[
            ColumnDef("ID", "id"),
            ColumnDef("Name", "name"),
            ColumnDef("VPC", "vpcName"),
            ColumnDef("Rules", "ruleCount", "number"),
            ColumnDef("Subnets", "subnetCount", "number"),
            ColumnDef("Region", "region"),
            ColumnDef("Created", "created_at", "date"),
        ],
    ),
    "vpcLoadBalancers": ResourceSchema(
        worksheet_name="vVpcLoadBalancers",
        domain="vpc",
        resource_type="vpcLoadBalancers",
        columns=[
            ColumnDef("ID", "id"),
            ColumnDef("Name", "name"),
            ColumnDef("Hostname", "hostname"),
            ColumnDef("Public", "isPublic", "boolean"),
            ColumnDef("Operating Status", "operatingStatus"),
            ColumnDef("Provisioning Status", "provisioningStatus"),
            ColumnDef("Region", "region"),
            ColumnDef("Created", "created_at", "date"),
        ],
    ),
    "vpcVpnGateways": ResourceSchema(
        worksheet_name="vVpcVpnGateways",
        domain="vpc",
        resource_type="vpcVpnGateways",
        columns=[
            ColumnDef("ID", "id"),
            ColumnDef("Name", "name"),
            ColumnDef("Status", "status"),
            ColumnDef("Mode", "mode"),
            ColumnDef("Subnet", "subnet"),
            ColumnDef("Region", "region"),
            ColumnDef("Created", "created_at", "date"),
        ],
    ),
    "transitGateways": ResourceSchema(
        worksheet_name="vTransitGateways",
        domain="vpc",
        resource_type="transitGateways",
        columns=[
            ColumnDef("ID", "id"),
            ColumnDef("Name", "name"),
            ColumnDef("Status", "status"),
            ColumnDef("Location", "location"),
            ColumnDef("Routing Scope", "routingScope"),
            ColumnDef("Resource Group", "resourceGroup"),
            ColumnDef("Created", "created_at", "date"),
        ],
    ),
    "transitGatewayConnections": ResourceSchema(
        worksheet_name="vTGConnections",
        domain="vpc",
        resource_type="transitGatewayConnections",
        columns=[
            ColumnDef("ID", "id"),
            ColumnDef("Name", "name"),
            ColumnDef("Status", "status"),
            ColumnDef("Network Type", "networkType"),
            ColumnDef("Transit Gateway", "transitGatewayName"),
            ColumnDef("Network ID", "networkId"),
            ColumnDef("Ownership", "ownershipType"),
            ColumnDef("Created", "created_at", "date"),
        ],
    ),
    "directLinkGateways": ResourceSchema(
        worksheet_name="vDirectLinkGateways",
        domain="vpc",
        resource_type="directLinkGateways",
        columns=[
            ColumnDef("ID", "id"),
            ColumnDef("Name", "name"),
            ColumnDef("Type", "type"),
            ColumnDef("Speed (Mbps)", "speedMbps", "number"),
            ColumnDef("Location", "locationName"),
            ColumnDef("BGP Status", "bgpStatus"),
            ColumnDef("Operational Status", "operationalStatus"),
            ColumnDef("Global", "global", "boolean"),
            ColumnDef("Resource Group", "resourceGroup"),
            ColumnDef("Created", "created_at", "date"),
        ],
    ),
    "directLinkVirtualConnections": ResourceSchema(
        worksheet_name="vDLVirtualConns",
        domain="vpc",
        resource_type="directLinkVirtualConnections",
        columns=[
            ColumnDef("ID", "id"),
            ColumnDef("Name", "name"),
            ColumnDef("Status", "status"),
            ColumnDef("Type", "type"),
            ColumnDef("Gateway", "gatewayName"),
            ColumnDef("Network ID", "networkId"),
            ColumnDef("Network Account", "networkAccountId"),
            ColumnDef("Created", "created_at", "date"),
        ],
    ),
    "vpnGatewayConnections": ResourceSchema(
        worksheet_name="vVpnGwConns",
        domain="vpc",
        resource_type="vpnGatewayConnections",
        columns=[
            ColumnDef("ID", "id"),
            ColumnDef("Name", "name"),
            ColumnDef("Status", "status"),
            ColumnDef("Mode", "mode"),
            ColumnDef("VPN Gateway", "vpnGatewayName"),
            ColumnDef("Peer Address", "peerAddress"),
            ColumnDef("Local CIDRs", "localCidrs"),
            ColumnDef("Peer CIDRs", "peerCidrs"),
            ColumnDef("Region", "region"),
            ColumnDef("Created", "created_at", "date"),
        ],
    ),
    "vpcEndpointGateways": ResourceSchema(
        worksheet_name="vVpcEndpointGateways",
        domain="vpc",
        resource_type="vpcEndpointGateways",
        columns=[
            ColumnDef("ID", "id"),
            ColumnDef("Name", "name"),
            ColumnDef("Lifecycle State", "lifecycleState"),
            ColumnDef("Health State", "healthState"),
            ColumnDef("Target", "target"),
            ColumnDef("VPC", "vpcName"),
            ColumnDef("Region", "region"),
            ColumnDef("Created", "created_at", "date"),
        ],
    ),
    "vpcRoutingTables": ResourceSchema(
        worksheet_name="vVpcRoutingTables",
        domain="vpc",
        resource_type="vpcRoutingTables",
        columns=[
            ColumnDef("ID", "id"),
            ColumnDef("Name", "name"),
            ColumnDef("VPC", "vpcName"),
            ColumnDef("Default", "isDefault", "boolean"),
            ColumnDef("Status", "lifecycleState"),
            ColumnDef("Routes", "routeCount", "number"),
            ColumnDef("Subnets", "subnets"),
            ColumnDef("Region", "region"),
            ColumnDef("Created", "created_at", "date"),
        ],
    ),
    "vpcRoutes": ResourceSchema(
        worksheet_name="vVpcRoutes",
        domain="vpc",
        resource_type="vpcRoutes",
        columns=[
            ColumnDef("ID", "id"),
            ColumnDef("Name", "name"),
            ColumnDef("Routing Table", "routingTableName"),
            ColumnDef("VPC", "vpcName"),
            ColumnDef("Destination CIDR", "destination"),
            ColumnDef("Action", "action"),
            ColumnDef("Next Hop Type", "nextHopType"),
            ColumnDef("Next Hop Target", "nextHopTarget"),
            ColumnDef("Zone", "zone"),
            ColumnDef("Priority", "priority", "number"),
            ColumnDef("Origin", "origin"),
            ColumnDef("Region", "region"),
            ColumnDef("Created", "created_at", "date"),
        ],
    ),
    "vpcVolumes": ResourceSchema(
        worksheet_name="vVpcVolumes",
        domain="vpc",
        resource_type="vpcVolumes",
        columns=[
            ColumnDef("ID", "id"),
            ColumnDef("Name", "name"),
            ColumnDef("Status", "status"),
            ColumnDef("Capacity (GB)", "capacity", "number"),
            ColumnDef("IOPS", "iops", "number"),
            ColumnDef("Profile", "profile"),
            ColumnDef("Encryption", "encryption"),
            ColumnDef("Zone", "zone"),
            ColumnDef("Region", "region"),
            ColumnDef("Created", "created_at", "date"),
        ],
    ),
    "vpcSshKeys": ResourceSchema(
        worksheet_name="vVpcSshKeys",
        domain="vpc",
        resource_type="vpcSshKeys",
        columns=[
            ColumnDef("ID", "id"),
            ColumnDef("Name", "name"),
            ColumnDef("Type", "type"),
            ColumnDef("Fingerprint", "fingerprint"),
            ColumnDef("Length", "length", "number"),
            ColumnDef("Region", "region"),
            ColumnDef("Created", "created_at", "date"),
        ],
    ),
    "vpcImages": ResourceSchema(
        worksheet_name="vVpcImages",
        domain="vpc",
        resource_type="vpcImages",
        columns=[
            ColumnDef("ID", "id"),
            ColumnDef("Name", "name"),
            ColumnDef("Status", "status"),
            ColumnDef("OS", "os"),
            ColumnDef("Architecture", "architecture"),
            ColumnDef("Region", "region"),
            ColumnDef("Created", "created_at", "date"),
        ],
    ),
    "vpcFlowLogCollectors": ResourceSchema(
        worksheet_name="vVpcFlowLogs",
        domain="vpc",
        resource_type="vpcFlowLogCollectors",
        columns=[
            ColumnDef("ID", "id"),
            ColumnDef("Name", "name"),
            ColumnDef("Active", "active", "boolean"),
            ColumnDef("Lifecycle State", "lifecycleState"),
            ColumnDef("Target", "target"),
            ColumnDef("Storage Bucket", "storageBucket"),
            ColumnDef("Region", "region"),
            ColumnDef("Created", "created_at", "date"),
        ],
    ),
}


# ──────────────────────────────────────────────
# POWERVS INFRASTRUCTURE SCHEMAS (~22 types)
# ──────────────────────────────────────────────

POWERVS_SCHEMAS: dict[str, ResourceSchema] = {
    "pvsInstances": ResourceSchema(
        worksheet_name="pPvsInstances",
        domain="powervs",
        resource_type="pvsInstances",
        columns=[
            ColumnDef("ID", "pvmInstanceID"),
            ColumnDef("Name", "serverName"),
            ColumnDef("Status", "status"),
            ColumnDef("System Type", "sysType"),
            ColumnDef("Processors", "processors", "number"),
            ColumnDef("Proc Type", "procType"),
            ColumnDef("Memory (GB)", "memory", "number"),
            ColumnDef("OS Type", "osType"),
            ColumnDef("Primary IP", "primaryIp"),
            ColumnDef("Storage Type", "storageType"),
            ColumnDef("Workspace", "workspace"),
            ColumnDef("Zone", "zone"),
            ColumnDef("Created", "creationDate", "date"),
        ],
    ),
    "pvsSharedProcessorPools": ResourceSchema(
        worksheet_name="pPvsSPPools",
        domain="powervs",
        resource_type="pvsSharedProcessorPools",
        columns=[
            ColumnDef("ID", "id"),
            ColumnDef("Name", "name"),
            ColumnDef("Host Group", "hostGroup"),
            ColumnDef("Reserved Cores", "reservedCores", "number"),
            ColumnDef("Allocated Cores", "allocatedCores", "number"),
            ColumnDef("Available Cores", "availableCores", "number"),
            ColumnDef("Instances", "instanceCount", "number"),
            ColumnDef("Workspace", "workspace"),
            ColumnDef("Zone", "zone"),
        ],
    ),
    "pvsPlacementGroups": ResourceSchema(
        worksheet_name="pPvsPlacementGrps",
        domain="powervs",
        resource_type="pvsPlacementGroups",
        columns=[
            ColumnDef("ID", "id"),
            ColumnDef("Name", "name"),
            ColumnDef("Policy", "policy"),
            ColumnDef("Members", "memberCount", "number"),
            ColumnDef("Workspace", "workspace"),
            ColumnDef("Zone", "zone"),
        ],
    ),
    "pvsHostGroups": ResourceSchema(
        worksheet_name="pPvsHostGroups",
        domain="powervs",
        resource_type="pvsHostGroups",
        columns=[
            ColumnDef("ID", "id"),
            ColumnDef("Name", "name"),
            ColumnDef("Hosts", "hostCount", "number"),
            ColumnDef("Secondaries", "secondaryCount", "number"),
            ColumnDef("Workspace", "workspace"),
            ColumnDef("Zone", "zone"),
        ],
    ),
    "pvsNetworks": ResourceSchema(
        worksheet_name="pPvsNetworks",
        domain="powervs",
        resource_type="pvsNetworks",
        columns=[
            ColumnDef("ID", "networkID"),
            ColumnDef("Name", "name"),
            ColumnDef("Type", "type"),
            ColumnDef("VLAN ID", "vlanID", "number"),
            ColumnDef("CIDR", "cidr"),
            ColumnDef("Gateway", "gateway"),
            ColumnDef("MTU", "mtu", "number"),
            ColumnDef("Workspace", "workspace"),
            ColumnDef("Zone", "zone"),
        ],
    ),
    "pvsNetworkPorts": ResourceSchema(
        worksheet_name="pPvsNetPorts",
        domain="powervs",
        resource_type="pvsNetworkPorts",
        columns=[
            ColumnDef("Port ID", "portID"),
            ColumnDef("IP Address", "ipAddress"),
            ColumnDef("MAC Address", "macAddress"),
            ColumnDef("Status", "status"),
            ColumnDef("Network", "networkName"),
            ColumnDef("Instance", "pvmInstanceName"),
            ColumnDef("Workspace", "workspace"),
            ColumnDef("Zone", "zone"),
        ],
    ),
    "pvsNetworkSecurityGroups": ResourceSchema(
        worksheet_name="pPvsNSGs",
        domain="powervs",
        resource_type="pvsNetworkSecurityGroups",
        columns=[
            ColumnDef("ID", "id"),
            ColumnDef("Name", "name"),
            ColumnDef("Rules", "ruleCount", "number"),
            ColumnDef("Members", "memberCount", "number"),
            ColumnDef("Workspace", "workspace"),
            ColumnDef("Zone", "zone"),
        ],
    ),
    "pvsCloudConnections": ResourceSchema(
        worksheet_name="pPvsCloudConns",
        domain="powervs",
        resource_type="pvsCloudConnections",
        columns=[
            ColumnDef("ID", "cloudConnectionID"),
            ColumnDef("Name", "name"),
            ColumnDef("Speed (Mbps)", "speed", "number"),
            ColumnDef("Global Routing", "globalRouting", "boolean"),
            ColumnDef("GRE Tunnel", "greEnabled", "boolean"),
            ColumnDef("Transit Enabled", "transitEnabled", "boolean"),
            ColumnDef("Networks", "networkCount", "number"),
            ColumnDef("Workspace", "workspace"),
            ColumnDef("Zone", "zone"),
        ],
    ),
    "pvsDhcpServers": ResourceSchema(
        worksheet_name="pPvsDhcp",
        domain="powervs",
        resource_type="pvsDhcpServers",
        columns=[
            ColumnDef("ID", "id"),
            ColumnDef("Status", "status"),
            ColumnDef("Network ID", "networkId"),
            ColumnDef("Network", "networkName"),
            ColumnDef("Workspace", "workspace"),
            ColumnDef("Zone", "zone"),
        ],
    ),
    "pvsVpnConnections": ResourceSchema(
        worksheet_name="pPvsVpnConns",
        domain="powervs",
        resource_type="pvsVpnConnections",
        columns=[
            ColumnDef("ID", "id"),
            ColumnDef("Name", "name"),
            ColumnDef("Status", "status"),
            ColumnDef("Mode", "mode"),
            ColumnDef("Peer Address", "peerAddress"),
            ColumnDef("Local Subnets", "localSubnets"),
            ColumnDef("Peer Subnets", "peerSubnets"),
            ColumnDef("Workspace", "workspace"),
            ColumnDef("Zone", "zone"),
        ],
    ),
    "pvsIkePolicies": ResourceSchema(
        worksheet_name="pPvsIkePolicies",
        domain="powervs",
        resource_type="pvsIkePolicies",
        columns=[
            ColumnDef("ID", "id"),
            ColumnDef("Name", "name"),
            ColumnDef("IKE Version", "version", "number"),
            ColumnDef("Encryption", "encryption"),
            ColumnDef("DH Group", "dhGroup", "number"),
            ColumnDef("Authentication", "authentication"),
            ColumnDef("Workspace", "workspace"),
            ColumnDef("Zone", "zone"),
        ],
    ),
    "pvsIpsecPolicies": ResourceSchema(
        worksheet_name="pPvsIpsecPolicies",
        domain="powervs",
        resource_type="pvsIpsecPolicies",
        columns=[
            ColumnDef("ID", "id"),
            ColumnDef("Name", "name"),
            ColumnDef("Encryption", "encryption"),
            ColumnDef("DH Group", "dhGroup", "number"),
            ColumnDef("Authentication", "authentication"),
            ColumnDef("PFS", "pfs", "boolean"),
            ColumnDef("Workspace", "workspace"),
            ColumnDef("Zone", "zone"),
        ],
    ),
    "pvsVolumes": ResourceSchema(
        worksheet_name="pPvsVolumes",
        domain="powervs",
        resource_type="pvsVolumes",
        columns=[
            ColumnDef("ID", "volumeID"),
            ColumnDef("Name", "name"),
            ColumnDef("State", "state"),
            ColumnDef("Size (GB)", "size", "number"),
            ColumnDef("Disk Type", "diskType"),
            ColumnDef("Bootable", "bootable", "boolean"),
            ColumnDef("Shareable", "shareable", "boolean"),
            ColumnDef("Attached To", "pvmInstanceName"),
            ColumnDef("Workspace", "workspace"),
            ColumnDef("Zone", "zone"),
            ColumnDef("Created", "creationDate", "date"),
        ],
    ),
    "pvsVolumeGroups": ResourceSchema(
        worksheet_name="pPvsVolGroups",
        domain="powervs",
        resource_type="pvsVolumeGroups",
        columns=[
            ColumnDef("ID", "id"),
            ColumnDef("Name", "name"),
            ColumnDef("Status", "status"),
            ColumnDef("Consistency Group", "consistencyGroupName"),
            ColumnDef("Volumes", "volumeCount", "number"),
            ColumnDef("Replication", "replicationEnabled", "boolean"),
            ColumnDef("Workspace", "workspace"),
            ColumnDef("Zone", "zone"),
        ],
    ),
    "pvsSnapshots": ResourceSchema(
        worksheet_name="pPvsSnapshots",
        domain="powervs",
        resource_type="pvsSnapshots",
        columns=[
            ColumnDef("ID", "snapshotID"),
            ColumnDef("Name", "name"),
            ColumnDef("Status", "status"),
            ColumnDef("% Complete", "percentComplete", "number"),
            ColumnDef("Instance", "pvmInstanceName"),
            ColumnDef("Volumes", "volumeCount", "number"),
            ColumnDef("Workspace", "workspace"),
            ColumnDef("Zone", "zone"),
            ColumnDef("Created", "creationDate", "date"),
        ],
    ),
    "pvsSshKeys": ResourceSchema(
        worksheet_name="pPvsSshKeys",
        domain="powervs",
        resource_type="pvsSshKeys",
        columns=[
            ColumnDef("Name", "name"),
            ColumnDef("Key (truncated)", "sshKey"),
            ColumnDef("Created", "creationDate", "date"),
            ColumnDef("Workspace", "workspace"),
            ColumnDef("Zone", "zone"),
        ],
    ),
    "pvsWorkspaces": ResourceSchema(
        worksheet_name="pPvsWorkspaces",
        domain="powervs",
        resource_type="pvsWorkspaces",
        columns=[
            ColumnDef("GUID", "guid"),
            ColumnDef("Name", "name"),
            ColumnDef("Zone", "zone"),
            ColumnDef("Region", "region"),
            ColumnDef("Resource Group", "resourceGroupName"),
            ColumnDef("State", "state"),
            ColumnDef("Created", "createdAt", "date"),
        ],
    ),
    "pvsSystemPools": ResourceSchema(
        worksheet_name="pPvsSystemPools",
        domain="powervs",
        resource_type="pvsSystemPools",
        columns=[
            ColumnDef("System Type", "type"),
            ColumnDef("Shared Core Ratio", "sharedCoreRatio"),
            ColumnDef("Max Available Cores", "maxAvailable", "number"),
            ColumnDef("Max Available Memory (GB)", "maxMemory", "number"),
            ColumnDef("Core:Memory Ratio", "coreMemoryRatio", "number"),
            ColumnDef("Workspace", "workspace"),
            ColumnDef("Zone", "zone"),
        ],
    ),
    "pvsSapProfiles": ResourceSchema(
        worksheet_name="pPvsSapProfiles",
        domain="powervs",
        resource_type="pvsSapProfiles",
        columns=[
            ColumnDef("Profile ID", "profileID"),
            ColumnDef("Type", "type"),
            ColumnDef("Cores", "cores", "number"),
            ColumnDef("Memory (GB)", "memory", "number"),
            ColumnDef("SAPS", "saps", "number"),
            ColumnDef("Certified", "certified", "boolean"),
            ColumnDef("Workspace", "workspace"),
            ColumnDef("Zone", "zone"),
        ],
    ),
    "pvsImages": ResourceSchema(
        worksheet_name="pPvsImages",
        domain="powervs",
        resource_type="pvsImages",
        columns=[
            ColumnDef("ID", "imageID"),
            ColumnDef("Name", "name"),
            ColumnDef("State", "state"),
            ColumnDef("OS", "operatingSystem"),
            ColumnDef("Architecture", "architecture"),
            ColumnDef("Size (GB)", "size", "number"),
            ColumnDef("Storage Type", "storageType"),
            ColumnDef("Workspace", "workspace"),
            ColumnDef("Zone", "zone"),
            ColumnDef("Created", "creationDate", "date"),
        ],
    ),
    "pvsStockImages": ResourceSchema(
        worksheet_name="pPvsStockImages",
        domain="powervs",
        resource_type="pvsStockImages",
        columns=[
            ColumnDef("ID", "imageID"),
            ColumnDef("Name", "name"),
            ColumnDef("State", "state"),
            ColumnDef("OS", "operatingSystem"),
            ColumnDef("Architecture", "architecture"),
            ColumnDef("Storage Type", "storageType"),
            ColumnDef("Workspace", "workspace"),
            ColumnDef("Zone", "zone"),
        ],
    ),
    "pvsEvents": ResourceSchema(
        worksheet_name="pPvsEvents",
        domain="powervs",
        resource_type="pvsEvents",
        columns=[
            ColumnDef("Event ID", "eventID"),
            ColumnDef("Action", "action"),
            ColumnDef("Level", "level"),
            ColumnDef("Message", "message"),
            ColumnDef("Resource", "resource"),
            ColumnDef("User", "user"),
            ColumnDef("Timestamp", "timestamp", "date"),
            ColumnDef("Workspace", "workspace"),
            ColumnDef("Zone", "zone"),
        ],
    ),
}


# ──────────────────────────────────────────────
# VMWARE INFRASTRUCTURE SCHEMAS
# ──────────────────────────────────────────────

VMWARE_SCHEMAS: dict[str, ResourceSchema] = {
    "vmwareInstances": ResourceSchema(
        worksheet_name="vVMwareInstances",
        domain="vmware",
        resource_type="vmwareInstances",
        columns=[
            ColumnDef("ID", "id"),
            ColumnDef("Name", "name"),
            ColumnDef("Location", "location"),
            ColumnDef("Status", "status"),
            ColumnDef("Deploy Type", "deployType"),
            ColumnDef("Domain Type", "domainType"),
            ColumnDef("NSX Type", "nsxType"),
            ColumnDef("Version", "version"),
            ColumnDef("Clusters", "clusterCount", "number"),
            ColumnDef("Creator", "creator"),
            ColumnDef("CRN", "crn"),
        ],
    ),
    "vmwareClusters": ResourceSchema(
        worksheet_name="vVMwareClusters",
        domain="vmware",
        resource_type="vmwareClusters",
        columns=[
            ColumnDef("ID", "id"),
            ColumnDef("Name", "name"),
            ColumnDef("Location", "location"),
            ColumnDef("Status", "status"),
            ColumnDef("Host Count", "hostCount", "number"),
            ColumnDef("Storage Type", "storageType"),
            ColumnDef("Instance ID", "instanceId"),
        ],
    ),
    "vmwareHosts": ResourceSchema(
        worksheet_name="vVMwareHosts",
        domain="vmware",
        resource_type="vmwareHosts",
        columns=[
            ColumnDef("Hostname", "hostname"),
            ColumnDef("Public IP", "publicIp"),
            ColumnDef("Private IP", "privateIp"),
            ColumnDef("Status", "status"),
            ColumnDef("Server ID", "serverId"),
            ColumnDef("Version", "version"),
            ColumnDef("Memory (GB)", "memory", "number"),
            ColumnDef("CPUs", "cpus", "number"),
            ColumnDef("Cluster", "clusterName"),
            ColumnDef("Location", "location"),
            ColumnDef("Instance ID", "instanceId"),
            ColumnDef("Cluster ID", "clusterId"),
        ],
    ),
    "vmwareVlans": ResourceSchema(
        worksheet_name="vVMwareVlans",
        domain="vmware",
        resource_type="vmwareVlans",
        columns=[
            ColumnDef("VLAN Number", "vlanNumber", "number"),
            ColumnDef("Name", "name"),
            ColumnDef("Purpose", "purpose"),
            ColumnDef("Primary Router", "primaryRouter"),
            ColumnDef("Cluster", "clusterName"),
            ColumnDef("Location", "location"),
            ColumnDef("Instance ID", "instanceId"),
            ColumnDef("Cluster ID", "clusterId"),
        ],
    ),
    "vmwareSubnets": ResourceSchema(
        worksheet_name="vVMwareSubnets",
        domain="vmware",
        resource_type="vmwareSubnets",
        columns=[
            ColumnDef("CIDR", "cidr"),
            ColumnDef("Netmask", "netmask"),
            ColumnDef("Gateway", "gateway"),
            ColumnDef("Type", "type"),
            ColumnDef("Purpose", "purpose"),
            ColumnDef("VLAN", "vlanNumber", "number"),
            ColumnDef("VLAN Name", "vlanName"),
            ColumnDef("Cluster", "clusterName"),
            ColumnDef("Location", "location"),
            ColumnDef("Instance ID", "instanceId"),
        ],
    ),
    "directorSites": ResourceSchema(
        worksheet_name="vDirectorSites",
        domain="vmware",
        resource_type="directorSites",
        columns=[
            ColumnDef("ID", "id"),
            ColumnDef("Name", "name"),
            ColumnDef("Status", "status"),
            ColumnDef("Region", "region"),
            ColumnDef("PVDCs", "pvdcCount", "number"),
            ColumnDef("Created", "createdAt", "date"),
        ],
    ),
    "pvdcs": ResourceSchema(
        worksheet_name="vPVDCs",
        domain="vmware",
        resource_type="pvdcs",
        columns=[
            ColumnDef("ID", "id"),
            ColumnDef("Name", "name"),
            ColumnDef("Datacenter", "datacenter"),
            ColumnDef("Status", "status"),
            ColumnDef("Provider Type", "providerType"),
            ColumnDef("Clusters", "clusterCount", "number"),
            ColumnDef("Director Site ID", "directorSiteId"),
        ],
    ),
    "vcfClusters": ResourceSchema(
        worksheet_name="vVCFClusters",
        domain="vmware",
        resource_type="vcfClusters",
        columns=[
            ColumnDef("ID", "id"),
            ColumnDef("Name", "name"),
            ColumnDef("Host Count", "hostCount", "number"),
            ColumnDef("Status", "status"),
            ColumnDef("Datacenter", "datacenter"),
            ColumnDef("Host Profile", "hostProfile"),
            ColumnDef("Storage Type", "storageType"),
            ColumnDef("PVDC ID", "pvdcId"),
        ],
    ),
    "vdcs": ResourceSchema(
        worksheet_name="vVDCs",
        domain="vmware",
        resource_type="vdcs",
        columns=[
            ColumnDef("ID", "id"),
            ColumnDef("Name", "name"),
            ColumnDef("Status", "status"),
            ColumnDef("Director Site", "directorSiteName"),
            ColumnDef("CPU", "cpu"),
            ColumnDef("RAM", "ram"),
            ColumnDef("Disk", "disk"),
            ColumnDef("Region", "region"),
            ColumnDef("Type", "type"),
            ColumnDef("Created", "createdAt", "date"),
        ],
    ),
    "multitenantSites": ResourceSchema(
        worksheet_name="vMultitenantSites",
        domain="vmware",
        resource_type="multitenantSites",
        columns=[
            ColumnDef("ID", "id"),
            ColumnDef("Name", "name"),
            ColumnDef("Region", "region"),
            ColumnDef("PVDCs", "pvdcCount", "number"),
        ],
    ),
    "vmwareCrossReferences": ResourceSchema(
        worksheet_name="vVMwareCrossReferences",
        domain="vmware",
        resource_type="vmwareCrossReferences",
        columns=[
            ColumnDef("Classic Resource Type", "classicResourceType"),
            ColumnDef("Classic Resource ID", "classicResourceId"),
            ColumnDef("Classic Resource Name", "classicResourceName"),
            ColumnDef("VMware Role", "vmwareRole"),
            ColumnDef("VMware Resource Type", "vmwareResourceType"),
            ColumnDef("VMware Resource ID", "vmwareResourceId"),
            ColumnDef("VMware Resource Name", "vmwareResourceName"),
        ],
    ),
}


ALL_SCHEMAS = {**CLASSIC_SCHEMAS, **VPC_SCHEMAS, **POWERVS_SCHEMAS, **VMWARE_SCHEMAS}
```

**Step 4: Run test to verify it passes**

Run: `source .venv/bin/activate && pytest tests/test_schema.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add src/cloud_harvester/schema.py tests/test_schema.py
git commit -m "feat: add complete XLSX schema definitions for all domains"
```

---

### Task 4: Base collector and registry

**Files:**
- Create: `src/cloud_harvester/collectors/__init__.py`
- Create: `src/cloud_harvester/collectors/base.py`
- Create: `src/cloud_harvester/collectors/registry.py`
- Create: `tests/test_registry.py`

**Step 1: Write the failing test**

```python
# tests/test_registry.py
from cloud_harvester.collectors.base import BaseCollector
from cloud_harvester.collectors.registry import CollectorRegistry


class FakeCollector(BaseCollector):
    domain = "classic"
    resource_type = "test"
    worksheet_name = "vTest"

    def collect(self, client, context):
        return [{"id": 1, "name": "test"}]


def test_register_and_get_collector():
    registry = CollectorRegistry()
    collector = FakeCollector()
    registry.register(collector)
    assert registry.get("classic", "test") is collector


def test_get_by_domain():
    registry = CollectorRegistry()
    c1 = FakeCollector()
    c1.resource_type = "a"
    c2 = FakeCollector()
    c2.resource_type = "b"
    c2.domain = "vpc"
    registry.register(c1)
    registry.register(c2)
    classic = registry.get_by_domain("classic")
    assert len(classic) == 1
    vpc = registry.get_by_domain("vpc")
    assert len(vpc) == 1
```

**Step 2: Run test to verify it fails**

Run: `source .venv/bin/activate && pytest tests/test_registry.py -v`
Expected: FAIL

**Step 3: Write implementation**

```python
# src/cloud_harvester/collectors/__init__.py
```

```python
# src/cloud_harvester/collectors/base.py
from abc import ABC, abstractmethod


class BaseCollector(ABC):
    domain: str = ""
    resource_type: str = ""
    worksheet_name: str = ""

    @abstractmethod
    def collect(self, client, context: dict) -> list[dict]:
        """Collect resources. Returns list of row dicts matching schema fields."""
        ...
```

```python
# src/cloud_harvester/collectors/registry.py
from cloud_harvester.collectors.base import BaseCollector


class CollectorRegistry:
    def __init__(self):
        self._collectors: dict[str, BaseCollector] = {}

    def register(self, collector: BaseCollector) -> None:
        key = f"{collector.domain}:{collector.resource_type}"
        self._collectors[key] = collector

    def get(self, domain: str, resource_type: str) -> BaseCollector | None:
        return self._collectors.get(f"{domain}:{resource_type}")

    def get_by_domain(self, domain: str) -> list[BaseCollector]:
        return [c for k, c in self._collectors.items() if k.startswith(f"{domain}:")]

    def get_all(self) -> list[BaseCollector]:
        return list(self._collectors.values())

    def get_domains(self) -> list[str]:
        return sorted(set(c.domain for c in self._collectors.values()))
```

**Step 4: Run test to verify it passes**

Run: `source .venv/bin/activate && pytest tests/test_registry.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add src/cloud_harvester/collectors/ tests/test_registry.py
git commit -m "feat: add base collector and registry"
```

---

### Task 5: XLSX writer module

**Files:**
- Create: `src/cloud_harvester/xlsx_writer.py`
- Create: `tests/test_xlsx_writer.py`

**Step 1: Write the failing test**

```python
# tests/test_xlsx_writer.py
import os
import tempfile
from openpyxl import load_workbook
from cloud_harvester.xlsx_writer import write_xlsx
from cloud_harvester.schema import CLASSIC_SCHEMAS


def test_write_xlsx_creates_file():
    data = {
        "virtualServers": [
            {"id": 123, "hostname": "web01", "domain": "example.com", "fqdn": "web01.example.com",
             "primaryIp": "10.0.0.1", "backendIp": "10.0.0.2", "maxCpu": 4, "maxMemory": 8192,
             "status": "Active", "powerState": "Running", "datacenter": "dal13", "os": "Ubuntu 22.04",
             "hourlyBilling": "No", "createDate": "2025-01-01", "recurringFee": "150.00",
             "costBasis": "Monthly", "notes": "", "privateNetworkOnly": "No", "localDisk": "No",
             "startCpus": 4, "modifyDate": "2025-02-01", "dedicated": "No", "placementGroupId": 0,
             "tags": "web,prod", "diskGb": 100, "networkVlans": "1234,5678"},
        ],
    }
    account_info = {
        "name": "Test Account",
        "id": "12345",
        "email": "test@example.com",
        "owner": "Test Owner",
    }

    with tempfile.TemporaryDirectory() as tmpdir:
        filepath = os.path.join(tmpdir, "test.xlsx")
        write_xlsx(filepath, data, CLASSIC_SCHEMAS, account_info)
        assert os.path.exists(filepath)

        wb = load_workbook(filepath)
        assert "Summary" in wb.sheetnames
        assert "vVirtualServers" in wb.sheetnames

        ws = wb["vVirtualServers"]
        headers = [cell.value for cell in ws[1]]
        assert "ID" in headers
        assert "Hostname" in headers
        assert ws.cell(row=2, column=1).value == 123
        assert ws.cell(row=2, column=2).value == "web01"


def test_write_xlsx_empty_data_still_creates_summary():
    with tempfile.TemporaryDirectory() as tmpdir:
        filepath = os.path.join(tmpdir, "empty.xlsx")
        write_xlsx(filepath, {}, CLASSIC_SCHEMAS, {"name": "Empty", "id": "0"})
        assert os.path.exists(filepath)
        wb = load_workbook(filepath)
        assert "Summary" in wb.sheetnames
```

**Step 2: Run test to verify it fails**

Run: `source .venv/bin/activate && pytest tests/test_xlsx_writer.py -v`
Expected: FAIL

**Step 3: Write implementation**

```python
# src/cloud_harvester/xlsx_writer.py
"""Generate XLSX files matching classic_analyser's format."""
from datetime import datetime, timezone

from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment

from cloud_harvester.schema import ResourceSchema

HEADER_FILL = PatternFill(start_color="FF0F62FE", end_color="FF0F62FE", fill_type="solid")
HEADER_FONT = Font(bold=True, color="FFFFFFFF")


def write_xlsx(
    filepath: str,
    data: dict[str, list[dict]],
    schemas: dict[str, ResourceSchema],
    account_info: dict,
) -> None:
    """Write collected data to XLSX file."""
    wb = Workbook()

    # Summary sheet (first sheet)
    ws_summary = wb.active
    ws_summary.title = "Summary"
    _write_summary(ws_summary, data, schemas, account_info)

    # Resource worksheets
    for resource_key, rows in data.items():
        schema = schemas.get(resource_key)
        if not schema or not rows:
            continue
        ws = wb.create_sheet(title=schema.worksheet_name)
        _write_resource_sheet(ws, schema, rows)

    wb.save(filepath)


def _write_summary(ws, data, schemas, account_info):
    """Write the Summary sheet with account info and resource counts."""
    ws.column_dimensions["A"].width = 30
    ws.column_dimensions["B"].width = 50

    rows = [
        ("Account Name", account_info.get("name", "")),
        ("Account ID", account_info.get("id", "")),
        ("Account Email", account_info.get("email", "")),
        ("Account Owner", account_info.get("owner", "")),
        ("Collection Timestamp", datetime.now(timezone.utc).isoformat()),
        ("", ""),
    ]

    # Resource counts
    for resource_key, schema in schemas.items():
        count = len(data.get(resource_key, []))
        rows.append((schema.worksheet_name, count))

    for row_idx, (key, value) in enumerate(rows, start=1):
        ws.cell(row=row_idx, column=1, value=key)
        ws.cell(row=row_idx, column=2, value=value)


def _write_resource_sheet(ws, schema: ResourceSchema, rows: list[dict]):
    """Write a resource worksheet with headers and data."""
    columns = schema.columns

    # Header row
    for col_idx, col_def in enumerate(columns, start=1):
        cell = ws.cell(row=1, column=col_idx, value=col_def.header)
        cell.font = HEADER_FONT
        cell.fill = HEADER_FILL
        cell.alignment = Alignment(vertical="center")
    ws.row_dimensions[1].height = 24

    # Data rows
    for row_idx, row_data in enumerate(rows, start=2):
        for col_idx, col_def in enumerate(columns, start=1):
            value = row_data.get(col_def.field, "")
            cell = ws.cell(row=row_idx, column=col_idx, value=_format_value(value, col_def.data_type))

    # Auto-width
    for col_idx, col_def in enumerate(columns, start=1):
        max_len = len(col_def.header)
        for row_idx in range(2, len(rows) + 2):
            val = str(ws.cell(row=row_idx, column=col_idx).value or "")
            max_len = max(max_len, len(val))
        ws.column_dimensions[ws.cell(row=1, column=col_idx).column_letter].width = min(max_len + 2, 60)


def _format_value(value, data_type: str):
    """Format a value for XLSX output."""
    if value is None:
        return ""
    if isinstance(value, list):
        return ", ".join(str(v) for v in value)
    if isinstance(value, dict):
        return str(value)
    if data_type == "boolean":
        if isinstance(value, bool):
            return "Yes" if value else "No"
        return str(value)
    return value
```

**Step 4: Run test to verify it passes**

Run: `source .venv/bin/activate && pytest tests/test_xlsx_writer.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add src/cloud_harvester/xlsx_writer.py tests/test_xlsx_writer.py
git commit -m "feat: add XLSX writer with classic_analyser-compatible formatting"
```

---

### Task 6: CLI entry point

**Files:**
- Create: `src/cloud_harvester/cli.py`
- Create: `tests/test_cli.py`

**Step 1: Write the failing test**

```python
# tests/test_cli.py
from click.testing import CliRunner
from cloud_harvester.cli import main


def test_cli_requires_api_key():
    runner = CliRunner()
    result = runner.invoke(main, [])
    assert result.exit_code != 0
    assert "api-key" in result.output.lower() or "IBMCLOUD_API_KEY" in result.output.lower()


def test_cli_help():
    runner = CliRunner()
    result = runner.invoke(main, ["--help"])
    assert result.exit_code == 0
    assert "cloud-harvester" in result.output.lower() or "api-key" in result.output.lower()
```

**Step 2: Run test to verify it fails**

Run: `source .venv/bin/activate && pytest tests/test_cli.py -v`
Expected: FAIL

**Step 3: Write implementation**

```python
# src/cloud_harvester/cli.py
"""CLI entry point for cloud-harvester."""
import os
import sys
from datetime import datetime, timezone

import click
from rich.console import Console

from cloud_harvester import __version__

console = Console()


@click.command()
@click.option("--api-key", envvar="IBMCLOUD_API_KEY", help="IBM Cloud API key (or set IBMCLOUD_API_KEY)")
@click.option("--domains", default="classic,vpc,powervs,vmware", help="Comma-separated domains to collect")
@click.option("--skip", default="", help="Comma-separated resource types to skip")
@click.option("--account", default="", help="Comma-separated account IDs to limit collection")
@click.option("--region", default="", help="Comma-separated regions/datacenters to filter")
@click.option("--output", default=".", help="Output directory for XLSX files")
@click.option("--concurrency", default=5, type=int, help="Parallel threads per domain")
@click.option("--resume/--no-resume", default=False, help="Resume interrupted collection")
@click.option("--no-cache", is_flag=True, help="Force fresh collection, ignore cache")
@click.version_option(version=__version__)
def main(api_key, domains, skip, account, region, output, concurrency, resume, no_cache):
    """Collect IBM Cloud infrastructure data into XLSX for classic_analyser."""
    if not api_key:
        console.print("[red]Error:[/red] API key required. Use --api-key or set IBMCLOUD_API_KEY environment variable.")
        sys.exit(1)

    domain_list = [d.strip() for d in domains.split(",") if d.strip()]
    skip_list = [s.strip() for s in skip.split(",") if s.strip()]
    account_list = [a.strip() for a in account.split(",") if a.strip()]
    region_list = [r.strip() for r in region.split(",") if r.strip()]

    from cloud_harvester.harvester import run_harvest

    run_harvest(
        api_key=api_key,
        domains=domain_list,
        skip=skip_list,
        accounts=account_list,
        regions=region_list,
        output_dir=output,
        concurrency=concurrency,
        resume=resume,
        no_cache=no_cache,
    )
```

**Step 4: Run test to verify it passes**

Run: `source .venv/bin/activate && pytest tests/test_cli.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add src/cloud_harvester/cli.py tests/test_cli.py
git commit -m "feat: add CLI entry point with all flags"
```

---

### Task 7: Harvester orchestrator

**Files:**
- Create: `src/cloud_harvester/harvester.py`
- Create: `src/cloud_harvester/cache.py`
- Create: `src/cloud_harvester/utils/__init__.py`
- Create: `src/cloud_harvester/utils/formatting.py`
- Create: `tests/test_harvester.py`

**Step 1: Write the failing test**

```python
# tests/test_harvester.py
from unittest.mock import patch, MagicMock
from cloud_harvester.harvester import run_harvest


def test_run_harvest_authenticates_and_discovers_accounts():
    with patch("cloud_harvester.harvester.authenticate", return_value="token") as mock_auth, \
         patch("cloud_harvester.harvester.get_account_info") as mock_info, \
         patch("cloud_harvester.harvester.collect_account") as mock_collect:

        mock_info.return_value = {"name": "Test", "account_id": "123", "owner_email": "t@t.com"}

        run_harvest(
            api_key="test-key",
            domains=["classic"],
            skip=[],
            accounts=[],
            regions=[],
            output_dir="/tmp",
            concurrency=5,
            resume=False,
            no_cache=True,
        )
        mock_auth.assert_called_once_with("test-key")
        mock_collect.assert_called_once()
```

**Step 2: Run test to verify it fails**

Run: `source .venv/bin/activate && pytest tests/test_harvester.py -v`
Expected: FAIL

**Step 3: Write implementation**

```python
# src/cloud_harvester/utils/__init__.py
```

```python
# src/cloud_harvester/utils/formatting.py
"""Data formatting utilities."""


def safe_string(value) -> str:
    """Convert value to a safe string for XLSX."""
    if value is None:
        return ""
    if isinstance(value, list):
        return ", ".join(str(v) for v in value)
    if isinstance(value, dict):
        import json
        return json.dumps(value)
    return str(value)


def bool_to_yesno(value) -> str:
    """Convert boolean to Yes/No string."""
    if isinstance(value, bool):
        return "Yes" if value else "No"
    if isinstance(value, str):
        return value
    return "Yes" if value else "No"
```

```python
# src/cloud_harvester/cache.py
"""Collection cache for resume support."""
import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path

CACHE_DIR = ".cloud-harvester-cache"


class CollectionCache:
    def __init__(self, account_id: str, api_key_hash: str, base_dir: str = "."):
        self.cache_path = Path(base_dir) / CACHE_DIR / account_id
        self.api_key_hash = api_key_hash
        self.manifest_path = self.cache_path / "manifest.json"

    @staticmethod
    def hash_api_key(api_key: str) -> str:
        return hashlib.sha256(api_key.encode()).hexdigest()[:16]

    def exists(self) -> bool:
        if not self.manifest_path.exists():
            return False
        manifest = self._read_manifest()
        return manifest.get("api_key_hash") == self.api_key_hash

    def save(self, resource_type: str, data: list[dict]) -> None:
        self.cache_path.mkdir(parents=True, exist_ok=True)
        filepath = self.cache_path / f"{resource_type}.json"
        with open(filepath, "w") as f:
            json.dump(data, f)
        self._update_manifest(resource_type)

    def load(self, resource_type: str) -> list[dict] | None:
        filepath = self.cache_path / f"{resource_type}.json"
        if not filepath.exists():
            return None
        with open(filepath) as f:
            return json.load(f)

    def completed_types(self) -> set[str]:
        manifest = self._read_manifest()
        return set(manifest.get("completed", {}).keys())

    def cleanup(self) -> None:
        import shutil
        if self.cache_path.exists():
            shutil.rmtree(self.cache_path)

    def _read_manifest(self) -> dict:
        if not self.manifest_path.exists():
            return {}
        with open(self.manifest_path) as f:
            return json.load(f)

    def _update_manifest(self, resource_type: str) -> None:
        manifest = self._read_manifest()
        manifest["api_key_hash"] = self.api_key_hash
        manifest.setdefault("completed", {})[resource_type] = datetime.now(timezone.utc).isoformat()
        with open(self.manifest_path, "w") as f:
            json.dump(manifest, f, indent=2)
```

```python
# src/cloud_harvester/harvester.py
"""Main orchestrator for data collection."""
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone

from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn

from cloud_harvester.auth import authenticate, get_account_info
from cloud_harvester.cache import CollectionCache
from cloud_harvester.schema import CLASSIC_SCHEMAS, VPC_SCHEMAS, POWERVS_SCHEMAS, VMWARE_SCHEMAS, ALL_SCHEMAS
from cloud_harvester.xlsx_writer import write_xlsx

console = Console()

DOMAIN_SCHEMAS = {
    "classic": CLASSIC_SCHEMAS,
    "vpc": VPC_SCHEMAS,
    "powervs": POWERVS_SCHEMAS,
    "vmware": VMWARE_SCHEMAS,
}


def run_harvest(
    api_key: str,
    domains: list[str],
    skip: list[str],
    accounts: list[str],
    regions: list[str],
    output_dir: str,
    concurrency: int,
    resume: bool,
    no_cache: bool,
) -> None:
    """Main entry point for data collection."""
    console.print("[bold blue]cloud-harvester[/bold blue] - IBM Cloud Infrastructure Collector\n")

    # Authenticate
    with console.status("Authenticating..."):
        token = authenticate(api_key)
    console.print("[green]Authenticated successfully[/green]")

    # Get account info
    with console.status("Discovering account..."):
        account = get_account_info(api_key)
    account_name = account.get("name", "unknown")
    account_id = account.get("account_id", "unknown")
    console.print(f"Account: [bold]{account_name}[/bold] ({account_id})")

    # Collect for the account
    collect_account(
        api_key=api_key,
        token=token,
        account=account,
        domains=domains,
        skip=skip,
        regions=regions,
        output_dir=output_dir,
        concurrency=concurrency,
        resume=resume,
        no_cache=no_cache,
    )


def collect_account(
    api_key: str,
    token: str,
    account: dict,
    domains: list[str],
    skip: list[str],
    regions: list[str],
    output_dir: str,
    concurrency: int,
    resume: bool,
    no_cache: bool,
) -> None:
    """Collect all data for a single account."""
    account_name = account.get("name", "unknown")
    account_id = account.get("account_id", "unknown")
    account_email = account.get("owner_email", "")
    owner = account.get("owner", "")

    # Set up cache
    api_key_hash = CollectionCache.hash_api_key(api_key)
    cache = CollectionCache(account_id, api_key_hash, output_dir)

    if not no_cache and cache.exists() and not resume:
        console.print("[yellow]Found cached data from previous run. Use --resume to continue or --no-cache to start fresh.[/yellow]")
        return

    all_data: dict[str, list[dict]] = {}
    errors: list[str] = []

    # Collect per domain
    for domain in domains:
        schemas = DOMAIN_SCHEMAS.get(domain, {})
        if not schemas:
            continue

        console.print(f"\n[bold]Collecting {domain} resources...[/bold]")

        # Import domain collectors lazily
        collectors = _get_domain_collectors(domain)

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            console=console,
        ) as progress:
            task = progress.add_task(f"[cyan]{domain}", total=len(collectors))

            def collect_one(collector_info):
                resource_type, collector_fn = collector_info
                if resource_type in skip:
                    return resource_type, [], None
                if resume and not no_cache and resource_type in cache.completed_types():
                    cached = cache.load(resource_type)
                    if cached is not None:
                        return resource_type, cached, None
                try:
                    result = collector_fn(api_key, token, regions)
                    if not no_cache:
                        cache.save(resource_type, result)
                    return resource_type, result, None
                except Exception as e:
                    return resource_type, [], str(e)

            with ThreadPoolExecutor(max_workers=concurrency) as executor:
                futures = {executor.submit(collect_one, c): c for c in collectors}
                for future in as_completed(futures):
                    resource_type, result, error = future.result()
                    all_data[resource_type] = result
                    if error:
                        errors.append(f"{resource_type}: {error}")
                        progress.console.print(f"  [yellow]Warning:[/yellow] {resource_type} - {error}")
                    else:
                        count = len(result)
                        progress.console.print(f"  {resource_type}: {count} items")
                    progress.advance(task)

    # Build schemas for collected data
    collected_schemas = {}
    for domain in domains:
        collected_schemas.update(DOMAIN_SCHEMAS.get(domain, {}))

    # Write XLSX
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    safe_name = account_name.replace(" ", "_").replace("/", "_")[:50]
    filename = f"{safe_name}_{account_id}_{timestamp}.xlsx"
    filepath = os.path.join(output_dir, filename)

    with console.status("Writing XLSX..."):
        account_info = {
            "name": account_name,
            "id": account_id,
            "email": account_email,
            "owner": owner,
        }
        write_xlsx(filepath, all_data, collected_schemas, account_info)

    # Cleanup cache
    cache.cleanup()

    # Summary
    console.print(f"\n[bold green]Done![/bold green] Saved to: {filepath}")
    total_resources = sum(len(v) for v in all_data.values())
    console.print(f"Total resources collected: {total_resources}")
    if errors:
        console.print(f"[yellow]Warnings: {len(errors)} resource types had errors[/yellow]")


def _get_domain_collectors(domain: str) -> list[tuple[str, callable]]:
    """Get collector functions for a domain. Returns list of (resource_type, fn)."""
    if domain == "classic":
        from cloud_harvester.collectors.classic import get_collectors
        return get_collectors()
    elif domain == "vpc":
        from cloud_harvester.collectors.vpc import get_collectors
        return get_collectors()
    elif domain == "powervs":
        from cloud_harvester.collectors.powervs import get_collectors
        return get_collectors()
    elif domain == "vmware":
        from cloud_harvester.collectors.vmware import get_collectors
        return get_collectors()
    return []
```

**Step 4: Run test to verify it passes**

Run: `source .venv/bin/activate && pytest tests/test_harvester.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add src/cloud_harvester/harvester.py src/cloud_harvester/cache.py src/cloud_harvester/utils/ tests/test_harvester.py
git commit -m "feat: add harvester orchestrator with parallel collection and caching"
```

---

## Phase 3: Classic Infrastructure Collectors

### Task 8: Classic collector package init and first collectors (compute)

**Files:**
- Create: `src/cloud_harvester/collectors/classic/__init__.py`
- Create: `src/cloud_harvester/collectors/classic/virtual_servers.py`
- Create: `src/cloud_harvester/collectors/classic/bare_metal.py`
- Create: `src/cloud_harvester/collectors/classic/dedicated_hosts.py`
- Create: `src/cloud_harvester/collectors/classic/images.py`
- Create: `src/cloud_harvester/collectors/classic/placement_groups.py`
- Create: `src/cloud_harvester/collectors/classic/reserved_capacity.py`
- Create: `tests/test_classic_collectors.py`

Each classic collector follows the same pattern:
1. Create a SoftLayer client from the API key
2. Call the appropriate SL API method with the object mask
3. Transform the response into flat dicts matching the schema field names
4. Return the list

**Step 1: Write the failing test**

```python
# tests/test_classic_collectors.py
from unittest.mock import patch, MagicMock
from cloud_harvester.collectors.classic.virtual_servers import collect_virtual_servers
from cloud_harvester.collectors.classic.bare_metal import collect_bare_metal


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
```

**Step 2: Run test to verify it fails**

Run: `source .venv/bin/activate && pytest tests/test_classic_collectors.py -v`
Expected: FAIL

**Step 3: Write the collector implementations**

The `__init__.py` registers all classic collectors:

```python
# src/cloud_harvester/collectors/classic/__init__.py
"""Classic infrastructure collectors."""


def get_collectors():
    """Return list of (resource_type, collector_fn) tuples."""
    from .virtual_servers import collect_virtual_servers
    from .bare_metal import collect_bare_metal
    from .dedicated_hosts import collect_dedicated_hosts
    from .images import collect_images
    from .placement_groups import collect_placement_groups
    from .reserved_capacity import collect_reserved_capacity
    from .vlans import collect_vlans
    from .subnets import collect_subnets
    from .gateways import collect_gateways
    from .firewalls import collect_firewalls
    from .security_groups import collect_security_groups
    from .load_balancers import collect_load_balancers
    from .vpn_tunnels import collect_vpn_tunnels
    from .block_storage import collect_block_storage
    from .file_storage import collect_file_storage
    from .object_storage import collect_object_storage
    from .ssl_certificates import collect_ssl_certificates
    from .ssh_keys import collect_ssh_keys
    from .dns import collect_dns_domains, collect_dns_records
    from .billing import collect_billing
    from .users import collect_users
    from .event_log import collect_event_log
    from .transit_gateways import collect_transit_gateways
    from .direct_links import collect_direct_links
    from .relationships import collect_relationships

    return [
        ("virtualServers", collect_virtual_servers),
        ("bareMetal", collect_bare_metal),
        ("dedicatedHosts", collect_dedicated_hosts),
        ("images", collect_images),
        ("placementGroups", collect_placement_groups),
        ("reservedCapacity", collect_reserved_capacity),
        ("vlans", collect_vlans),
        ("subnets", collect_subnets),
        ("gateways", collect_gateways),
        ("firewalls", collect_firewalls),
        ("securityGroups", collect_security_groups),
        ("securityGroupRules", collect_security_groups),  # derived from security groups
        ("loadBalancers", collect_load_balancers),
        ("vpnTunnels", collect_vpn_tunnels),
        ("blockStorage", collect_block_storage),
        ("fileStorage", collect_file_storage),
        ("objectStorage", collect_object_storage),
        ("sslCertificates", collect_ssl_certificates),
        ("sshKeys", collect_ssh_keys),
        ("dnsDomains", collect_dns_domains),
        ("dnsRecords", collect_dns_records),
        ("billing", collect_billing),
        ("users", collect_users),
        ("eventLog", collect_event_log),
        ("transitGateways", collect_transit_gateways),
        ("directLinks", collect_direct_links),
        ("relationships", collect_relationships),
    ]
```

Example collector pattern (virtual_servers.py - the most complex one):

```python
# src/cloud_harvester/collectors/classic/virtual_servers.py
"""Collect IBM Cloud Classic Virtual Servers."""
import SoftLayer
from cloud_harvester.utils.formatting import bool_to_yesno, safe_string

OBJECT_MASK = (
    "mask[id,hostname,domain,fullyQualifiedDomainName,primaryIpAddress,"
    "primaryBackendIpAddress,maxCpu,maxMemory,startCpus,status,powerState,"
    "datacenter,operatingSystem[softwareDescription],hourlyBillingFlag,"
    "createDate,modifyDate,billingItem[recurringFee,hourlyRecurringFee,"
    "children[categoryCode,hourlyRecurringFee],orderItem],"
    "networkVlans[id,vlanNumber,name,networkSpace],"
    "blockDevices[diskImage[capacity,units]],tagReferences[tag],notes,"
    "dedicatedAccountHostOnlyFlag,placementGroupId,privateNetworkOnlyFlag,"
    "localDiskFlag]"
)


def _create_sl_client(api_key):
    return SoftLayer.create_client_from_env(api_key=api_key)


def collect_virtual_servers(api_key: str, token: str, regions: list[str]) -> list[dict]:
    """Collect all virtual server instances."""
    client = _create_sl_client(api_key)
    account = client["SoftLayer_Account"]

    try:
        vsis = account.getVirtualGuests(mask=OBJECT_MASK)
    except Exception:
        return []

    results = []
    for vsi in vsis:
        dc = vsi.get("datacenter", {}).get("name", "")
        if regions and dc and not any(r in dc for r in regions):
            continue

        os_desc = vsi.get("operatingSystem", {}).get("softwareDescription", {})
        os_name = os_desc.get("name", "")
        os_version = os_desc.get("version", "")
        os_str = f"{os_name} {os_version}".strip()

        # Calculate monthly fee
        billing = vsi.get("billingItem", {})
        recurring_fee = billing.get("recurringFee", "")
        cost_basis = "Monthly"
        if vsi.get("hourlyBillingFlag") and not recurring_fee:
            hourly = float(billing.get("hourlyRecurringFee", 0) or 0)
            for child in billing.get("children", []):
                hourly += float(child.get("hourlyRecurringFee", 0) or 0)
            recurring_fee = f"{hourly * 730:.2f}"
            cost_basis = "Estimated"

        # Calculate disk
        disk_gb = sum(
            bd.get("diskImage", {}).get("capacity", 0) or 0
            for bd in vsi.get("blockDevices", [])
        )

        # Format VLANs
        vlans = ", ".join(
            str(v.get("vlanNumber", ""))
            for v in vsi.get("networkVlans", [])
        )

        # Format tags
        tags = ", ".join(
            t.get("tag", {}).get("name", "")
            for t in vsi.get("tagReferences", [])
        )

        results.append({
            "id": vsi.get("id"),
            "hostname": vsi.get("hostname", ""),
            "domain": vsi.get("domain", ""),
            "fqdn": vsi.get("fullyQualifiedDomainName", ""),
            "primaryIp": vsi.get("primaryIpAddress", ""),
            "backendIp": vsi.get("primaryBackendIpAddress", ""),
            "maxCpu": vsi.get("maxCpu", 0),
            "maxMemory": vsi.get("maxMemory", 0),
            "status": vsi.get("status", {}).get("keyName", ""),
            "powerState": vsi.get("powerState", {}).get("keyName", ""),
            "datacenter": dc,
            "os": os_str,
            "hourlyBilling": bool_to_yesno(vsi.get("hourlyBillingFlag", False)),
            "createDate": vsi.get("createDate", ""),
            "recurringFee": recurring_fee,
            "costBasis": cost_basis,
            "notes": vsi.get("notes", "") or "",
            "privateNetworkOnly": bool_to_yesno(vsi.get("privateNetworkOnlyFlag", False)),
            "localDisk": bool_to_yesno(vsi.get("localDiskFlag", False)),
            "startCpus": vsi.get("startCpus", 0),
            "modifyDate": vsi.get("modifyDate", ""),
            "dedicated": bool_to_yesno(vsi.get("dedicatedAccountHostOnlyFlag", False)),
            "placementGroupId": vsi.get("placementGroupId") or 0,
            "tags": tags,
            "diskGb": disk_gb,
            "networkVlans": vlans,
        })

    return results
```

Each remaining classic collector follows this same pattern. The implementation for each is straightforward - call the SL API, transform the response. Here are the remaining collectors to implement:

- `bare_metal.py` - `getHardware()` with mask
- `dedicated_hosts.py` - `getDedicatedHosts()` with mask
- `images.py` - `getBlockDeviceTemplateGroups()` with mask
- `placement_groups.py` - `getPlacementGroups()` with mask
- `reserved_capacity.py` - `getReservedCapacityGroups()` with mask
- `vlans.py` - `getNetworkVlans()` with mask
- `subnets.py` - `getSubnets()` with mask
- `gateways.py` - `getNetworkGateways()` with mask
- `firewalls.py` - `getNetworkVlanFirewalls()` with mask
- `security_groups.py` - `getSecurityGroups()` with mask (also produces securityGroupRules)
- `load_balancers.py` - `getAdcLoadBalancers()` with mask
- `vpn_tunnels.py` - `getNetworkTunnelContexts()` with mask
- `block_storage.py` - `getIscsiNetworkStorage()` + `getNetworkStorage()` with mask
- `file_storage.py` - `getNasNetworkStorage()` with mask
- `object_storage.py` - `getHubNetworkStorage()` with mask
- `ssl_certificates.py` - `getSecurityCertificates()` with mask
- `ssh_keys.py` - `getSshKeys()` with mask
- `dns.py` - `getDomains()` with mask (produces both dnsDomains and dnsRecords)
- `billing.py` - `getAllBillingItems()` with mask
- `users.py` - `getUsers()` with mask
- `event_log.py` - `SoftLayer_Event_Log.getAllObjects()` with mask
- `transit_gateways.py` - REST calls to transit gateway API
- `direct_links.py` - REST calls to direct link API
- `relationships.py` - computed from all collected data

Each file should follow the exact pattern shown in `virtual_servers.py`:
1. Define OBJECT_MASK constant
2. Define `_create_sl_client(api_key)` helper
3. Define `collect_<resource>(api_key, token, regions)` function
4. Return list of dicts with keys matching schema field names

**Step 4: Run test to verify it passes**

Run: `source .venv/bin/activate && pytest tests/test_classic_collectors.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add src/cloud_harvester/collectors/classic/ tests/test_classic_collectors.py
git commit -m "feat: add classic infrastructure collectors"
```

---

## Phase 4: VPC Collectors

### Task 9: VPC collector package

**Files:**
- Create: `src/cloud_harvester/collectors/vpc/__init__.py`
- Create: `src/cloud_harvester/collectors/vpc/client.py`
- Create: One file per VPC resource type
- Create: `tests/test_vpc_collectors.py`

VPC collectors use the ibm-vpc SDK or direct REST calls. The pattern:
1. Create VPC client from API key
2. List all VPC-enabled regions
3. For each region, call the API and collect resources
4. Transform and return

The VPC client:

```python
# src/cloud_harvester/collectors/vpc/client.py
"""VPC API client."""
import requests

VPC_API_VERSION = "2024-06-01"
VPC_REGIONS = [
    "us-south", "us-east", "eu-gb", "eu-de", "eu-es",
    "jp-tok", "jp-osa", "au-syd", "ca-tor", "br-sao",
]
TRANSIT_GW_BASE = "https://transit.cloud.ibm.com/v1"
DIRECT_LINK_BASE = "https://directlink.cloud.ibm.com/v1"


class VpcClient:
    def __init__(self, token: str):
        self.token = token
        self.headers = {"Authorization": f"Bearer {token}"}

    def list_resources(self, region: str, path: str, items_key: str) -> list[dict]:
        """List all resources with pagination."""
        base = f"https://{region}.iaas.cloud.ibm.com/v1"
        url = f"{base}/{path}?version={VPC_API_VERSION}&generation=2&limit=100"
        all_items = []
        while url:
            resp = requests.get(url, headers=self.headers, timeout=60)
            if resp.status_code == 403:
                return []
            resp.raise_for_status()
            data = resp.json()
            all_items.extend(data.get(items_key, []))
            url = data.get("next", {}).get("href")
        return all_items

    def list_transit_gateways(self) -> list[dict]:
        url = f"{TRANSIT_GW_BASE}/transit_gateways?version=2024-01-01&limit=100"
        all_items = []
        while url:
            resp = requests.get(url, headers=self.headers, timeout=60)
            if resp.status_code == 403:
                return []
            resp.raise_for_status()
            data = resp.json()
            all_items.extend(data.get("transit_gateways", []))
            url = data.get("next", {}).get("href")
        return all_items

    def list_transit_gateway_connections(self, tg_id: str) -> list[dict]:
        url = f"{TRANSIT_GW_BASE}/transit_gateways/{tg_id}/connections?version=2024-01-01&limit=100"
        resp = requests.get(url, headers=self.headers, timeout=60)
        if resp.status_code == 403:
            return []
        resp.raise_for_status()
        return resp.json().get("connections", [])

    def list_direct_link_gateways(self) -> list[dict]:
        url = f"{DIRECT_LINK_BASE}/gateways?version=2024-06-01"
        resp = requests.get(url, headers=self.headers, timeout=60)
        if resp.status_code == 403:
            return []
        resp.raise_for_status()
        return resp.json().get("gateways", [])

    def list_direct_link_virtual_connections(self, gw_id: str) -> list[dict]:
        url = f"{DIRECT_LINK_BASE}/gateways/{gw_id}/virtual_connections?version=2024-06-01"
        resp = requests.get(url, headers=self.headers, timeout=60)
        if resp.status_code == 403:
            return []
        resp.raise_for_status()
        return resp.json().get("virtual_connections", [])
```

The `__init__.py` follows the same pattern as classic, registering all collectors. Each VPC collector:
1. Creates a VpcClient
2. Iterates over regions (filtered by --region)
3. Calls the appropriate API
4. Transforms response to match schema field names

**Commit after implementing:**

```bash
git add src/cloud_harvester/collectors/vpc/ tests/test_vpc_collectors.py
git commit -m "feat: add VPC infrastructure collectors"
```

---

## Phase 5: PowerVS Collectors

### Task 10: PowerVS collector package

**Files:**
- Create: `src/cloud_harvester/collectors/powervs/__init__.py`
- Create: `src/cloud_harvester/collectors/powervs/client.py`
- Create: One file per PowerVS resource type
- Create: `tests/test_powervs_collectors.py`

PowerVS collection pattern:
1. Discover PowerVS workspaces via Resource Controller API
2. For each workspace, create a PowerVS client
3. Call PowerVS API endpoints per workspace
4. Inject workspace and zone metadata into each row

PowerVS API base: `https://{region}.power-iaas.cloud.ibm.com/pcloud/v1/cloud-instances/{cloudInstanceId}/`

**Commit after implementing:**

```bash
git add src/cloud_harvester/collectors/powervs/ tests/test_powervs_collectors.py
git commit -m "feat: add PowerVS infrastructure collectors"
```

---

## Phase 6: VMware Collectors

### Task 11: VMware collector package

**Files:**
- Create: `src/cloud_harvester/collectors/vmware/__init__.py`
- Create: `src/cloud_harvester/collectors/vmware/client.py`
- Create: One file per VMware resource type
- Create: `tests/test_vmware_collectors.py`

VMware collection pattern:
1. VCF for Classic: Call VMware Solutions API (api.vmware-solutions.cloud.ibm.com)
2. VCFaaS: Call VCF API per region (api.{region}.vmware.cloud.ibm.com)
3. Cross-references: Build from classic bare metal data + VMware host data

**Commit after implementing:**

```bash
git add src/cloud_harvester/collectors/vmware/ tests/test_vmware_collectors.py
git commit -m "feat: add VMware/VCF infrastructure collectors"
```

---

## Phase 7: Relationships Builder

### Task 12: Implement relationships collector

**Files:**
- Modify: `src/cloud_harvester/collectors/classic/relationships.py`
- Create: `tests/test_relationships.py`

The relationships collector runs after all other collectors and builds parent-child mappings:

1. VLAN → Virtual Server (via networkVlans)
2. VLAN → Bare Metal (via networkVlans)
3. VLAN → Subnet (via networkVlan)
4. VLAN → Firewall (via networkVlan)
5. Network Gateway → VLAN (via insideVlans)
6. Block Storage → Virtual Server (via allowedVirtualGuests)
7. Block Storage → Bare Metal (via allowedHardware)
8. File Storage → Virtual Server (via allowedVirtualGuests)
9. File Storage → Bare Metal (via allowedHardware)
10. Security Group → Virtual Server (via networkComponentBindings)
11. Placement Group → Virtual Server (via placementGroupId)
12. Dedicated Host → Virtual Server (via dedicatedHost)

Note: The relationships collector needs access to all previously collected data, so it should receive the full `all_data` dict as context rather than making its own API calls.

**Commit after implementing:**

```bash
git add src/cloud_harvester/collectors/classic/relationships.py tests/test_relationships.py
git commit -m "feat: add relationship mapping builder"
```

---

## Phase 8: Integration & Polish

### Task 13: End-to-end integration test

**Files:**
- Create: `tests/test_integration.py`

Write an integration test that mocks all API calls and verifies a complete XLSX is generated with correct worksheet names and data.

```bash
git commit -m "test: add end-to-end integration test"
```

### Task 14: Add README

**Files:**
- Create: `README.md`

Include: installation, usage examples, supported resource types, authentication setup guide.

```bash
git commit -m "docs: add README with usage guide"
```

### Task 15: Final verification

Run full test suite:

```bash
source .venv/bin/activate && pytest tests/ -v --cov=cloud_harvester
```

Run linting:

```bash
source .venv/bin/activate && ruff check src/ tests/
```

Verify CLI works:

```bash
source .venv/bin/activate && cloud-harvester --help
```

```bash
git commit -m "chore: final verification and cleanup"
```
