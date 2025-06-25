from keycloak import KeycloakAdmin
import os
from dotenv import load_dotenv

load_dotenv()

# print("###############")
# print(os.getenv("KEYCLOAK_ADMIN_USER"))
# print(os.getenv("KEYCLOAK_SERVER"))
# print(os.getenv("KEYCLOAK_REALM"))

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
            keys.append({
                "id": cid,
                "enabled": c["enabled"]
            })
    return keys

def revoke_api_key(client_id: str):
    c = kc.get_client_id(client_id)
    if not c:
        return False
    kc.delete_client(c)
    return True
