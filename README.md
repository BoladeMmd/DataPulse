# DataPulse — API d'analyse et de scoring des transactions

<p align="center">
  <strong>Une API REST de scoring des transactions, conçue avec FastAPI et une architecture conteneurisée, intégrant CI/CD et monitoring.</strong>
</p>

## Présentation du projet

**DataPulse** est un projet orienté Data Engineering et DevOps visant à développer une API REST capable d'analyser des transactions financières et de leur attribuer un score de risque à partir de règles métier.

L'objectif est de mettre en place une solution complète couvrant le développement d'une API, la gestion des données, la conteneurisation, l'intégration et le déploiement continus, ainsi que la supervision de l'application.

> **Note :** le moteur de scoring actuel repose sur des règles prédéfinies à des fins de démonstration. Il ne constitue pas un modèle de détection de fraude validé en production.

## Fonctionnalités

- Création et enregistrement de transactions.
- Calcul d'un score de risque.
- Classification des transactions : faible, moyen ou élevé.
- Identification des facteurs ayant contribué au score.
- Consultation de l'historique des transactions.
- Validation des données entrantes.
- Protection des endpoints sensibles par clé API.
- Exposition de métriques pour la supervision.
- Tests automatisés et pipeline CI/CD.

## Architecture technique

```text
                 Utilisateur / Client
                         |
                         v
                    NGINX
                         |
                         v
                  FASTAPI (API)
                         |
              +----------+----------+
              |                     |
              v                     v
        PostgreSQL             Scoring Engine
              |
              v
       Stockage des données

       Monitoring :
       Prometheus ---> Grafana

       CI/CD :
       GitHub Actions ---> Docker Hub
```

## Technologies utilisées

| Domaine | Technologies |
|---|---|
| Backend API | Python, FastAPI |
| Validation | Pydantic |
| Base de données | PostgreSQL |
| ORM | SQLAlchemy |
| Conteneurisation | Docker, Docker Compose |
| Reverse proxy | Nginx |
| Monitoring | Prometheus, Grafana |
| Tests | Pytest |
| CI/CD | GitHub Actions |
| Registry Docker | Docker Hub |

## Structure du projet

```text
DataPulse/
│
├── app/
│   ├── api/
│   ├── db/
│   ├── models/
│   ├── schemas/
│   ├── services/
│   │   └── scoring.py
│   └── main.py
│
├── tests/
│   ├── test_main.py
│   └── test_scoring.py
│
├── docker/
│   └── nginx.conf
│
├── monitoring/
│   └── prometheus.yml
│
├── .github/
│   └── workflows/
│
├── Dockerfile
├── compose.yaml
├── requirements.txt
├── .env.example
└── README.md
```

## Fonctionnement du scoring

Le moteur analyse plusieurs caractéristiques d'une transaction :

- Le montant de la transaction.
- Le pays d'origine.
- Le type de transaction.

Un score est ensuite calculé et associé à un niveau de risque.

| Score | Niveau |
|---|---|
| 0 à 24 | Faible |
| 25 à 49 | Moyen |
| 50 à 100 | Élevé |

Les facteurs ayant contribué au score sont également retournés afin de rendre le résultat interprétable.

## API et endpoints

| Méthode | Endpoint | Description | Authentification |
|---|---|---|---|
| GET | `/` | Présentation de l'API | Non |
| GET | `/health` | Vérification de disponibilité | Non |
| POST | `/transactions` | Création d'une transaction | Oui |
| GET | `/transactions` | Liste des transactions | Oui |
| POST | `/transactions/score` | Scoring sans enregistrement | Oui |
| GET | `/metrics` | Métriques Prometheus | Non |

La documentation interactive est accessible via `/docs`.

Les endpoints protégés utilisent une clé API transmise dans l'en-tête HTTP `X-API-Key`.

## Installation et exécution

### Prérequis

- Git
- Docker Desktop
- Docker Compose

### 1. Cloner le dépôt

```bash
git clone https://github.com/BoladeMmd/DataPulse.git
cd DataPulse
```

### 2. Configurer les variables d'environnement

Créer un fichier `.env` à partir de `.env.example`, puis renseigner les paramètres nécessaires :

```env
DATABASE_URL=postgresql+psycopg://datapulse_user:YOUR_PASSWORD@db:5432/datapulse
API_KEY=YOUR_STRONG_API_KEY
POSTGRES_DB=datapulse
POSTGRES_USER=datapulse_user
POSTGRES_PASSWORD=YOUR_STRONG_DATABASE_PASSWORD
```

Adapter les valeurs aux paramètres attendus par le fichier `compose.yaml`. Ne jamais publier le fichier `.env` ni ses secrets sur GitHub.

### 3. Démarrer l'architecture

```bash
docker compose up -d
```

### 4. Vérifier les conteneurs

```bash
docker compose ps
```

### 5. Consulter les logs de l'API

```bash
docker compose logs -f api
```

## Utilisation de l'API

Exemple de création d'une transaction :

```bash
curl -X POST "http://localhost:8082/transactions" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: YOUR_API_KEY" \
  -d '{
    "amount": 250000,
    "country": "SN",
    "merchant": "Supermarche Dakar",
    "transaction_type": "payment"
  }'
```

Pour consulter la documentation interactive :

```text
http://localhost:8082/docs
```

## Monitoring

DataPulse intègre une architecture de supervision basée sur Prometheus et Grafana.

- **Prometheus** collecte les métriques exposées par l'API.
- **Grafana** permet de visualiser les indicateurs de fonctionnement à travers des dashboards.

Interfaces locales :

| Service | URL |
|---|---|
| API | http://localhost:8082 |
| Swagger | http://localhost:8082/docs |
| Prometheus | http://localhost:9090 |
| Grafana | http://localhost:3000 |

## Tests automatisés

Les tests sont réalisés avec Pytest.

Exécution locale :

```bash
python -m pytest -v
```

**Résultat obtenu : 16 tests réussis.**

Les tests couvrent notamment :
- Les règles de scoring.
- Les endpoints de l'API.
- La validation des données.
- L'authentification par clé API.
- La gestion des erreurs de base de données.

## Pipeline CI/CD

GitHub Actions automatise le processus de livraison :

1. Déclenchement à la suite d'un push sur `main`.
2. Installation des dépendances Python.
3. Exécution des tests automatisés.
4. Construction de l'image Docker si les tests réussissent.
5. Publication de l'image sur Docker Hub.

Image Docker :

```bash
docker pull bolade07/datapulse:latest
```

Dépôt Docker Hub : https://hub.docker.com/r/bolade07/datapulse

## Sécurité

Quelques mesures intégrées au projet :

- Authentification par clé API pour les opérations sensibles.
- Gestion des variables sensibles avec `.env`.
- Secrets CI/CD stockés dans GitHub Secrets.
- Utilisation de `secrets.compare_digest` pour comparer les clés API.
- Isolation des services dans l'environnement Docker Compose.

## Perspectives d'amélioration

- Déploiement sur un serveur Linux distant.
- Mise en place du HTTPS avec un nom de domaine.
- Évolution du moteur de scoring vers un modèle de Machine Learning évalué sur des données adaptées.
- Renforcement de la gestion des utilisateurs et des permissions.
- Amélioration des alertes et de la supervision.

## Auteur

**Boladé Mamadou**

Projet personnel — Data Engineering & DevOps.

- GitHub : https://github.com/BoladeMmd
- Projet : https://github.com/BoladeMmd/DataPulse

---

*DataPulse — From transaction data to actionable risk insights.*