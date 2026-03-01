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
