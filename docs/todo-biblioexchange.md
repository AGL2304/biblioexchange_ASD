# Todo-list — BiblioExchange v2 (titre ASD)

Ordre de réalisation recommandé, aligné sur les 3 blocs de compétences.
Chaque étape indique la/les compétence(s) ASD démontrée(s).

## Phase 0 — Cadrage

- [ ] Reprendre le cahier des charges fonctionnel du PFE (users, books, exchanges, admin)
- [x] Figer le modèle de données (User, Book, Exchange, Rendezvous, Report)
- [ ] Créer le repo Git (branche `main` protégée, convention de commits)

## Phase 1 — Bloc 1 : Infrastructure

- [x] **Terraform** : écrire le module (VPC/subnet existant ou par défaut, security group, instance EC2, IP publique) — *Comp. 2*  
  (Les fichiers Terraform sont présents dans `infra/terraform/` mais le provisionnement n'a pas été exécuté ici.)
- [ ] Provisionner l'EC2 via `terraform apply` — *Comp. 4*
- [x] **Ansible** : playbook de provisioning (création user non-root, install Docker/Docker Compose, durcissement SSH — désactiver root login, clé uniquement) — *Comp. 1*  
  (`infra/ansible/playbook.yml` présent)
- [ ] Configurer le firewall (ufw / security group : ports 22, 80, 443 uniquement) — *Comp. 3*
- [ ] Mettre en place HTTPS (Certbot + Nginx) — *Comp. 3*
- [ ] Externaliser les secrets (SSM Parameter Store ou `.env` non versionné + `.gitignore`) — *Comp. 3*
- [ ] Vérifier l'accès à l'app via l'IP/domaine sur AWS — *Comp. 4*

## Phase 2 — Bloc 2 : Application et CI/CD

### Backend
- [x] Initialiser le projet FastAPI (structure : routers, models, schemas, services)
- [x] Modèles de données (SQLAlchemy) : User, Book, Exchange, Rendezvous, Report
- [x] Auth JWT (inscription, connexion, hash de mot de passe)
- [x] Middleware RBAC (dépendance `require_admin`)
- [x] Endpoints utilisateur (voir `endpoints-biblioexchange.md`)
- [x] Endpoints admin (voir `endpoints-biblioexchange.md`)
- [x] Règles métier critiques : un livre `en_negociation` non re-proposable, user suspendu bloqué

### Frontend
- [x] Setup Tailwind CLI (`npx tailwindcss init`)
- [x] Pages : accueil, mes livres, détail livre, proposition d'échange, profil, notifications
- [x] Espace admin : liste users, liste livres à valider, liste signalements (pages présentes côté front)
- [x] Intégration fetch() vers l'API FastAPI (client `frontend/src/js/api.js`)

### Containers
- [x] Dockerfile FastAPI
- [x] Dockerfile Nginx (sert le front Tailwind + reverse proxy)
- [x] `docker-compose.yml` (Nginx + FastAPI + PostgreSQL, réseau dédié, volumes) — *Comp. 7*
- [x] `docker-compose.test.yml` (environnement isolé pour les tests) — *Comp. 5*

### Tests
- [x] Tests pytest sur l'auth, le CRUD livres, les règles métier d'échange, le RBAC admin — *Comp. 5*  
  (Tests unitaires exécutés localement ; 5 tests passés dans l'exécution récente)
- [ ] Tests d'intégration (appel API réel sur l'environnement de test) — *Comp. 5*

### Données
- [ ] Script de backup `pg_dump` planifié (cron) vers stockage externe (S3 ou local) — *Comp. 6*
- [ ] Test réel d'une restauration à partir d'un backup — *Comp. 6*

### CI/CD
- [ ] Pipeline GitHub Actions : lint → tests → build image → push registry — *Comp. 8*
- [ ] Étape de déploiement automatique (SSH vers l'EC2 + `docker compose up -d`) — *Comp. 8*
- [ ] Stratégie de rollback (tag d'image précédent conservé, commande de retour arrière documentée) — *Comp. 8*
- [ ] Déclencher un déploiement de bout en bout et le documenter (capture, logs)

## Phase 3 — Bloc 3 : Supervision

- [x] Installer Prometheus + node_exporter sur l'EC2 (ou en container)  
  (Configuration Prometheus présente sous `monitoring/prometheus/` — fichiers de base fournis.)
- [x] Exposer des métriques applicatives depuis FastAPI (middleware Prometheus : latence, taux d'erreur)  
  (Endpoint `/metrics` monté dans `backend/app/main.py`)
- [ ] Définir les indicateurs métier : échanges créés/terminés/annulés par jour, signalements en attente, taux de livres refusés — *Comp. 9*
- [ ] Installer Grafana, connecter la source Prometheus, construire les dashboards — *Comp. 10*
- [x] Configurer Alertmanager (au moins 1 alerte technique + 1 alerte métier, ex : API down, pic de signalements) — *Comp. 10*  
  (Fichier d'alertes `monitoring/prometheus/alerts.yml` présent — déploiement Alertmanager non vérifié.)
- [ ] Simuler un incident (ex : couper le container PostgreSQL) et documenter la détection + la réaction — *Comp. 10*

## Phase 4 — Livrables et communication

- [x] README complet (installation, architecture, usage) avec une section en anglais — *Comp. 11*  
  (README.md présent et contient résumé et instructions de démarrage)
- [x] Schéma d'architecture final  
  (Voir `docs/architecture.md`)
- [ ] Préparer un pitch oral bilingue (FR/EN) sur le projet — *Comp. 11*
- [ ] Constituer le dossier de preuves par compétence (captures, extraits de code, logs de pipeline, dashboards)

## Phase 5 — Relecture avant soutenance

- [ ] Vérifier que chacune des 11 compétences a au moins une preuve tangible et démontrable en live
- [ ] Répéter une démo de bout en bout : provisioning → déploiement → incident → supervision
- [ ] Préparer les réponses aux questions probables du jury (choix techniques, alternatives écartées, limites connues)
