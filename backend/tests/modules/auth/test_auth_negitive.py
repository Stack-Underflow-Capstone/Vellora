import jwt
from app.config import get_settings
from tests.modules.auth.test_helpers import register, login, me, refresh, logout

async def test_login_wrong_password(client):
    await register(client, email="bob@example.com", password="CorrectHorse1!")
    r = await login(client, email="bob@example.com", password="WrongPass1!")
    assert r.status_code in (400, 401)

async def test_protected_requires_bearer(client):
    resp = await client.get("/api/v1/auth/me")
    assert resp.status_code == 401

async def test_tampered_jwt_signature(client):
    await register(client, email="carol@example.com", password="StrongP@ss1!")
    r = await login(client, email="carol@example.com", password="StrongP@ss1!")
    response = r.json()
    tokens = response.get("tokens", response)
    at = tokens["access_token"]

    # Replace signature with junk (simulate tamper)
    parts = at.split(".")
    fake = parts[0] + "." + parts[1] + ".xxxx"
    resp = await client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {fake}"})
    assert resp.status_code == 401

async def test_expired_access_token(client):
    await register(client, email="dave@example.com", password="Aaa1!aaaa")
    r = await login(client, email="dave@example.com", password="Aaa1!aaaa")
    response = r.json()
    tokens = response.get("tokens", response)
    
    #create an expired token manually using the security module
    from app.core.security import create_access_token
    from app.core.security import decode_access_token
    import time
    
    #decode the original token to get the user ID
    original_token = tokens["access_token"]
    payload = decode_access_token(original_token)
    user_id = payload["sub"]
    
    #create a token that expires in 1 second
    short_token = create_access_token(subject=user_id, expires_in_minutes=1/60)  # 1 sec
    time.sleep(2)
    
    resp = await client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {short_token}"})
    assert resp.status_code in (401, 403)

async def test_refresh_reuse_detection(client):
    await register(client, email="erin@example.com", password="Aaa1!aaaa")
    r = await login(client, email="erin@example.com", password="Aaa1!aaaa")
    response = r.json()
    tokens = response.get("tokens", response)
    rt1 = tokens["refresh_token"]

    # First refresh (valid)
    r = await refresh(client, rt1)
    assert r.status_code == 200
    rt2 = r.json()["tokens"]["refresh_token"]

    # Reuse the first (should fail due to rotation)
    r = await refresh(client, rt1)
    assert r.status_code in (401, 400)

    # New one still valid
    r = await refresh(client, rt2)
    assert r.status_code == 200
