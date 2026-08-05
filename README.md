# BiblioExchange v2

Plateforme d'échange de livres entre particuliers, reconstruite dans le cadre
du titre ASD (Administrateur Système DevOps). Reprise du projet de fin
d'études BiblioExchange avec une architecture cloud, conteneurisée,
livrée en continu et supervisée.

## Structure du dépôt

```
biblioexchange/
├── backend/       API FastAPI (auth, livres, échanges, admin)
├── frontend/      Front HTML/JS + Tailwind CSS
├── infra/         Terraform (IaC) + Ansible (provisioning)
├── monitoring/    Configuration Prometheus + dashboards Grafana
├── .github/       Pipeline CI/CD (GitHub Actions)
├── docs/          Documentation, todo-list, spécification des endpoints
├── docker-compose.yml
├── docker-compose.test.yml
└── .env.example
```

## Démarrage rapide (développement local)

```bash
cp .env.example .env
docker compose up --build
```

- API : http://localhost:8000/docs
- Front : http://localhost:8080

## Documentation

- [`docs/architecture.md`](docs/architecture.md) — architecture cible
- [`docs/endpoints-biblioexchange.md`](docs/endpoints-biblioexchange.md) — spécification API
- [`docs/todo-biblioexchange.md`](docs/todo-biblioexchange.md) — plan de réalisation par bloc de compétences

## Stack technique

| Couche | Techno |
|---|---|
| Front-end | HTML/JS + Tailwind CSS |
| Back-end | FastAPI (Python), JWT, RBAC |
| Base de données | PostgreSQL |
| Reverse proxy | Nginx + Certbot |
| Conteneurisation | Docker / Docker Compose |
| IaC | Terraform |
| Provisioning | Ansible |
| CI/CD | GitHub Actions |
| Supervision | Prometheus + Grafana |
| Cloud | AWS EC2 |

## English summary

BiblioExchange v2 is a book-exchange platform rebuilt to demonstrate the
full DevSecOps lifecycle: infrastructure as code, containerized CI/CD
delivery, and production monitoring, on top of a FastAPI/PostgreSQL backend
and a Tailwind CSS frontend.
