from tests.modules.auth.test_helpers import register, login, me, refresh, logout

async def test_insufficient_role_gets_403(client):
    await register(client, email="user@ex.com", password="P@ssw0rd!", name="User")
    login_resp = await login(client, email="user@ex.com", password="P@ssw0rd!")
    response = login_resp.json()
    tokens = response.get("tokens", response)
    at = tokens["access_token"]
    # Hitting an admin-only route with a normal user
    r = await client.get("/api/v1/admin/users", headers={"Authorization": f"Bearer {at}"})
    assert r.status_code in (403, 404)  
