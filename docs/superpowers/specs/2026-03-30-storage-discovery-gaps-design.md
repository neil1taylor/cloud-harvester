# Storage Discovery Gaps — Design Spec

**Date:** 2026-03-30
**Status:** Implemented
**Reference:** [discovery-storage.md](https://github.ibm.com/cloud-docs-solutions/classic-to-vpc/blob/source/discovery-storage.md)

## Problem

The classic-to-vpc discovery doc defines storage information that should be collected for migration readiness. cloud-harvester has gaps in its block storage, file storage, VSI, and bare metal collectors relative to what the doc specifies. The output XLSX feeds into classic_analyser, which will need to be updated to consume the new fields.

## Approach

Expand existing collectors' SoftLayer object masks and add new fields to schemas. No new collector files are needed. After implementation, produce a changelist for classic_analyser to incorporate.

## Changes by Collector

### 1. Block Storage (`collectors/classic/block_storage.py`)

#### Mask additions

Add to `OBJECT_MASK`:
- `serviceResource.datacenter.name`
- `hasEncryptionAtRest`
- `allowedSubnets[id,networkIdentifier,cidr]`
- `parentVolume.snapshotSizeBytes`
- `replicationStatus`
- `replicationPartners.replicationSchedule.type.keyname`
- `replicationPartners.serviceResource.datacenter.name`

#### New output fields

| Field | Source | Type | Description |
|---|---|---|---|
| `datacenter` | `serviceResource.datacenter.name` | string | Datacenter where volume is provisioned |
| `encrypted` | `hasEncryptionAtRest` | boolean | Whether volume has at-rest encryption |
| `allowedSubnets` | `allowedSubnets` array | string | Formatted as `"networkId/cidr, ..."` |
| `snapshotSizeBytes` | `parentVolume.snapshotSizeBytes` | number | Snapshot space consumed in bytes |
| `replicationStatus` | `replicationStatus` | string | e.g. `REPLICATION_PROVISIONING_COMPLETED` |

#### Modified fields

`replicationPartners` format changes from `id:username` to `id:username:datacenter:schedule` to include replication datacenter and schedule type.

### 2. File Storage (`collectors/classic/file_storage.py`)

#### Mask additions

Same as block storage, plus:
- `bytesUsed`

#### New output fields

All fields from block storage above, plus:

| Field | Source | Type | Description |
|---|---|---|---|
| `bytesUsed` | `bytesUsed` | number | Actual bytes consumed on the volume |

#### Modified fields

Same `replicationPartners` format change as block storage.

### 3. VSI Collector (`collectors/classic/virtual_servers.py`)

#### Mask additions

Expand existing `blockDevices` mask:
- `blockDevices.diskImage.localDiskFlag`
- `blockDevices.diskImage.description`
- `blockDevices.bootableFlag`

Add new top-level mask:
- `allowedNetworkStorage[id,nasType,capacityGb,username]`

#### New output fields

| Field | Source | Type | Description |
|---|---|---|---|
| `localStorageGb` | Sum of `blockDevices` where `diskImage.localDiskFlag=true`, excluding swap and metadata | number | Total local disk capacity |
| `portableStorageGb` | Sum of `blockDevices` where `diskImage.localDiskFlag=false`, excluding swap and metadata | number | Total portable SAN capacity |
| `portableStorageDetails` | Portable disk descriptions | string | Formatted as `"description (capacityGb GB), ..."` |
| `blockDeviceDetails` | All block devices | string | Formatted as `"device:description:capacityGb:local/portable, ..."` |
| `attachedBlockStorageGb` | Sum `capacityGb` from `allowedNetworkStorage` where `nasType=ISCSI` | number | Total attached iSCSI block storage |
| `attachedFileStorageGb` | Sum `capacityGb` from `allowedNetworkStorage` where `nasType=NAS` | number | Total attached NFS file storage |
| `volumeCount` | Count of `allowedNetworkStorage` entries | number | Number of attached storage volumes |

#### Swap/metadata exclusion logic

- **Swap:** `description` contains "SWAP" (case-insensitive)
- **Metadata:** `description` contains "Metadata" (case-insensitive)

The existing `diskGb` field remains unchanged for backwards compatibility (total of all block devices).

### 4. Bare Metal Collector (`collectors/classic/bare_metal.py`)

#### Mask additions

Add:
- `allowedNetworkStorage[id,nasType,capacityGb,username]`

Expand existing `hardDrives` mask:
- `hardDrives.hardwareComponentModel.capacity`
- `hardDrives.hardwareComponentModel.hardwareGenericComponentModel.hardwareComponentType.keyName`

The existing bare metal mask already traverses `hardDrives.hardwareComponentModel.hardwareGenericComponentModel.hardwareComponentType` — adding `.keyName` extends the same path. If `keyName` is absent on some drives, default to `"Unknown"`.

#### New output fields

| Field | Source | Type | Description |
|---|---|---|---|
| `attachedBlockStorageGb` | Sum `capacityGb` from `allowedNetworkStorage` where `nasType=ISCSI` | number | Total attached iSCSI block storage |
| `attachedFileStorageGb` | Sum `capacityGb` from `allowedNetworkStorage` where `nasType=NAS` | number | Total attached NFS file storage |
| `volumeCount` | Count of `allowedNetworkStorage` entries | number | Number of attached storage volumes |
| `hardDriveDetails` | Enhanced drive formatting | string | Formatted as `"capacityGB (driveType), ..."` using component type keyName |

### 5. Schema Updates (`schema.py`)

Add `ColumnDef` entries for every new field listed above to the corresponding `ResourceSchema`:

- **`CLASSIC_SCHEMAS["blockStorage"]`** — add `datacenter`, `encrypted`, `allowedSubnets`, `snapshotSizeBytes`, `replicationStatus`
- **`CLASSIC_SCHEMAS["fileStorage"]`** — add `datacenter`, `encrypted`, `bytesUsed`, `allowedSubnets`, `snapshotSizeBytes`, `replicationStatus`
- **`CLASSIC_SCHEMAS["virtualServers"]`** — add `localStorageGb`, `portableStorageGb`, `portableStorageDetails`, `blockDeviceDetails`, `attachedBlockStorageGb`, `attachedFileStorageGb`, `volumeCount`
- **`CLASSIC_SCHEMAS["bareMetal"]`** — add `attachedBlockStorageGb`, `attachedFileStorageGb`, `volumeCount`, `hardDriveDetails`

Column data types:
- `number` for all GB/byte/count fields
- `boolean` for `encrypted`
- `string` for all formatted detail fields
- `string` for `datacenter`, `replicationStatus`

### 6. Test Updates

Update existing test mocks to include the new mask fields in their mock API responses. Each collector's test file needs mock data expanded to cover:
- New fields return correct values
- Missing/null new fields default gracefully (empty string, 0, or False)
- Swap/metadata exclusion logic in VSI collector

### 7. Deliverable for classic_analyser

After implementation, produce `docs/analyser-storage-changelist.md` listing:
- Every new field added per worksheet
- Data type and format
- Example values
- Which fields are new vs modified (replicationPartners format change)

This gives the classic_analyser team a clear integration spec.

## Out of Scope

- Collecting individual snapshot records (id, created date, size) as separate rows — the discovery doc shows these as drill-down queries, not bulk collection
- In-VSI discovery commands (`lsblk`, `iscsiadm`, `df -h`) — these require SSH access to running instances, which is outside cloud-harvester's API-only approach
- Object storage changes — already aligned
- VPC/PowerVS storage changes — not covered by this discovery doc
