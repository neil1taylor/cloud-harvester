"""PowerVS API client."""
import requests

POWERVS_REGIONS = {
    "us-south": "us-south",
    "us-east": "us-east",
    "eu-de": "eu-de",
    "eu-gb": "eu-gb",
    "jp-tok": "jp-tok",
    "jp-osa": "jp-osa",
    "au-syd": "au-syd",
    "ca-tor": "ca-tor",
    "br-sao": "br-sao",
    "eu-es": "eu-es",
}

# Zone to region mapping for PowerVS
ZONE_TO_REGION = {
    "dal10": "us-south", "dal12": "us-south", "dal13": "us-south",
    "wdc04": "us-east", "wdc06": "us-east", "wdc07": "us-east",
    "lon04": "eu-gb", "lon06": "eu-gb",
    "fra04": "eu-de", "fra05": "eu-de",
    "tok04": "jp-tok",
    "osa21": "jp-osa",
    "syd04": "au-syd", "syd05": "au-syd",
    "tor01": "ca-tor",
    "sao01": "br-sao", "sao04": "br-sao",
    "mad02": "eu-es", "mad04": "eu-es",
}


class PowerVSClient:
    def __init__(self, token: str, region: str, cloud_instance_id: str):
        self.token = token
        self.region = region
        self.cloud_instance_id = cloud_instance_id
        self.base_url = f"https://{region}.power-iaas.cloud.ibm.com/pcloud/v1/cloud-instances/{cloud_instance_id}"
        self.v1_base = f"https://{region}.power-iaas.cloud.ibm.com/v1"
        self.headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    def get(self, path: str) -> dict:
        """GET request to PowerVS pcloud API."""
        url = f"{self.base_url}/{path}"
        resp = requests.get(url, headers=self.headers, timeout=60)
        if resp.status_code == 403:
            return {}
        resp.raise_for_status()
        return resp.json()

    def get_v1(self, path: str) -> dict:
        """GET request to PowerVS v1 API."""
        url = f"{self.v1_base}/{path}"
        resp = requests.get(url, headers=self.headers, timeout=60)
        if resp.status_code == 403:
            return {}
        resp.raise_for_status()
        return resp.json()
