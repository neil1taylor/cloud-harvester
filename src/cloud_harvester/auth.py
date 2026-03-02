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
    account_id = api_key_details.get("account_id", "")

    # Try to get account details from the Account Management API
    token = authenticate(api_key)
    account_name = account_id
    owner_email = ""
    owner = ""

    try:
        response = requests.get(
            f"https://accounts.cloud.ibm.com/coe/v2/accounts/{account_id}",
            headers={"Authorization": f"Bearer {token}"},
            timeout=30,
        )
        if response.status_code == 200:
            acct = response.json()
            entity = acct.get("entity", {})
            account_name = entity.get("name", account_id)
            owner_email = entity.get("owner_email", "")
            owner = entity.get("owner", owner_email)
    except Exception:
        pass  # Fall back to API key details

    return {
        "account_id": account_id,
        "name": account_name,
        "owner_email": owner_email,
        "owner": owner,
    }
