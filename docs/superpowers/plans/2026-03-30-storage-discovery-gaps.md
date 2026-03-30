# Storage Discovery Gaps Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [x]`) syntax for tracking.

**Goal:** Close storage discovery gaps identified in the classic-to-vpc discovery doc by expanding block/file storage, VSI, and bare metal collectors with missing fields.

**Architecture:** Expand SoftLayer object masks in 4 existing collectors to fetch additional fields, add formatting logic for new data, update schema.py with new ColumnDef entries, and add/update tests for each change. No new files created except the analyser changelist doc.

**Tech Stack:** Python 3.11+, SoftLayer SDK, pytest, unittest.mock

**Spec:** `docs/superpowers/specs/2026-03-30-storage-discovery-gaps-design.md`

---

### Task 1: Block Storage — add missing fields

**Files:**
- Modify: `src/cloud_harvester/collectors/classic/block_storage.py:4-11` (OBJECT_MASK)
- Modify: `src/cloud_harvester/collectors/classic/block_storage.py:79-95` (results dict)
- Modify: `src/cloud_harvester/schema.py:193-213` (blockStorage schema)
- Test: `tests/test_classic_collectors.py`

- [x] **Step 1: Write the failing test for new block storage fields**

Add to `tests/test_classic_collectors.py`:

```python
from cloud_harvester.collectors.classic.block_storage import collect_block_storage


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
    assert r["encrypted"] == True
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
    assert r["encrypted"] == False
    assert r["allowedSubnets"] == ""
    assert r["snapshotSizeBytes"] == 0
    assert r["replicationStatus"] == ""
```

- [x] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_classic_collectors.py::test_collect_block_storage tests/test_classic_collectors.py::test_collect_block_storage_missing_new_fields -v`
Expected: FAIL — `KeyError` for missing fields like `datacenter`, `encrypted`

- [x] **Step 3: Expand the block storage object mask**

In `src/cloud_harvester/collectors/classic/block_storage.py`, replace the OBJECT_MASK:

```python
OBJECT_MASK = (
    "mask[id,username,capacityGb,iops,storageType,storageTierLevel,"
    "serviceResourceBackendIpAddress,lunId,"
    "allowedVirtualGuests[id,hostname],allowedHardware[id,hostname],"
    "allowedSubnets[id,networkIdentifier,cidr],"
    "snapshotCapacityGb,hasEncryptionAtRest,"
    "serviceResource.datacenter.name,"
    "parentVolume.snapshotSizeBytes,"
    "replicationStatus,"
    "replicationPartners[id,username,"
    "serviceResourceBackendIpAddress,"
    "serviceResource.datacenter.name,"
    "replicationSchedule.type.keyname],"
    "billingItem[recurringFee],createDate,notes]"
)
```

- [x] **Step 4: Add new fields to the results dict**

In `src/cloud_harvester/collectors/classic/block_storage.py`, update the replication partners formatting and the results dict. Replace the replication partners formatting block and the `results.append(...)`:

```python
        # Format replication partners (enriched with datacenter and schedule)
        repl_parts = []
        for r in item.get("replicationPartners", []):
            r_dc = r.get("serviceResource", {}).get("datacenter", {}).get("name", "")
            r_sched = r.get("replicationSchedule", {}).get("type", {}).get("keyname", "")
            repl_parts.append(
                f"{r.get('id')}:{r.get('username', '')}:{r_dc}:{r_sched}"
            )
        repl_partners = ", ".join(repl_parts)

        # Format allowed subnets
        allowed_subnets = ", ".join(
            f"{s.get('networkIdentifier', '')}/{s.get('cidr', '')}"
            for s in item.get("allowedSubnets", [])
        )

        results.append({
            "id": item.get("id"),
            "username": item.get("username", ""),
            "capacityGb": item.get("capacityGb", 0),
            "iops": item.get("iops", ""),
            "storageType": storage_type_str,
            "storageTierLevel": item.get("storageTierLevel", ""),
            "targetIp": item.get("serviceResourceBackendIpAddress", ""),
            "lunId": item.get("lunId", ""),
            "datacenter": item.get("serviceResource", {}).get("datacenter", {}).get("name", ""),
            "encrypted": bool(item.get("hasEncryptionAtRest", False)),
            "snapshotCapacityGb": item.get("snapshotCapacityGb", 0),
            "snapshotSizeBytes": item.get("parentVolume", {}).get("snapshotSizeBytes", 0) or 0,
            "replicationStatus": item.get("replicationStatus", "") or "",
            "recurringFee": billing.get("recurringFee", "") if billing else "",
            "createDate": item.get("createDate", ""),
            "notes": item.get("notes", "") or "",
            "allowedVirtualGuests": allowed_vsis,
            "allowedHardware": allowed_hw,
            "allowedSubnets": allowed_subnets,
            "replicationPartners": repl_partners,
        })
```

- [x] **Step 5: Update the block storage schema**

In `src/cloud_harvester/schema.py`, replace the blockStorage columns list (lines 197-212):

```python
        columns=[
            ColumnDef("ID", "id", "number"),
            ColumnDef("Username", "username"),
            ColumnDef("Capacity (GB)", "capacityGb", "number"),
            ColumnDef("IOPS", "iops"),
            ColumnDef("Storage Type", "storageType"),
            ColumnDef("Tier", "storageTierLevel"),
            ColumnDef("Target IP", "targetIp"),
            ColumnDef("LUN ID", "lunId"),
            ColumnDef("Datacenter", "datacenter"),
            ColumnDef("Encrypted", "encrypted", "boolean"),
            ColumnDef("Snapshot (GB)", "snapshotCapacityGb", "number"),
            ColumnDef("Snapshot Used (Bytes)", "snapshotSizeBytes", "number"),
            ColumnDef("Replication Status", "replicationStatus"),
            ColumnDef("Classic Monthly Fee", "recurringFee", "currency"),
            ColumnDef("Create Date", "createDate", "date"),
            ColumnDef("Notes", "notes"),
            ColumnDef("Allowed VSIs", "allowedVirtualGuests"),
            ColumnDef("Allowed Hardware", "allowedHardware"),
            ColumnDef("Allowed Subnets", "allowedSubnets"),
            ColumnDef("Replication Partners", "replicationPartners"),
        ],
```

- [x] **Step 6: Run tests to verify they pass**

Run: `pytest tests/test_classic_collectors.py -v`
Expected: All tests PASS including the two new block storage tests

- [x] **Step 7: Commit**

```bash
git add src/cloud_harvester/collectors/classic/block_storage.py src/cloud_harvester/schema.py tests/test_classic_collectors.py
git commit -m "feat: add datacenter, encrypted, subnets, snapshot, replication fields to block storage collector"
```

---

### Task 2: File Storage — add missing fields

**Files:**
- Modify: `src/cloud_harvester/collectors/classic/file_storage.py:5-11` (OBJECT_MASK)
- Modify: `src/cloud_harvester/collectors/classic/file_storage.py:57-74` (results dict)
- Modify: `src/cloud_harvester/schema.py:215-235` (fileStorage schema)
- Test: `tests/test_classic_collectors.py`

- [x] **Step 1: Write the failing test for new file storage fields**

Add to `tests/test_classic_collectors.py`:

```python
from cloud_harvester.collectors.classic.file_storage import collect_file_storage


def test_collect_file_storage():
    mock_client = MagicMock()
    mock_client.__getitem__ = MagicMock(return_value=MagicMock())
    mock_account = mock_client["SoftLayer_Account"]
    mock_account.getNasNetworkStorage.return_value = [
        {
            "id": 722595986,
            "username": "IBM02SEV1041833_1179",
            "capacityGb": 20,
            "iops": "",
            "storageType": {"keyName": "endurance_file_storage"},
            "storageTierLevel": "LOW_INTENSITY_TIER",
            "serviceResourceBackendIpAddress": "fsf-dal1301e-fz.adn.networklayer.com",
            "fileNetworkMountAddress": "fsf-dal1301e-fz.adn.networklayer.com:/IBM02SEV1041833_1179/data01",
            "bytesUsed": 393216000,
            "snapshotCapacityGb": 5,
            "hasEncryptionAtRest": False,
            "serviceResource": {"datacenter": {"name": "dal13"}},
            "parentVolume": {"snapshotSizeBytes": 159744},
            "replicationStatus": "REPLICATION_PROVISIONING_COMPLETED",
            "billingItem": {"recurringFee": "5.00"},
            "createDate": "2025-10-21T00:00:00",
            "notes": "Automation Storage Test",
            "allowedVirtualGuests": [{"id": 154290696, "hostname": "virtualserver01"}],
            "allowedHardware": [],
            "allowedSubnets": [
                {"id": 10, "networkIdentifier": "10.0.5.0", "cidr": 24},
            ],
            "replicationPartners": [
                {
                    "id": 722964836,
                    "username": "IBM02SEV1041833_1179_REP_1",
                    "serviceResourceBackendIpAddress": "fsf-dal1401a-fz.adn.networklayer.com",
                    "serviceResource": {"datacenter": {"name": "dal14"}},
                    "replicationSchedule": {"type": {"keyname": "REPLICATION_HOURLY"}},
                },
            ],
        }
    ]

    with patch("cloud_harvester.collectors.classic.file_storage._create_sl_client", return_value=mock_client):
        result = collect_file_storage("test-key", "token", [])

    assert len(result) == 1
    r = result[0]
    assert r["id"] == 722595986
    assert r["datacenter"] == "dal13"
    assert r["encrypted"] == False
    assert r["bytesUsed"] == 393216000
    assert r["allowedSubnets"] == "10.0.5.0/24"
    assert r["snapshotSizeBytes"] == 159744
    assert r["replicationStatus"] == "REPLICATION_PROVISIONING_COMPLETED"
    assert r["mountAddress"] == "fsf-dal1301e-fz.adn.networklayer.com:/IBM02SEV1041833_1179/data01"
    assert "dal14" in r["replicationPartners"]
    assert "REPLICATION_HOURLY" in r["replicationPartners"]


def test_collect_file_storage_missing_new_fields():
    """New fields default gracefully when absent from API response."""
    mock_client = MagicMock()
    mock_client.__getitem__ = MagicMock(return_value=MagicMock())
    mock_account = mock_client["SoftLayer_Account"]
    mock_account.getNasNetworkStorage.return_value = [
        {
            "id": 200,
            "username": "test-file-vol",
            "storageType": {"keyName": "endurance_file_storage"},
        }
    ]

    with patch("cloud_harvester.collectors.classic.file_storage._create_sl_client", return_value=mock_client):
        result = collect_file_storage("test-key", "token", [])

    assert len(result) == 1
    r = result[0]
    assert r["datacenter"] == ""
    assert r["encrypted"] == False
    assert r["bytesUsed"] == 0
    assert r["allowedSubnets"] == ""
    assert r["snapshotSizeBytes"] == 0
    assert r["replicationStatus"] == ""
```

- [x] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_classic_collectors.py::test_collect_file_storage tests/test_classic_collectors.py::test_collect_file_storage_missing_new_fields -v`
Expected: FAIL — `KeyError` for missing fields

- [x] **Step 3: Expand the file storage object mask**

In `src/cloud_harvester/collectors/classic/file_storage.py`, replace the OBJECT_MASK:

```python
OBJECT_MASK = (
    "mask[id,username,capacityGb,iops,storageType,storageTierLevel,"
    "serviceResourceBackendIpAddress,fileNetworkMountAddress,"
    "bytesUsed,hasEncryptionAtRest,"
    "serviceResource.datacenter.name,"
    "parentVolume.snapshotSizeBytes,"
    "replicationStatus,"
    "allowedVirtualGuests[id,hostname],allowedHardware[id,hostname],"
    "allowedSubnets[id,networkIdentifier,cidr],"
    "snapshotCapacityGb,"
    "replicationPartners[id,username,"
    "serviceResourceBackendIpAddress,"
    "serviceResource.datacenter.name,"
    "replicationSchedule.type.keyname],"
    "billingItem[recurringFee],createDate,notes]"
)
```

- [x] **Step 4: Update the results dict with new fields**

In `src/cloud_harvester/collectors/classic/file_storage.py`, replace the replication formatting and `results.append(...)`:

```python
        # Format replication partners (enriched with datacenter and schedule)
        repl_parts = []
        for r in item.get("replicationPartners", []):
            r_dc = r.get("serviceResource", {}).get("datacenter", {}).get("name", "")
            r_sched = r.get("replicationSchedule", {}).get("type", {}).get("keyname", "")
            repl_parts.append(
                f"{r.get('id')}:{r.get('username', '')}:{r_dc}:{r_sched}"
            )
        repl_partners = ", ".join(repl_parts)

        # Format allowed subnets
        allowed_subnets = ", ".join(
            f"{s.get('networkIdentifier', '')}/{s.get('cidr', '')}"
            for s in item.get("allowedSubnets", [])
        )

        results.append({
            "id": item.get("id"),
            "username": item.get("username", ""),
            "capacityGb": item.get("capacityGb", 0),
            "iops": item.get("iops", ""),
            "storageType": storage_type_str,
            "storageTierLevel": item.get("storageTierLevel", ""),
            "targetIp": item.get("serviceResourceBackendIpAddress", ""),
            "mountAddress": item.get("fileNetworkMountAddress", ""),
            "datacenter": item.get("serviceResource", {}).get("datacenter", {}).get("name", ""),
            "encrypted": bool(item.get("hasEncryptionAtRest", False)),
            "bytesUsed": item.get("bytesUsed", 0) or 0,
            "snapshotCapacityGb": item.get("snapshotCapacityGb", 0),
            "snapshotSizeBytes": item.get("parentVolume", {}).get("snapshotSizeBytes", 0) or 0,
            "replicationStatus": item.get("replicationStatus", "") or "",
            "recurringFee": billing.get("recurringFee", "") if billing else "",
            "createDate": item.get("createDate", ""),
            "notes": item.get("notes", "") or "",
            "allowedVirtualGuests": allowed_vsis,
            "allowedHardware": allowed_hw,
            "allowedSubnets": allowed_subnets,
            "replicationPartners": repl_partners,
        })
```

- [x] **Step 5: Remove the unused `safe_string` import**

In `src/cloud_harvester/collectors/classic/file_storage.py`, line 2, remove:

```python
from cloud_harvester.utils.formatting import safe_string
```

The `safe_string` function was only used for the old replication formatting. The new code uses explicit formatting instead.

- [x] **Step 6: Update the file storage schema**

In `src/cloud_harvester/schema.py`, replace the fileStorage columns list (lines 219-234):

```python
        columns=[
            ColumnDef("ID", "id", "number"),
            ColumnDef("Username", "username"),
            ColumnDef("Capacity (GB)", "capacityGb", "number"),
            ColumnDef("IOPS", "iops"),
            ColumnDef("Storage Type", "storageType"),
            ColumnDef("Tier", "storageTierLevel"),
            ColumnDef("Target IP", "targetIp"),
            ColumnDef("Mount Address", "mountAddress"),
            ColumnDef("Datacenter", "datacenter"),
            ColumnDef("Encrypted", "encrypted", "boolean"),
            ColumnDef("Bytes Used", "bytesUsed", "number"),
            ColumnDef("Snapshot (GB)", "snapshotCapacityGb", "number"),
            ColumnDef("Snapshot Used (Bytes)", "snapshotSizeBytes", "number"),
            ColumnDef("Replication Status", "replicationStatus"),
            ColumnDef("Classic Monthly Fee", "recurringFee", "currency"),
            ColumnDef("Create Date", "createDate", "date"),
            ColumnDef("Notes", "notes"),
            ColumnDef("Allowed VSIs", "allowedVirtualGuests"),
            ColumnDef("Allowed Hardware", "allowedHardware"),
            ColumnDef("Allowed Subnets", "allowedSubnets"),
            ColumnDef("Replication Partners", "replicationPartners"),
        ],
```

- [x] **Step 7: Run tests to verify they pass**

Run: `pytest tests/test_classic_collectors.py -v`
Expected: All tests PASS

- [x] **Step 8: Commit**

```bash
git add src/cloud_harvester/collectors/classic/file_storage.py src/cloud_harvester/schema.py tests/test_classic_collectors.py
git commit -m "feat: add datacenter, encrypted, bytesUsed, subnets, snapshot, replication fields to file storage collector"
```

---

### Task 3: VSI Collector — storage breakdown fields

**Files:**
- Modify: `src/cloud_harvester/collectors/classic/virtual_servers.py:5-14` (OBJECT_MASK)
- Modify: `src/cloud_harvester/collectors/classic/virtual_servers.py:54-58` (disk calculation)
- Modify: `src/cloud_harvester/collectors/classic/virtual_servers.py:72-99` (results dict)
- Modify: `src/cloud_harvester/schema.py:26-57` (virtualServers schema)
- Test: `tests/test_classic_collectors.py`

- [x] **Step 1: Write the failing test for VSI storage breakdown**

Add to `tests/test_classic_collectors.py`:

```python
def test_collect_virtual_servers_storage_breakdown():
    mock_client = MagicMock()
    mock_client.__getitem__ = MagicMock(return_value=MagicMock())
    mock_account = mock_client["SoftLayer_Account"]
    mock_account.getVirtualGuests.return_value = [
        {
            "id": 154195996,
            "hostname": "virtualserver01",
            "domain": "ibmcloud.private",
            "fullyQualifiedDomainName": "virtualserver01.ibmcloud.private",
            "primaryIpAddress": "10.0.0.1",
            "primaryBackendIpAddress": "10.0.0.2",
            "maxCpu": 2,
            "maxMemory": 4096,
            "startCpus": 2,
            "status": {"keyName": "ACTIVE"},
            "powerState": {"keyName": "RUNNING"},
            "datacenter": {"name": "dal13"},
            "operatingSystem": {"softwareDescription": {"name": "Ubuntu", "version": "24.04"}},
            "hourlyBillingFlag": False,
            "createDate": "2025-11-06T00:00:00",
            "modifyDate": "2025-11-07T00:00:00",
            "billingItem": {"recurringFee": "50.00"},
            "networkVlans": [],
            "tagReferences": [],
            "notes": "",
            "privateNetworkOnlyFlag": False,
            "localDiskFlag": True,
            "dedicatedAccountHostOnlyFlag": False,
            "placementGroupId": None,
            "blockDevices": [
                {
                    "bootableFlag": 1,
                    "device": "0",
                    "diskImage": {"capacity": 100, "description": "virtualserver01.ibmcloud.private", "localDiskFlag": True},
                },
                {
                    "bootableFlag": 0,
                    "device": "1",
                    "diskImage": {"capacity": 2, "description": "154195996-SWAP", "localDiskFlag": True},
                },
                {
                    "bootableFlag": 0,
                    "device": "2",
                    "diskImage": {"capacity": 100, "description": "virtualserver01 - Disk 2", "localDiskFlag": True},
                },
                {
                    "bootableFlag": 0,
                    "device": "4",
                    "diskImage": {"capacity": 10, "description": "virtualserver01 - Disk 3", "localDiskFlag": False},
                },
                {
                    "bootableFlag": 0,
                    "device": "7",
                    "diskImage": {"capacity": 64, "description": "virtualserver01 - Metadata", "localDiskFlag": True},
                },
            ],
            "allowedNetworkStorage": [
                {"id": 723195182, "nasType": "ISCSI", "capacityGb": 20, "username": "IBM02SEL1041833-909"},
                {"id": 721245700, "nasType": "NAS", "capacityGb": 20, "username": "IBM02SEV1041833_935"},
            ],
        }
    ]

    with patch("cloud_harvester.collectors.classic.virtual_servers._create_sl_client", return_value=mock_client):
        result = collect_virtual_servers("test-key", "token", [])

    assert len(result) == 1
    r = result[0]
    # Existing field unchanged
    assert r["diskGb"] == 276  # 100+2+100+10+64 = total of all block devices
    # New storage breakdown fields
    assert r["localStorageGb"] == 200  # 100 (boot) + 100 (Disk 2), excludes swap and metadata
    assert r["portableStorageGb"] == 10  # Disk 3 (localDiskFlag=False)
    assert "virtualserver01 - Disk 3 (10 GB)" in r["portableStorageDetails"]
    assert "0:virtualserver01.ibmcloud.private:100:local" in r["blockDeviceDetails"]
    assert "4:virtualserver01 - Disk 3:10:portable" in r["blockDeviceDetails"]
    assert r["attachedBlockStorageGb"] == 20
    assert r["attachedFileStorageGb"] == 20
    assert r["volumeCount"] == 2


def test_collect_virtual_servers_no_storage_attachments():
    """VSI with no network storage and only local disks."""
    mock_client = MagicMock()
    mock_client.__getitem__ = MagicMock(return_value=MagicMock())
    mock_account = mock_client["SoftLayer_Account"]
    mock_account.getVirtualGuests.return_value = [
        {
            "id": 999,
            "hostname": "simple-vm",
            "domain": "test.com",
            "fullyQualifiedDomainName": "simple-vm.test.com",
            "datacenter": {"name": "dal13"},
            "status": {},
            "powerState": {},
            "operatingSystem": {},
            "billingItem": {},
            "networkVlans": [],
            "blockDevices": [
                {
                    "bootableFlag": 1,
                    "device": "0",
                    "diskImage": {"capacity": 25, "description": "simple-vm", "localDiskFlag": True},
                },
            ],
            "tagReferences": [],
        }
    ]

    with patch("cloud_harvester.collectors.classic.virtual_servers._create_sl_client", return_value=mock_client):
        result = collect_virtual_servers("test-key", "token", [])

    assert len(result) == 1
    r = result[0]
    assert r["localStorageGb"] == 25
    assert r["portableStorageGb"] == 0
    assert r["portableStorageDetails"] == ""
    assert r["attachedBlockStorageGb"] == 0
    assert r["attachedFileStorageGb"] == 0
    assert r["volumeCount"] == 0
```

- [x] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_classic_collectors.py::test_collect_virtual_servers_storage_breakdown tests/test_classic_collectors.py::test_collect_virtual_servers_no_storage_attachments -v`
Expected: FAIL — `KeyError` for `localStorageGb` etc.

- [x] **Step 3: Expand the VSI object mask**

In `src/cloud_harvester/collectors/classic/virtual_servers.py`, replace the OBJECT_MASK:

```python
OBJECT_MASK = (
    "mask[id,hostname,domain,fullyQualifiedDomainName,primaryIpAddress,"
    "primaryBackendIpAddress,maxCpu,maxMemory,startCpus,status,powerState,"
    "datacenter,operatingSystem[softwareDescription],hourlyBillingFlag,"
    "createDate,modifyDate,billingItem[recurringFee,hourlyRecurringFee,"
    "children[categoryCode,hourlyRecurringFee],orderItem],"
    "networkVlans[id,vlanNumber,name,networkSpace],"
    "blockDevices[bootableFlag,device,"
    "diskImage[capacity,units,localDiskFlag,description]],"
    "allowedNetworkStorage[id,nasType,capacityGb,username],"
    "tagReferences[tag],notes,"
    "dedicatedAccountHostOnlyFlag,placementGroupId,privateNetworkOnlyFlag,"
    "localDiskFlag]"
)
```

- [x] **Step 4: Add storage breakdown logic and new fields to results**

In `src/cloud_harvester/collectors/classic/virtual_servers.py`, replace the disk calculation block (line 54-58) and add new logic before the `results.append()`. Then add the new fields to the results dict:

```python
        # Calculate disk totals and breakdowns
        block_devices = vsi.get("blockDevices", [])
        disk_gb = sum(
            bd.get("diskImage", {}).get("capacity", 0) or 0
            for bd in block_devices
        )

        local_gb = 0
        portable_gb = 0
        portable_details = []
        device_details = []
        for bd in block_devices:
            di = bd.get("diskImage", {})
            cap = di.get("capacity", 0) or 0
            desc = di.get("description", "") or ""
            is_local = di.get("localDiskFlag", True)
            device_num = bd.get("device", "")
            is_swap = "swap" in desc.lower()
            is_metadata = "metadata" in desc.lower()

            storage_label = "local" if is_local else "portable"
            device_details.append(f"{device_num}:{desc}:{cap}:{storage_label}")

            if is_swap or is_metadata:
                continue
            if is_local:
                local_gb += cap
            else:
                portable_gb += cap
                portable_details.append(f"{desc} ({cap} GB)")

        # Attached network storage
        net_storage = vsi.get("allowedNetworkStorage", [])
        attached_block_gb = sum(
            s.get("capacityGb", 0) or 0
            for s in net_storage if s.get("nasType") == "ISCSI"
        )
        attached_file_gb = sum(
            s.get("capacityGb", 0) or 0
            for s in net_storage if s.get("nasType") == "NAS"
        )
```

Then update the `results.append({...})` to include the new fields after the existing ones:

```python
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
            "localStorageGb": local_gb,
            "portableStorageGb": portable_gb,
            "portableStorageDetails": ", ".join(portable_details),
            "blockDeviceDetails": ", ".join(device_details),
            "attachedBlockStorageGb": attached_block_gb,
            "attachedFileStorageGb": attached_file_gb,
            "volumeCount": len(net_storage),
        })
```

- [x] **Step 5: Update the virtualServers schema**

In `src/cloud_harvester/schema.py`, replace the virtualServers columns list (lines 30-57):

```python
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
            ColumnDef("Local Storage (GB)", "localStorageGb", "number"),
            ColumnDef("Portable Storage (GB)", "portableStorageGb", "number"),
            ColumnDef("Portable Storage Details", "portableStorageDetails"),
            ColumnDef("Block Device Details", "blockDeviceDetails"),
            ColumnDef("Attached Block Storage (GB)", "attachedBlockStorageGb", "number"),
            ColumnDef("Attached File Storage (GB)", "attachedFileStorageGb", "number"),
            ColumnDef("Volume Count", "volumeCount", "number"),
        ],
```

- [x] **Step 6: Update existing VSI test mock data**

The existing `test_collect_virtual_servers` test mock data at line 31 needs `localDiskFlag` and `description` added to blockDevices, and `allowedNetworkStorage` added. Update the mock data:

```python
            "blockDevices": [
                {
                    "bootableFlag": 1,
                    "device": "0",
                    "diskImage": {"capacity": 100, "description": "web01.test.com", "localDiskFlag": True},
                },
            ],
```

And add `"allowedNetworkStorage": []` to the mock dict. Then add assertions for the new fields:

```python
    assert result[0]["localStorageGb"] == 100
    assert result[0]["portableStorageGb"] == 0
    assert result[0]["attachedBlockStorageGb"] == 0
    assert result[0]["attachedFileStorageGb"] == 0
    assert result[0]["volumeCount"] == 0
```

Also update the `test_collect_virtual_servers_region_filter` mock data for both VSIs: add `"allowedNetworkStorage": []` and update blockDevices to include the new sub-fields (or leave blockDevices as `[]`).

- [x] **Step 7: Run all tests to verify they pass**

Run: `pytest tests/test_classic_collectors.py -v`
Expected: All tests PASS

- [x] **Step 8: Commit**

```bash
git add src/cloud_harvester/collectors/classic/virtual_servers.py src/cloud_harvester/schema.py tests/test_classic_collectors.py
git commit -m "feat: add local/portable storage breakdown and network storage fields to VSI collector"
```

---

### Task 4: Bare Metal Collector — storage enrichment

**Files:**
- Modify: `src/cloud_harvester/collectors/classic/bare_metal.py:6-14` (OBJECT_MASK)
- Modify: `src/cloud_harvester/collectors/classic/bare_metal.py:46-49` (hardDrives formatting)
- Modify: `src/cloud_harvester/collectors/classic/bare_metal.py:83-105` (results dict)
- Modify: `src/cloud_harvester/schema.py:59-85` (bareMetal schema)
- Test: `tests/test_classic_collectors.py`

- [x] **Step 1: Write the failing test for bare metal storage enrichment**

Add to `tests/test_classic_collectors.py`:

```python
def test_collect_bare_metal_storage_enrichment():
    mock_client = MagicMock()
    mock_client.__getitem__ = MagicMock(return_value=MagicMock())
    mock_account = mock_client["SoftLayer_Account"]
    mock_account.getHardware.return_value = [
        {
            "id": 3481996,
            "hostname": "bm-storage01",
            "domain": "test.com",
            "fullyQualifiedDomainName": "bm-storage01.test.com",
            "manufacturerSerialNumber": "SN789",
            "primaryIpAddress": "10.0.1.1",
            "primaryBackendIpAddress": "10.0.1.2",
            "processorPhysicalCoreAmount": 16,
            "memoryCapacity": 128,
            "datacenter": {"name": "dal13"},
            "operatingSystem": {"softwareDescription": {"name": "RHEL", "version": "9"}},
            "billingItem": {"recurringFee": "800.00"},
            "provisionDate": "2025-06-01T00:00:00",
            "powerSupplyCount": 2,
            "networkGatewayMemberFlag": False,
            "networkVlans": [],
            "tagReferences": [],
            "notes": "",
            "hardDrives": [
                {
                    "capacity": 480,
                    "hardwareComponentModel": {
                        "capacity": "480",
                        "hardwareGenericComponentModel": {
                            "hardwareComponentType": {"keyName": "SSD"}
                        }
                    }
                },
                {
                    "capacity": 960,
                    "hardwareComponentModel": {
                        "capacity": "960",
                        "hardwareGenericComponentModel": {
                            "hardwareComponentType": {"keyName": "HDD"}
                        }
                    }
                },
            ],
            "networkComponents": [],
            "allowedNetworkStorage": [
                {"id": 100, "nasType": "ISCSI", "capacityGb": 500, "username": "block-vol-01"},
                {"id": 200, "nasType": "ISCSI", "capacityGb": 1000, "username": "block-vol-02"},
                {"id": 300, "nasType": "NAS", "capacityGb": 250, "username": "file-vol-01"},
            ],
        }
    ]

    with patch("cloud_harvester.collectors.classic.bare_metal._create_sl_client", return_value=mock_client):
        result = collect_bare_metal("test-key", "token", [])

    assert len(result) == 1
    r = result[0]
    assert r["hardDrives"] == "480, 960"
    assert r["hardDriveDetails"] == "480 GB (SSD), 960 GB (HDD)"
    assert r["attachedBlockStorageGb"] == 1500
    assert r["attachedFileStorageGb"] == 250
    assert r["volumeCount"] == 3


def test_collect_bare_metal_no_storage_attachments():
    """Bare metal with no network storage and drives with missing type info."""
    mock_client = MagicMock()
    mock_client.__getitem__ = MagicMock(return_value=MagicMock())
    mock_account = mock_client["SoftLayer_Account"]
    mock_account.getHardware.return_value = [
        {
            "id": 555,
            "hostname": "bm-simple",
            "domain": "test.com",
            "fullyQualifiedDomainName": "bm-simple.test.com",
            "manufacturerSerialNumber": "SN000",
            "primaryIpAddress": "10.0.2.1",
            "primaryBackendIpAddress": "10.0.2.2",
            "processorPhysicalCoreAmount": 8,
            "memoryCapacity": 32,
            "datacenter": {"name": "wdc04"},
            "operatingSystem": {},
            "billingItem": {},
            "provisionDate": "2025-01-01T00:00:00",
            "powerSupplyCount": 1,
            "networkGatewayMemberFlag": False,
            "networkVlans": [],
            "tagReferences": [],
            "notes": "",
            "hardDrives": [
                {"capacity": 500},
            ],
            "networkComponents": [],
        }
    ]

    with patch("cloud_harvester.collectors.classic.bare_metal._create_sl_client", return_value=mock_client):
        result = collect_bare_metal("test-key", "token", [])

    assert len(result) == 1
    r = result[0]
    assert r["hardDrives"] == "500"
    assert r["hardDriveDetails"] == "500 GB (Unknown)"
    assert r["attachedBlockStorageGb"] == 0
    assert r["attachedFileStorageGb"] == 0
    assert r["volumeCount"] == 0
```

- [x] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_classic_collectors.py::test_collect_bare_metal_storage_enrichment tests/test_classic_collectors.py::test_collect_bare_metal_no_storage_attachments -v`
Expected: FAIL — `KeyError` for `hardDriveDetails`, `attachedBlockStorageGb` etc.

- [x] **Step 3: Expand the bare metal object mask**

In `src/cloud_harvester/collectors/classic/bare_metal.py`, replace the OBJECT_MASK:

```python
OBJECT_MASK = (
    "mask[id,hostname,domain,fullyQualifiedDomainName,manufacturerSerialNumber,"
    "primaryIpAddress,primaryBackendIpAddress,processorPhysicalCoreAmount,"
    "memoryCapacity,hardDrives[capacity,hardwareComponentModel"
    "[capacity,hardwareGenericComponentModel[hardwareComponentType[keyName]]]],"
    "datacenter,operatingSystem[softwareDescription],"
    "networkComponents[primaryIpAddress,port,speed,status,macAddress],"
    "billingItem[recurringFee],provisionDate,powerSupplyCount,"
    "networkGatewayMemberFlag,networkVlans,tagReferences,notes,"
    "allowedNetworkStorage[id,nasType,capacityGb,username]]"
)
```

- [x] **Step 4: Add hardDriveDetails formatting and network storage fields**

In `src/cloud_harvester/collectors/classic/bare_metal.py`, replace the hard drives formatting block (lines 46-49) and add network storage logic before `results.append()`:

```python
        # Format hard drives (simple list)
        drives = []
        drive_details = []
        for hd in srv.get("hardDrives", []):
            cap = hd.get("capacity", "")
            drives.append(str(cap))
            drive_type = (
                hd.get("hardwareComponentModel", {})
                .get("hardwareGenericComponentModel", {})
                .get("hardwareComponentType", {})
                .get("keyName", "Unknown")
            ) or "Unknown"
            drive_details.append(f"{cap} GB ({drive_type})")
        hard_drives = ", ".join(drives)
        hard_drive_details = ", ".join(drive_details)

        # Attached network storage
        net_storage = srv.get("allowedNetworkStorage", [])
        attached_block_gb = sum(
            s.get("capacityGb", 0) or 0
            for s in net_storage if s.get("nasType") == "ISCSI"
        )
        attached_file_gb = sum(
            s.get("capacityGb", 0) or 0
            for s in net_storage if s.get("nasType") == "NAS"
        )
```

Then add the new fields to `results.append({...})`:

```python
            "hardDrives": hard_drives,
            "hardDriveDetails": hard_drive_details,
            "attachedBlockStorageGb": attached_block_gb,
            "attachedFileStorageGb": attached_file_gb,
            "volumeCount": len(net_storage),
```

- [x] **Step 5: Update the bareMetal schema**

In `src/cloud_harvester/schema.py`, replace the bareMetal columns list (lines 63-85):

```python
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
            ColumnDef("Drive Details", "hardDriveDetails"),
            ColumnDef("Attached Block Storage (GB)", "attachedBlockStorageGb", "number"),
            ColumnDef("Attached File Storage (GB)", "attachedFileStorageGb", "number"),
            ColumnDef("Volume Count", "volumeCount", "number"),
            ColumnDef("Network Components", "networkComponents"),
            ColumnDef("VLANs", "networkVlans"),
            ColumnDef("Tags", "tags"),
        ],
```

- [x] **Step 6: Update existing bare metal test mock data**

Update `test_collect_bare_metal` (line 126-128): add `"allowedNetworkStorage": []` to the mock dict and add assertions:

```python
    assert result[0]["hardDriveDetails"] == ""
    assert result[0]["attachedBlockStorageGb"] == 0
    assert result[0]["attachedFileStorageGb"] == 0
    assert result[0]["volumeCount"] == 0
```

Update `test_collect_bare_metal_vmware_detection` (line 170): add `"allowedNetworkStorage": []` to the mock dict.

- [x] **Step 7: Run all tests to verify they pass**

Run: `pytest tests/test_classic_collectors.py -v`
Expected: All tests PASS

- [x] **Step 8: Commit**

```bash
git add src/cloud_harvester/collectors/classic/bare_metal.py src/cloud_harvester/schema.py tests/test_classic_collectors.py
git commit -m "feat: add drive details and attached network storage fields to bare metal collector"
```

---

### Task 5: Run full test suite and lint

**Files:**
- No new files

- [x] **Step 1: Run full test suite**

Run: `pytest tests/ -v --tb=short`
Expected: All tests PASS

- [x] **Step 2: Run linter**

Run: `ruff check src/ tests/`
Expected: No errors

- [x] **Step 3: Fix any lint issues**

Run: `ruff check --fix src/ tests/`
Then re-run: `ruff check src/ tests/`
Expected: Clean

- [x] **Step 4: Commit any lint fixes**

```bash
git add -u
git commit -m "fix: resolve lint issues from storage discovery changes"
```

(Skip this step if there were no lint issues.)

---

### Task 6: Write analyser changelist

**Files:**
- Create: `docs/analyser-storage-changelist.md`

- [x] **Step 1: Create the changelist document**

Create `docs/analyser-storage-changelist.md`:

```markdown
# Storage Discovery Changes — classic_analyser Integration Guide

Changes made to cloud-harvester XLSX output that classic_analyser needs to incorporate.

## vBlockStorage worksheet — new columns

| Column Header | Field Key | Data Type | Example Value |
|---|---|---|---|
| Datacenter | `datacenter` | string | `dal13` |
| Encrypted | `encrypted` | boolean | `True` / `False` |
| Snapshot Used (Bytes) | `snapshotSizeBytes` | number | `163840` |
| Replication Status | `replicationStatus` | string | `REPLICATION_PROVISIONING_COMPLETED` |
| Allowed Subnets | `allowedSubnets` | string | `10.0.0.0/24, 10.0.1.0/28` |

### Modified columns

| Column | Change | Old Format | New Format |
|---|---|---|---|
| Replication Partners | Enriched format | `id:username` | `id:username:datacenter:schedule` |

## vFileStorage worksheet — new columns

| Column Header | Field Key | Data Type | Example Value |
|---|---|---|---|
| Datacenter | `datacenter` | string | `dal13` |
| Encrypted | `encrypted` | boolean | `True` / `False` |
| Bytes Used | `bytesUsed` | number | `393216000` |
| Snapshot Used (Bytes) | `snapshotSizeBytes` | number | `159744` |
| Replication Status | `replicationStatus` | string | `REPLICATION_PROVISIONING_COMPLETED` |
| Allowed Subnets | `allowedSubnets` | string | `10.0.5.0/24` |

### Modified columns

| Column | Change | Old Format | New Format |
|---|---|---|---|
| Replication Partners | Enriched format | `id:username` | `id:username:datacenter:schedule` |

## vVirtualServers worksheet — new columns

| Column Header | Field Key | Data Type | Example Value |
|---|---|---|---|
| Local Storage (GB) | `localStorageGb` | number | `200` |
| Portable Storage (GB) | `portableStorageGb` | number | `10` |
| Portable Storage Details | `portableStorageDetails` | string | `virtualserver01 - Disk 3 (10 GB)` |
| Block Device Details | `blockDeviceDetails` | string | `0:hostname:100:local, 4:Disk 3:10:portable` |
| Attached Block Storage (GB) | `attachedBlockStorageGb` | number | `20` |
| Attached File Storage (GB) | `attachedFileStorageGb` | number | `20` |
| Volume Count | `volumeCount` | number | `2` |

## vBareMetal worksheet — new columns

| Column Header | Field Key | Data Type | Example Value |
|---|---|---|---|
| Drive Details | `hardDriveDetails` | string | `480 GB (SSD), 960 GB (HDD)` |
| Attached Block Storage (GB) | `attachedBlockStorageGb` | number | `1500` |
| Attached File Storage (GB) | `attachedFileStorageGb` | number | `250` |
| Volume Count | `volumeCount` | number | `3` |

## Notes

- All new fields default to empty string, `0`, or `False` when data is unavailable
- The `replicationPartners` format change is backwards-incompatible — the analyser transform should be updated to parse the new `id:username:datacenter:schedule` format
- `blockDeviceDetails` format: `device_number:description:capacity_gb:local|portable` separated by commas
- Swap disks (description contains "SWAP") and metadata disks (description contains "Metadata") are excluded from `localStorageGb` and `portableStorageGb` but included in the existing `diskGb` total and in `blockDeviceDetails`
```

- [x] **Step 2: Commit**

```bash
git add docs/analyser-storage-changelist.md
git commit -m "docs: add classic_analyser integration guide for new storage fields"
```
