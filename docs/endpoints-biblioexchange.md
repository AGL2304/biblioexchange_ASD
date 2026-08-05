# Endpoints API — BiblioExchange v2

API REST FastAPI. Auth par JWT (Bearer token). Les routes `/admin/*` nécessitent
le rôle `admin` (dépendance RBAC), toutes les autres routes authentifiées
nécessitent un compte `actif`.

## Légende des statuts

- `Book.statut` : `disponible` | `indisponible` | `en_negociation`
- `Book.valide_par_admin` : `true` | `false`
- `Exchange.statut` : `propose` | `accepte` | `refuse` | `annule` | `termine`
- `Rendezvous.statut` : `prevu` | `confirme` | `passe` | `annule`
- `User.statut_compte` : `actif` | `suspendu`
- `Report.statut` : `ouvert` | `traite`

---

## 1. Authentification

| Méthode | Route | Description | Accès |
|---|---|---|---|
| POST | `/auth/register` | Inscription (email, nom, mot de passe) | Public |
| POST | `/auth/login` | Connexion, retourne un JWT | Public |
| POST | `/auth/refresh` | Rafraîchit le token | Authentifié |
| PATCH | `/auth/credentials` | Modifie email / mot de passe | Authentifié |

## 2. Profil utilisateur

| Méthode | Route | Description | Accès |
|---|---|---|---|
| GET | `/users/me` | Récupère le profil courant | Authentifié |
| PATCH | `/users/me` | Modifie nom, photo, etc. | Authentifié |
| GET | `/users/me/exchanges` | Historique des échanges de l'utilisateur | Authentifié |
| GET | `/users/{id}` | Profil public d'un autre utilisateur | Authentifié |

## 3. Livres

| Méthode | Route | Description | Accès | Règle métier |
|---|---|---|---|---|
| GET | `/books` | Liste des livres disponibles (recherche, filtres titre/auteur/catégorie) | Public/Authentifié | Ne retourne que `statut=disponible` et `valide_par_admin=true` |
| GET | `/books/{id}` | Détail d'un livre | Public/Authentifié | |
| GET | `/books/mine` | Mes livres (tous statuts) | Authentifié | |
| POST | `/books` | Publier un livre | Authentifié | Créé avec `valide_par_admin=false` en attente de modération |
| PATCH | `/books/{id}` | Modifier un livre | Authentifié (propriétaire) | Refusé si `statut=en_negociation` |
| DELETE | `/books/{id}` | Supprimer un livre | Authentifié (propriétaire) | Refusé si `statut=en_negociation` |
| PATCH | `/books/{id}/status` | Basculer disponible/indisponible | Authentifié (propriétaire) | |

## 4. Échanges

| Méthode | Route | Description | Accès | Règle métier |
|---|---|---|---|---|
| POST | `/exchanges` | Proposer un échange (livre offert + livre demandé) | Authentifié | Les deux livres doivent être `disponible` ; passe les deux en `en_negociation` |
| GET | `/exchanges` | Liste des échanges de l'utilisateur (envoyés/reçus) | Authentifié | |
| GET | `/exchanges/{id}` | Détail d'un échange | Authentifié (parties prenantes) | |
| PATCH | `/exchanges/{id}/accept` | Accepter la proposition | Authentifié (destinataire) | |
| PATCH | `/exchanges/{id}/refuse` | Refuser la proposition | Authentifié (destinataire) | Remet les deux livres à `disponible` |
| PATCH | `/exchanges/{id}/cancel` | Annuler un échange en cours | Authentifié (parties prenantes) | Remet les deux livres à `disponible` |
| PATCH | `/exchanges/{id}/complete` | Marquer l'échange comme terminé | Authentifié (parties prenantes) | Transfère la propriété des livres |

## 5. Rendez-vous

| Méthode | Route | Description | Accès |
|---|---|---|---|
| POST | `/exchanges/{id}/rendezvous` | Proposer un lieu + créneau (date, heure, durée) | Authentifié (parties prenantes) |
| PATCH | `/rendezvous/{id}/confirm` | Confirmer le RDV | Authentifié (parties prenantes) |
| PATCH | `/rendezvous/{id}/cancel` | Annuler le RDV | Authentifié (parties prenantes) |
| GET | `/exchanges/{id}/rendezvous` | Consulter le RDV lié à un échange | Authentifié (parties prenantes) |

## 6. Notifications

| Méthode | Route | Description | Accès |
|---|---|---|---|
| GET | `/notifications` | Liste des notifications de l'utilisateur | Authentifié |
| PATCH | `/notifications/{id}/read` | Marquer comme lue | Authentifié |

## 7. Forum

| Méthode | Route | Description | Accès |
|---|---|---|---|
| GET | `/forum/threads` | Liste des sujets | Authentifié |
| POST | `/forum/threads` | Créer un sujet | Authentifié |
| GET | `/forum/threads/{id}` | Détail + réponses | Authentifié |
| POST | `/forum/threads/{id}/replies` | Répondre à un sujet | Authentifié |

## 8. Signalements (utilisateur)

| Méthode | Route | Description | Accès |
|---|---|---|---|
| POST | `/reports` | Signaler un utilisateur ou un livre (motif) | Authentifié |

---

## 9. Administration — Utilisateurs

| Méthode | Route | Description | Accès |
|---|---|---|---|
| GET | `/admin/users` | Liste de tous les utilisateurs (filtre par statut) | Admin |
| GET | `/admin/users/{id}` | Détail d'un utilisateur | Admin |
| PATCH | `/admin/users/{id}/suspend` | Suspendre un compte | Admin |
| PATCH | `/admin/users/{id}/reactivate` | Réactiver un compte | Admin |
| DELETE | `/admin/users/{id}` | Supprimer un compte | Admin |

## 10. Administration — Livres

| Méthode | Route | Description | Accès |
|---|---|---|---|
| GET | `/admin/books` | Liste de tous les livres (filtre : en attente de validation, tous statuts) | Admin |
| PATCH | `/admin/books/{id}/validate` | Valider un livre (`valide_par_admin=true`) | Admin |
| PATCH | `/admin/books/{id}/reject` | Rejeter un livre (motif) | Admin |
| DELETE | `/admin/books/{id}` | Supprimer un livre | Admin |

## 11. Administration — Échanges et litiges

| Méthode | Route | Description | Accès |
|---|---|---|---|
| GET | `/admin/exchanges` | Liste de tous les échanges (filtre par statut) | Admin |
| GET | `/admin/exchanges/{id}` | Détail complet d'un échange (audit) | Admin |
| PATCH | `/admin/exchanges/{id}/force-cancel` | Forcer l'annulation (résolution de litige) | Admin |

## 12. Administration — Signalements

| Méthode | Route | Description | Accès |
|---|---|---|---|
| GET | `/admin/reports` | Liste des signalements (filtre par statut) | Admin |
| PATCH | `/admin/reports/{id}/resolve` | Marquer un signalement comme traité | Admin |

## 13. Administration — Statistiques (bloc 3)

| Méthode | Route | Description | Accès |
|---|---|---|---|
| GET | `/admin/stats/exchanges` | Échanges créés/terminés/annulés par période | Admin |
| GET | `/admin/stats/moderation` | Taux de validation/rejet des livres, signalements en attente | Admin |
| GET | `/metrics` | Endpoint Prometheus (latence, taux d'erreur, requêtes/s) | Interne (scrape Prometheus uniquement, non exposé publiquement) |

---

## Notes de sécurité (Bloc 1, compétence 3)

- Toutes les routes `/admin/*` : vérifier le rôle **et** logger l'action (audit trail : qui, quoi, quand)
- Toute tentative d'accès à une route admin par un non-admin doit être loggée pour alimenter une alerte de supervision (Bloc 3)
- `/metrics` ne doit être accessible que depuis le réseau interne (Nginx bloque l'accès public à ce endpoint)
