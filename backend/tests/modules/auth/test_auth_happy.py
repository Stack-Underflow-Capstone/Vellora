import time
from tests.modules.auth.test_helpers import register, login, me, refresh, logout

async def test_register_login_me_refresh_logout_flow(client):
    # Register
    r = await register(client)
    assert r.status_code in (200, 201)
    # Login
    r = await login(client)
    assert r.status_code == 200
    response = r.json()
    tokens = response.get("tokens", response)  # Handle both nested and flat structure
    assert "access_token" in tokens and "refresh_token" in tokens
    at1 = tokens["access_token"]
    rt1 = tokens["refresh_token"]

    # Access protected
    r = await me(client, at1)
    assert r.status_code == 200
    profile = r.json()
    assert profile["email"] == "alice@example.com"

    # Refresh rotation
    import time
    time.sleep(1)  # Wait 1 second to ensure different timestamps
    r = await refresh(client, rt1)
    assert r.status_code == 200
    response2 = r.json()
    tokens2 = response2.get("tokens", response2)
    assert tokens2["access_token"] != at1
    assert tokens2["refresh_token"] != rt1
    at2 = tokens2["access_token"]
    rt2 = tokens2["refresh_token"]

    # Old refresh should now be invalid (rotation)
    r = await refresh(client, rt1)
    assert r.status_code in (401, 400)

    # New access works
    r = await me(client, at2)
    assert r.status_code == 200

    # Logout revokes refresh
    r = await logout(client, refresh_token=rt2)
    assert r.status_code in (200, 204)

    # Cannot refresh after logout
    r = await refresh(client, rt2)
    assert r.status_code in (401, 400)
