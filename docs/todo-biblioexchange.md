# Todo-list — BiblioExchange v2 (titre ASD)

Ordre de réalisation recommandé, aligné sur les 3 blocs de compétences.
Chaque étape indique la/les compétence(s) ASD démontrée(s).

*Mise à jour du 06/08/2026 — voir le récapitulatif en fin de fichier pour le détail des changements de cette session.*

## Phase 0 — Cadrage

- [ ] Reprendre le cahier des charges fonctionnel du PFE (users, books, exchanges, admin)
- [x] Figer le modèle de données (User, Book, Exchange, Rendezvous, Report)
- [ ] Créer le repo Git (branche `main` protégée, convention de commits)
  (Repo existant et actif ; plusieurs commits conventionnels passés cette session — voir note Git en fin de fichier. Protection de branche et workflow PR toujours à faire.)

## Phase 1 — Bloc 1 : Infrastructure

- [x] **Terraform** : écrire le module (security group, instance EC2, IP publique) — *Comp. 2*
- [x] Provisionner l'EC2 via `terraform apply` — *Comp. 4*
  (Instance `i-0c09ff97b74bb8ccf` (51.44.24.184) et security group `sg-0e7069ca8754653ad` confirmés actifs sur AWS, réimportés proprement dans un state Terraform sain — `terraform plan` renvoie `No changes.`)
- [x] **Ansible** : playbook de provisioning (création user non-root, install Docker/Docker Compose, durcissement SSH) — *Comp. 1*
- [x] **Sécuriser le backend Terraform** : migration du state vers S3 (chiffré AES-256, versionné, verrouillage natif `use_lockfile`) + purge de l'historique Git des fichiers sensibles (`terraform.tfstate`, `tfplan`, binaire provider 674 Mo) via `git-filter-repo` — *Comp. 3* **[NOUVEAU cette session]**
- [ ] Configurer le firewall (ufw / security group : ports 22, 80, 443 uniquement) — *Comp. 3*
  (⚠️ Le port 22 est actuellement ouvert à `0.0.0.0/0` en plus de l'IP admin, pour permettre au runner GitHub Actions de se connecter en SSH. C'est documenté comme temporaire dans le code Terraform. À migrer vers AWS SSM Session Manager pour supprimer cette règle — voir action prioritaire ci-dessous.)
- [ ] Mettre en place HTTPS (Certbot + Nginx) — *Comp. 3*
- [ ] Externaliser les secrets (SSM Parameter Store) — *Comp. 3*
  (`.env` généré sur l'EC2 avec des secrets forts, non versionné, `chmod 600`. Secrets CI dans GitHub — repo + environment `production`. Reste : migration vers un vrai secret manager plutôt qu'un fichier `.env` local.)
- [x] Vérifier l'accès à l'app via l'IP/domaine sur AWS — *Comp. 4*
  (Health check `curl -f http://localhost:8000/health` exécuté depuis la CI à chaque déploiement, réponse `{"status":"ok"}` confirmée. Reste à vérifier l'accès navigateur complet via le port 80/443.)

## Phase 2 — Bloc 2 : Application et CI/CD

### Backend
- [x] Initialiser le projet FastAPI (structure : routers, models, schemas, services)
- [x] Modèles de données (SQLAlchemy) : User, Book, Exchange, Rendezvous, Report
- [x] Auth JWT (inscription, connexion, hash de mot de passe)
- [x] Middleware RBAC (dépendance `require_admin`)
- [x] Endpoints utilisateur (voir `endpoints-biblioexchange.md`)
- [x] Endpoints admin (voir `endpoints-biblioexchange.md`)
- [x] Règles métier critiques : un livre `en_negociation` non re-proposable, user suspendu bloqué
  (⚠️ Deux trous identifiés à l'audit : `complete_exchange` ne vérifie ni rôle ni statut courant du demandeur, `cancel_exchange` ouvert aux deux participants à tout moment. À corriger avant soutenance — ce sont des règles que tu revendiques comme testées.)

### Frontend
- [x] Setup Tailwind CLI (`npx tailwindcss init`)
- [x] Pages : accueil, mes livres, détail livre, proposition d'échange, profil, notifications
- [x] Espace admin : liste users, liste livres à valider, liste signalements
- [x] Intégration fetch() vers l'API FastAPI (client `frontend/src/js/api.js`)
- [ ] **[NOUVEAU]** Faire pointer les pages vers le CSS Tailwind compilé (`output.css`) au lieu du CDN `cdn.tailwindcss.com` — les 15 pages HTML chargent actuellement le CDN malgré l'étape de build dans le Dockerfile, qui ne sert donc à rien
- [ ] **[NOUVEAU]** Supprimer le front dupliqué : `frontend/src/pages/*.html` (7 pages sans `api.js`) coexiste avec `frontend/src/*.html` (8 pages complètes), les deux sont copiées dans l'image Nginx

### Containers
- [x] Dockerfile FastAPI
- [x] Dockerfile Nginx (sert le front Tailwind + reverse proxy)
- [x] `docker-compose.yml` (Nginx + FastAPI + PostgreSQL, réseau dédié, volumes) — *Comp. 7*
- [x] `docker-compose.test.yml` (environnement isolé pour les tests) — *Comp. 5*
- [ ] **[NOUVEAU]** Durcir les containers : utilisateur non-root dans le Dockerfile backend, `HEALTHCHECK`, `restart: unless-stopped`, `depends_on` avec `condition: service_healthy` pour Postgres
- [ ] **[NOUVEAU]** Passer `backend` (8000), `prometheus` (9090) et `grafana` (3000) en `expose:` plutôt qu'en `ports:` — actuellement accessibles directement sur l'hôte en contournement du reverse proxy (le security group AWS protège aujourd'hui, mais c'est une seule couche de défense)

### Tests
- [x] Tests pytest sur l'auth, le CRUD livres, les règles métier d'échange, le RBAC admin — *Comp. 5*
- [ ] Tests d'intégration (appel API réel sur l'environnement de test) — *Comp. 5*

### Données
- [ ] Script de backup `pg_dump` planifié (cron) vers stockage externe (S3 ou local) — *Comp. 6*
- [ ] Test réel d'une restauration à partir d'un backup — *Comp. 6*

### CI/CD
- [x] Pipeline GitHub Actions : lint → tests → build image → scan sécurité → push registry — *Comp. 8* **[FAIT cette session]**
  (`.github/workflows/ci.yml` créé et poussé. Images taguées `:latest` **et** `:${{ github.sha }}`. Scan Trivy sur les deux images (CRITICAL/HIGH), action épinglée par SHA de commit immuable suite à l'incident de supply chain trivy-action de mars 2026.)
- [x] Étape de déploiement automatique (SSH vers l'EC2 + `docker compose up -d`) — *Comp. 8* **[FAIT cette session]**
  (Déploiement via `appleboy/ssh-action`, secrets dans l'environment GitHub `production`, `IMAGE_TAG` propagé par SHA.)
- [ ] Stratégie de rollback (tag d'image précédent conservé, commande de retour arrière documentée) — *Comp. 8*
  (Le tagging par SHA rend le rollback techniquement possible — reste à documenter et tester la procédure explicitement : `docker compose` avec un `IMAGE_TAG` antérieur.)
- [x] Déclencher un déploiement de bout en bout et le documenter (capture, logs) — *Comp. 8* **[FAIT cette session]**
  (Run complet test → build → scan → push → deploy → health check exécuté avec succès, réponse `{"status":"ok"}` capturée. Documenté dans le dossier §5.6/5.8.)

## Phase 3 — Bloc 3 : Supervision

- [x] Installer Prometheus + node_exporter sur l'EC2 (ou en container)
  (⚠️ `prometheus.yml` scrape la cible `node-exporter:9100`, mais **aucun service `node-exporter` n'existe dans `docker-compose.yml`** — cette target sera rouge en permanence. Cocher réellement quand le service sera ajouté au compose.)
- [x] Exposer des métriques applicatives depuis FastAPI (middleware Prometheus : latence, taux d'erreur)
- [ ] Définir les indicateurs métier : échanges créés/terminés/annulés par jour, signalements en attente, taux de livres refusés — *Comp. 9*
  (Les indicateurs existent en JSON sur `/admin/stats/*` derrière l'auth admin — Prometheus ne peut pas les lire. Il faut les ré-exposer en `Gauge`/`Counter` `prometheus_client` sur `/metrics`.)
- [ ] Installer Grafana, connecter la source Prometheus, construire les dashboards — *Comp. 10*
  (Le compose monte `./monitoring/grafana/dashboards`, mais ce dossier n'existe pas dans le dépôt — Grafana démarrera sans aucun dashboard.)
- [ ] Configurer Alertmanager (au moins 1 alerte technique + 1 alerte métier) — *Comp. 10*
  (Absent du `docker-compose.yml` et absent de `prometheus.yml` — pas de bloc `alerting:`. Les 2 règles dans `alerts.yml` existent mais ne sont reçues par personne. L'alerte métier est encore un `# TODO` commenté.)
- [ ] Simuler un incident (ex : couper le container PostgreSQL) et documenter la détection + la réaction — *Comp. 10*

## Phase 4 — Livrables et communication

- [x] README complet (installation, architecture, usage) avec une section en anglais — *Comp. 11*
  (⚠️ Décrit `.github/` et `.env.example` dans « Structure du dépôt » — `.github/` est maintenant réel (pipeline créé cette session), à revérifier que `.env.example` l'est aussi et correctement commitable.)
- [x] Schéma d'architecture final
  (⚠️ `docs/architecture.md` renvoie encore à « le schéma détaillé partagé dans la conversation de conception » — phrase à corriger, sans valeur pour un lecteur externe.)
- [ ] **[NOUVEAU]** Ajouter une vue réseau/flux au schéma (ports, qui parle à qui, où se termine le TLS, ce qui est publié sur l'hôte) en complément de la vue composants existante
- [ ] Préparer un pitch oral bilingue (FR/EN) sur le projet — *Comp. 11*
- [ ] Constituer le dossier de preuves par compétence (captures, extraits de code, logs de pipeline, dashboards)
  (Première preuve concrète obtenue cette session : capture du run CI/CD vert avec health check réussi.)

## Phase 5 — Relecture avant soutenance

- [ ] Vérifier que chacune des 11 compétences a au moins une preuve tangible et démontrable en live
- [ ] Répéter une démo de bout en bout : provisioning → déploiement → incident → supervision
- [ ] Préparer les réponses aux questions probables du jury (choix techniques, alternatives écartées, limites connues)
  (Prépare en particulier : pourquoi EC2+Compose plutôt qu'ECS/Kubernetes, pourquoi Postgres en container plutôt que RDS, pourquoi GitHub Actions plutôt que GitLab CI, et où se situe la base par rapport au réseau — VPC par défaut implicite, pas de VPC/subnet dédié déclaré.)
- [ ] **[NOUVEAU]** Vérifier/compléter le champ « Session : ______ » vide en page de garde du dossier
- [ ] **[NOUVEAU]** Retravailler le §4.3 « Collaborations » du dossier — assimiler les rôles applicatifs user/admin à des équipes produit/support est un contournement qui se verra ; documenter plutôt de vrais échanges (revue de code, retours de session de suivi, issues/PR)
- [ ] **[NOUVEAU]** Corriger le §5.3 du dossier : le logger d'audit `unauthorized_admin_access` n'alimente aucune alerte réelle (pas de Loki/promtail, pas d'alerte correspondante) — exporter un `Counter` Prometheus incrémenté dans `require_admin` et écrire l'alerte, ou reformuler l'affirmation
- [ ] **[NOUVEAU]** Compléter le §3.2 du dossier avec les alternatives écartées pour chaque choix technologique (une ligne « alternative + raison » suffit)

---

## Récapitulatif — ce qui a changé cette session (06/08/2026)

**Corrigé / fait :**
- Pipeline CI/CD écrit, poussé, et exécuté avec succès de bout en bout (test → build → scan Trivy → push → deploy SSH → health check)
- Scan de sécurité Trivy intégré, épinglé par SHA suite à l'incident de supply chain de mars 2026
- Images Docker versionnées par SHA de commit (traçabilité + rollback technique possible)
- Secrets Docker Hub et EC2 configurés côté GitHub (repo + environment `production`)
- `.env` généré sur l'EC2 avec des secrets forts, non versionné
- Infrastructure EC2 confirmée active et réimportée proprement dans le state Terraform
- State Terraform migré vers un backend S3 chiffré, versionné, avec verrouillage natif
- Historique Git purgé des fichiers sensibles (`tfstate`, `tfplan`, binaire 674 Mo) via `git-filter-repo`
- Dossier de projet (.docx) mis à jour : §5.6 CI/CD actualisée, §5.8 (nouvelle, sécurisation du state) et §6.5 (nouvelle, incident supply chain trivy-action) ajoutées

**Toujours manquant (repris de l'audit du 05/08) :**
- Supervision non exploitée : `node-exporter` absent du compose, dossier de dashboards Grafana inexistant, Alertmanager non configuré, indicateurs métier non exportés en format Prometheus
- Aucune sauvegarde PostgreSQL, aucun test de restauration
- Pas de TLS (Certbot/Nginx) alors que l'architecture l'annonce
- Front : CDN Tailwind au lieu du build compilé, pages dupliquées
- Ports d'administration (8000/9090/3000) publiés directement sur l'hôte
- Pas de migrations de schéma (Alembic)
- `CORS allow_origins=["*"]` non restreint
- Containers non durcis (root, pas de healthcheck, pas de restart policy)
- Deux trous dans la logique métier (`complete_exchange`, `cancel_exchange`)
- Le port SSH 22 est temporairement ouvert à `0.0.0.0/0` pour la CI — à migrer vers SSM
- Un seul gros commit initial reste dans l'historique (les commits de cette session sont propres et conventionnels, mais ne réparent pas rétroactivement le premier commit) ; pas de branche protégée, pas de PR, pas de tags de version
- Plusieurs incohérences documentaires restantes (README vs contenu réel, `docs/architecture.md`, tableau des alternatives, §4.3, champ Session vide)