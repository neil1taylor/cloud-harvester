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
