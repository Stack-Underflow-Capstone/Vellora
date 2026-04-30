#helper funcs for auth tests

async def register(client, email="alice@example.com", password="Pass123!", name="Alice"):
    return await client.post("/api/v1/auth/register", json={
        "email": email,
        "password": password,
        "name": name
    })


async def login(client, email="alice@example.com", password="Pass123!"):
    return await client.post("/api/v1/auth/login", data={
        "username": email,
        "password": password
    })


async def me(client, access_token):
    return await client.get("/api/v1/auth/me", headers={
        "Authorization": f"Bearer {access_token}"
    })


async def refresh(client, refresh_token):
    return await client.post("/api/v1/auth/refresh", json={
        "refresh_token": refresh_token
    })


async def logout(client, refresh_token):
    return await client.post("/api/v1/auth/logout", json={
        "refresh_token": refresh_token
    })