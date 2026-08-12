"""
Export des indicateurs metier au format Prometheus.

Reutilise les memes requetes que app/routers/admin_stats.py, mais expose les
valeurs en Gauge plutot qu'en JSON authentifie, pour que Prometheus puisse
les collecter sur /metrics (endpoint non authentifie, cf. deny au niveau Nginx).

Un Collector personnalise interroge la base a chaque scrape Prometheus (pas de
tache de fond, pas de valeurs perimees) : cf. doc prometheus_client sur les
"Custom Collectors".
"""
from datetime import datetime, timedelta, timezone

from prometheus_client.core import GaugeMetricFamily
from prometheus_client.registry import Collector

from app.core.database import SessionLocal
from app.models.book import Book
from app.models.exchange import Exchange, ExchangeStatus
from app.models.report import Report, ReportStatus


class BusinessMetricsCollector(Collector):
    def collect(self):
        db = SessionLocal()
        try:
            since_24h = datetime.now(timezone.utc) - timedelta(days=1)

            exchanges_created = GaugeMetricFamily(
                "biblioexchange_exchanges_created_24h",
                "Nombre d'echanges crees dans les dernieres 24h",
            )
            exchanges_created.add_metric(
                [], db.query(Exchange).filter(Exchange.created_at >= since_24h).count()
            )
            yield exchanges_created

            exchanges_by_status = GaugeMetricFamily(
                "biblioexchange_exchanges_by_status",
                "Nombre d'echanges par statut courant",
                labels=["statut"],
            )
            for status in ExchangeStatus:
                count = db.query(Exchange).filter(Exchange.statut == status).count()
                exchanges_by_status.add_metric([status.value], count)
            yield exchanges_by_status

            books_pending = GaugeMetricFamily(
                "biblioexchange_books_pending_moderation",
                "Nombre de livres en attente de validation admin",
            )
            books_pending.add_metric(
                [], db.query(Book).filter(Book.valide_par_admin == False).count()  # noqa: E712
            )
            yield books_pending

            reports_open = GaugeMetricFamily(
                "biblioexchange_reports_open",
                "Nombre de signalements ouverts (non traites)",
            )
            reports_open.add_metric(
                [], db.query(Report).filter(Report.statut == ReportStatus.ouvert).count()
            )
            yield reports_open
        finally:
            db.close()


def register_business_metrics():
    """A appeler une seule fois au demarrage de l'app (voir main.py)."""
    from prometheus_client import REGISTRY

    REGISTRY.register(BusinessMetricsCollector())