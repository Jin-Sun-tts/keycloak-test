from keycloak import KeycloakAdmin
import os
from dotenv import load_dotenv

load_dotenv()

kc = KeycloakAdmin(
    server_url=f"{os.getenv('KEYCLOAK_SERVER')}/",
    username=os.getenv("KEYCLOAK_ADMIN_USER"),
    password=os.getenv("KEYCLOAK_ADMIN_PASSWORD"),
    realm_name=os.getenv("KEYCLOAK_REALM"),
    client_id="admin-cli",
    verify=True
)


def create_api_key(name: str, roles: list[str] = None):
    client_id = kc.create_client({
        "clientId": name,
        "serviceAccountsEnabled": True,
        "enabled": True,
        "standardFlowEnabled": False,
        "clientAuthenticatorType": "client-secret",
        "directAccessGrantsEnabled": False
    })

    secret = kc.get_client_secrets(client_id)["value"]
    print("secret:", secret)
    if roles:
        svc_user_id = kc.get_client_service_account_user(client_id)["id"]
        print("user_id:", svc_user_id)
        role_objs = [kc.get_realm_role(r) for r in roles]
        kc.assign_realm_roles(user_id=svc_user_id, roles=role_objs)

    kc.add_mapper_to_client(client_id, {
        "name": "audience-mapper",
        "protocol": "openid-connect",
        "protocolMapper": "oidc-audience-mapper",
        "consentRequired": False,
        "config": {
            "included.client.audience": os.getenv("KEYCLOAK_BACKEND_AUD", "api-backend"),
            "id.token.claim": "true",
            "access.token.claim": "true"
        }
    })

    return {"client_id": name, "client_secret": secret}

def list_api_keys(owner_prefix: str) -> list[dict]:
    clients = kc.get_clients()
    keys = []
    for c in clients:
        cid = c.get("clientId")
        if cid and cid.startswith(owner_prefix + "-"):
            secret = kc.get_client_secrets(c["id"]).get("value")
            keys.append({
                "id": cid,
                "enabled": c["enabled"],
                "secret": secret
            })
    return keys

def revoke_api_key(client_id: str):
    c = kc.get_client_id(client_id)
    if not c:
        return False
    kc.delete_client(c)
    return True

def create_realm_role(role_name: str):
    try:
        return kc.create_realm_role({"name": role_name})
    except:
        return kc.get_realm_role(role_name)

def list_realm_roles():
    return kc.get_realm_roles()

def assign_role_to_user(user_id: str, role_name: str):
    role = kc.get_realm_role(role_name)
    kc.assign_realm_roles(user_id=user_id, roles=[role])


def list_users():
    return kc.get_users()

def create_user(username: str, email: str, password: str):
    user = kc.create_user({
        "username": username,
        "email": email,
        "enabled": True,
        "credentials": [{"type": "password", "value": password, "temporary": False}]
    })
    return user

def get_user_realm_roles(user_id: str) -> list[str]:
    roles = kc.get_realm_roles_of_user(user_id=user_id)
    return [r["name"] for r in roles]
