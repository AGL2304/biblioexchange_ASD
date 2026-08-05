# Architecture — BiblioExchange v2

```
Internet ──▶ Nginx (TLS, Tailwind statique) ──▶ FastAPI (JWT, RBAC) ──▶ PostgreSQL
                                                       │
                                                       ▼
                                          Prometheus / Grafana (supervision)

GitHub Actions ──▶ déploiement SSH ──▶ Instance EC2 (AWS)
```

## Composants

| Composant | Rôle |
|---|---|
| Nginx | Reverse proxy, terminaison TLS (Certbot), sert le front Tailwind |
| FastAPI | API REST, authentification JWT, RBAC user/admin |
| PostgreSQL | Persistance des données (users, books, exchanges, rendezvous, reports) |
| Prometheus | Collecte des métriques techniques et métier |
| Grafana | Dashboards et alertes |
| GitHub Actions | Tests, build, push image, déploiement, rollback |
| Terraform | Provisioning de l'infrastructure AWS (EC2, security group) |
| Ansible | Configuration du serveur (Docker, durcissement SSH, firewall) |

Voir le schéma détaillé partagé dans la conversation de conception pour la
vue graphique complète.
