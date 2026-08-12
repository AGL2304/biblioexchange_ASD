from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import make_asgi_app
from prometheus_fastapi_instrumentator import Instrumentator

from app.core.database import Base, engine
from app.core.metrics import register_business_metrics
from app import models  # noqa: F401  (enregistre les modèles avant create_all)
from app.routers import (
    auth, users, books, exchanges, rendezvous, notifications, forum, reports,
    admin_users, admin_books, admin_exchanges, admin_reports, admin_stats,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Simple pour le développement. En production : migrations Alembic versionnées.
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(title="BiblioExchange API", version="2.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # à restreindre au domaine du front en production
    allow_methods=["*"],
    allow_headers=["*"],
)


# Routes utilisateur
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(users.router, prefix="/users", tags=["users"])
app.include_router(books.router, prefix="/books", tags=["books"])
app.include_router(exchanges.router, prefix="/exchanges", tags=["exchanges"])
app.include_router(rendezvous.router, tags=["rendezvous"])
app.include_router(notifications.router, prefix="/notifications", tags=["notifications"])
app.include_router(forum.router, prefix="/forum", tags=["forum"])
app.include_router(reports.router, prefix="/reports", tags=["reports"])

# Routes admin
app.include_router(admin_users.router, prefix="/admin/users", tags=["admin"])
app.include_router(admin_books.router, prefix="/admin/books", tags=["admin"])
app.include_router(admin_exchanges.router, prefix="/admin/exchanges", tags=["admin"])
app.include_router(admin_reports.router, prefix="/admin/reports", tags=["admin"])
app.include_router(admin_stats.router, prefix="/admin/stats", tags=["admin"])

# Métriques métier custom (échanges, modération, signalements) — voir app/core/metrics.py
register_business_metrics()

# Instrumentation HTTP automatique (latence, http_requests_total par route/statut)
# expose=False : on garde un seul point de montage /metrics (ci-dessous), gere par
# make_asgi_app, plutot que le endpoint /metrics par defaut de l'instrumentator.
Instrumentator().instrument(app)

# Endpoint Prometheus (bloqué publiquement au niveau de Nginx, voir frontend/nginx.conf)
app.mount("/metrics", make_asgi_app())


@app.get("/health", tags=["health"])
def health_check():
    return {"status": "ok"}