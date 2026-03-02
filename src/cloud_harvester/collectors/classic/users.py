"""Collect IBM Cloud Classic Users."""
import SoftLayer

OBJECT_MASK = (
    "mask[id,username,email,firstName,lastName,"
    "createDate,statusDate,userStatus,roles,permissions]"
)


def _create_sl_client(api_key):
    return SoftLayer.create_client_from_env(username='apikey', api_key=api_key)


def collect_users(api_key: str, token: str, regions: list[str]) -> list[dict]:
    """Collect all users."""
    client = _create_sl_client(api_key)
    account = client["SoftLayer_Account"]

    try:
        users = account.getUsers(mask=OBJECT_MASK)
    except Exception:
        return []

    results = []
    for user in users:
        # Format user status
        status = user.get("userStatus", {})
        if isinstance(status, dict):
            status_str = status.get("name", "")
        else:
            status_str = str(status) if status else ""

        # Format roles
        roles = user.get("roles", [])
        if isinstance(roles, list):
            roles_str = ", ".join(
                r.get("name", "") if isinstance(r, dict) else str(r)
                for r in roles
            )
        else:
            roles_str = str(roles) if roles else ""

        # Format permissions
        perms = user.get("permissions", [])
        if isinstance(perms, list):
            perms_str = ", ".join(
                p.get("keyName", "") if isinstance(p, dict) else str(p)
                for p in perms
            )
        else:
            perms_str = str(perms) if perms else ""

        results.append({
            "id": user.get("id"),
            "username": user.get("username", ""),
            "email": user.get("email", ""),
            "firstName": user.get("firstName", ""),
            "lastName": user.get("lastName", ""),
            "createDate": user.get("createDate", ""),
            "statusDate": user.get("statusDate", ""),
            "userStatus": status_str,
            "roles": roles_str,
            "permissions": perms_str,
        })

    return results
