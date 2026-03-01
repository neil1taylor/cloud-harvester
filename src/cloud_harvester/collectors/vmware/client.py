"""VMware Solutions API client."""
import requests

VMWARE_API_BASE = "https://api.vmware-solutions.cloud.ibm.com"
VCFAAS_REGIONS = [
    "us-south", "us-east", "eu-de", "eu-gb", "eu-es",
    "eu-fr2", "jp-tok", "jp-osa", "au-syd", "ca-tor", "br-sao",
]


class VMwareClient:
    def __init__(self, token: str):
        self.token = token
        self.headers = {"Authorization": f"Bearer {token}", "Accept": "application/json"}

    def get_vcenter_instances(self) -> list[dict]:
        """Get VCF for Classic instances."""
        url = f"{VMWARE_API_BASE}/v2/vcenters"
        resp = requests.get(url, headers=self.headers, timeout=60)
        if resp.status_code in (403, 404):
            return []
        resp.raise_for_status()
        return resp.json() if isinstance(resp.json(), list) else resp.json().get("vcenters", [])

    def get_vcenter_detail(self, instance_id: str) -> dict:
        """Get VCF for Classic instance detail including clusters."""
        url = f"{VMWARE_API_BASE}/v1/vcenters/{instance_id}"
        resp = requests.get(url, headers=self.headers, timeout=60)
        if resp.status_code in (403, 404):
            return {}
        resp.raise_for_status()
        return resp.json()

    def get_cluster_detail(self, instance_id: str, cluster_id: str) -> dict:
        """Get cluster detail including hosts."""
        url = f"{VMWARE_API_BASE}/v1/vcenters/{instance_id}/clusters/{cluster_id}"
        resp = requests.get(url, headers=self.headers, timeout=60)
        if resp.status_code in (403, 404):
            return {}
        resp.raise_for_status()
        return resp.json()

    def get_cluster_vlans(self, instance_id: str, cluster_id: str) -> list[dict]:
        """Get VLANs for a cluster."""
        url = f"{VMWARE_API_BASE}/v2/vcenters/{instance_id}/clusters/{cluster_id}/vlans"
        resp = requests.get(url, headers=self.headers, timeout=60)
        if resp.status_code in (403, 404):
            return []
        resp.raise_for_status()
        data = resp.json()
        return data if isinstance(data, list) else data.get("vlans", [])

    def get_vcfaas_director_sites(self, region: str) -> list[dict]:
        """Get VCFaaS director sites for a region."""
        url = f"https://api.{region}.vmware.cloud.ibm.com/v1/director_sites"
        resp = requests.get(url, headers=self.headers, timeout=60)
        if resp.status_code in (403, 404):
            return []
        resp.raise_for_status()
        data = resp.json()
        return data if isinstance(data, list) else data.get("director_sites", [])

    def get_vcfaas_pvdcs(self, region: str, site_id: str) -> list[dict]:
        """Get VCFaaS PVDCs for a director site."""
        url = f"https://api.{region}.vmware.cloud.ibm.com/v1/director_sites/{site_id}/pvdcs"
        resp = requests.get(url, headers=self.headers, timeout=60)
        if resp.status_code in (403, 404):
            return []
        resp.raise_for_status()
        data = resp.json()
        return data if isinstance(data, list) else data.get("pvdcs", [])

    def get_vcfaas_clusters(self, region: str, site_id: str, pvdc_id: str) -> list[dict]:
        """Get VCFaaS clusters for a PVDC."""
        url = f"https://api.{region}.vmware.cloud.ibm.com/v1/director_sites/{site_id}/pvdcs/{pvdc_id}/clusters"
        resp = requests.get(url, headers=self.headers, timeout=60)
        if resp.status_code in (403, 404):
            return []
        resp.raise_for_status()
        data = resp.json()
        return data if isinstance(data, list) else data.get("clusters", [])

    def get_vcfaas_vdcs(self, region: str) -> list[dict]:
        """Get VCFaaS virtual data centres for a region."""
        url = f"https://api.{region}.vmware.cloud.ibm.com/v1/vdcs"
        resp = requests.get(url, headers=self.headers, timeout=60)
        if resp.status_code in (403, 404):
            return []
        resp.raise_for_status()
        data = resp.json()
        return data if isinstance(data, list) else data.get("vdcs", [])

    def get_vcfaas_multitenant_sites(self, region: str) -> list[dict]:
        """Get VCFaaS multitenant director sites for a region."""
        url = f"https://api.{region}.vmware.cloud.ibm.com/v1/multitenant_director_sites"
        resp = requests.get(url, headers=self.headers, timeout=60)
        if resp.status_code in (403, 404):
            return []
        resp.raise_for_status()
        data = resp.json()
        return data if isinstance(data, list) else data.get("multitenant_director_sites", [])
