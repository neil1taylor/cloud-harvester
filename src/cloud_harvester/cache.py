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
