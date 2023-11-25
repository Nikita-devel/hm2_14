"""
FastAPI Application Configuration

This module configures a FastAPI application with routes, middleware, and event handlers.

Attributes:
    origins (List[str]): List of allowed origins for CORS.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.middlewares.middlewares import startup_event, ban_ips_middleware, limit_access_by_ip, \
    user_agent_ban_middleware
from src.routes import contacts, auth, users

origins = ["https://localhost:3000"]

app = FastAPI()

app.include_router(auth.router, prefix='/api')
app.include_router(contacts.router, prefix="/api")
app.include_router(users.router, prefix="/api")

app.add_event_handler("startup", startup_event)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.middleware("http")(ban_ips_middleware)
app.middleware("http")(limit_access_by_ip)
app.middleware("http")(user_agent_ban_middleware)

