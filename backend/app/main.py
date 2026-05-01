from fastapi import FastAPI
from uvicorn.middleware.proxy_headers import ProxyHeadersMiddleware
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.router import router as api_v1_router
import os

app = FastAPI(title="Vellora", version="1.0.0", docs_url=None if os.getenv("ENV") == "Production" else "/docs", redoc_url=None if os.getenv("ENV") == "Production" else "/redoc")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# @app.get("/")
# def root():
#     return {"status": "ok", "app": "Vellora"}

app.include_router(api_v1_router)

# Add this middleware. 'trusted_hosts="*"' is usually safe on EC2
# as long as your security group only allows traffic from your load balancer/Caddy.
app.add_middleware(ProxyHeadersMiddleware, trusted_hosts="*")
