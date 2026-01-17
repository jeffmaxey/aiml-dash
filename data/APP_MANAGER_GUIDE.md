# AppManager - Gestionnaire d'Application Centralisé

Le `AppManager` est le gestionnaire central de l'application AIML Dash qui orchestre tous les composants, paramètres, sessions et actions.

## Vue d'ensemble

```python
from aiml_dash.utils.app_manager import app_manager

# Accès global au gestionnaire d'application
status = app_manager.get_status_summary()
print(f"Datasets: {status['data']['datasets']}")
print(f"Projects: {status['projects']['total']}")
```

## Architecture

```
┌─────────────────────────────────────────────────┐
│              AppManager (Singleton)              │
│  Orchestration centrale de l'application        │
├─────────────────────────────────────────────────┤
│  • Sessions (multi-utilisateurs)                │
│  • Settings (configuration globale)             │
│  • Action History (traçabilité)                 │
│  • Cache (résultats temporaires)                │
│  • State Management (import/export)             │
└────────┬─────────────────────┬──────────────────┘
         │                     │
         ▼                     ▼
┌─────────────────┐   ┌──────────────────┐
│  DataManager    │   │ ProjectManager   │
│  (Datasets)     │   │  (Projects)      │
└─────────────────┘   └──────────────────┘
```

## Fonctionnalités principales

### 1. Gestion des Sessions

Gérez plusieurs sessions utilisateur avec état isolé.

```python
# Créer une session
session = app_manager.create_session("alice@example.com")

# Définir comme session active
app_manager.set_active_session(session.id)

# Stocker des données de session
session = app_manager.get_session()
session.set_data("selected_dataset", "diamonds")
session.set_setting("theme", "dark")

# Récupérer des données
dataset = session.get_data("selected_dataset")
theme = session.get_setting("theme")

# Lister toutes les sessions
all_sessions = app_manager.list_sessions()

# Nettoyer les sessions inactives
removed = app_manager.cleanup_inactive_sessions(timeout_seconds=3600)
```

#### Classe Session

```python
from aiml_dash.utils.app_manager import Session

session = Session(user_id="user@example.com")

# Données de session
session.set_data("key", "value")
value = session.get_data("key", default="default_value")

# Paramètres de session
session.set_setting("preference", "option")
pref = session.get_setting("preference")

# Historique d'actions
session.add_to_history("action_name", {"detail": "info"})
history = session.history  # Liste des actions

# Sérialisation
data = session.to_dict()
restored = Session.from_dict(data)
```

### 2. Gestion des Paramètres

Configuration globale de l'application.

```python
# Obtenir un paramètre
theme = app_manager.get_setting("theme")
page_size = app_manager.get_setting("page_size", default=10)

# Définir un paramètre
app_manager.set_setting("theme", "dark")
app_manager.set_setting("debug_mode", True)

# Mettre à jour plusieurs paramètres
app_manager.update_settings({
    "theme": "dark",
    "page_size": 25,
    "show_code": False
})

# Réinitialiser aux valeurs par défaut
app_manager.reset_settings()

# Export/Import
app_manager.export_settings("settings.json")
app_manager.import_settings("settings.json")
```

#### Paramètres par défaut

```python
{
    # Affichage
    "theme": "light",
    "page_size": 10,
    "max_rows_display": 1000,
    "precision": 2,
    "show_index": True,
    
    # Données
    "auto_save": False,
    "auto_save_interval": 300,
    "max_memory_mb": 1024,
    "cache_enabled": True,
    
    # Analyse
    "confidence_level": 0.95,
    "random_seed": 42,
    "n_jobs": -1,
    
    # Export
    "default_export_format": "csv",
    "include_index_export": False,
    
    # Interface
    "show_code": True,
    "show_tooltips": True,
    "animation_enabled": True,
    
    # Avancé
    "debug_mode": False,
    "log_actions": True,
    "session_timeout": 3600
}
```

### 3. Journalisation des Actions

Traçabilité complète des actions utilisateur.

```python
# Enregistrer une action
app_manager.log_action("dataset_loaded", {
    "dataset": "diamonds",
    "rows": 200,
    "columns": 10
})

app_manager.log_action("model_trained", {
    "model": "linear_regression",
    "accuracy": 0.85
})

# Obtenir l'historique
all_actions = app_manager.get_action_history()
recent = app_manager.get_action_history(limit=10)
specific = app_manager.get_action_history(action_type="dataset_loaded")
by_session = app_manager.get_action_history(session_id="sess-123")

# Effacer l'historique
app_manager.clear_action_history()  # Tout
app_manager.clear_action_history(session_id="sess-123")  # Session spécifique

# Désactiver la journalisation
app_manager.set_setting("log_actions", False)
```

#### Structure d'une action

```python
{
    "timestamp": "2026-01-13 10:30:45",
    "action": "dataset_loaded",
    "details": {
        "dataset": "diamonds",
        "rows": 200
    },
    "session_id": "session-abc123"
}
```

### 4. Gestion du Cache

Cache en mémoire pour résultats temporaires.

```python
# Mettre en cache
app_manager.cache_set("correlation_matrix", matrix_data)
app_manager.cache_set("model_results", {"accuracy": 0.92})

# Récupérer du cache
matrix = app_manager.cache_get("correlation_matrix")
results = app_manager.cache_get("model_results", default={})

# Vérifier l'existence
if "model_results" in app_manager.cache_keys():
    results = app_manager.cache_get("model_results")

# Supprimer du cache
app_manager.cache_delete("old_data")

# Vider le cache
app_manager.cache_clear()

# Lister les clés
all_keys = app_manager.cache_keys()

# Désactiver le cache
app_manager.set_setting("cache_enabled", False)
```

### 5. Intégration avec DataManager

Accès unifié aux datasets.

```python
# Accéder au DataManager
dm = app_manager.data_manager

# Obtenir le dataset actuel
df = app_manager.get_current_dataset()

# Utiliser le DataManager
datasets = dm.get_dataset_names()
dm.set_active_dataset("diamonds")

# Journaliser automatiquement
df = dm.get_dataset("diamonds")
app_manager.log_action("dataset_accessed", {
    "name": "diamonds",
    "shape": str(df.shape)
})
```

### 6. Intégration avec ProjectManager

Accès unifié aux projets.

```python
# Accéder au ProjectManager
pm = app_manager.project_manager

# Obtenir le projet actuel
project = app_manager.get_current_project()

# Créer un projet et journaliser
project = pm.create_project("My Analysis")
app_manager.log_action("project_created", {
    "project_id": project.id,
    "name": project.name
})

# Ajouter dataset au projet
dm = app_manager.data_manager
dm.add_dataset_to_project("diamonds")
app_manager.log_action("dataset_added", {
    "project": project.name,
    "dataset": "diamonds"
})
```

### 7. Gestion d'État

Sauvegarde et restauration complète de l'état.

```python
# Exporter l'état complet
success, msg = app_manager.export_state(
    "app_state.pkl",
    include_sessions=True,
    include_data=True,
    include_projects=True
)

# Exporter seulement les paramètres et le cache
success, msg = app_manager.export_state(
    "light_state.pkl",
    include_sessions=False,
    include_data=False
)

# Importer l'état (remplacer)
success, msg = app_manager.import_state(
    "app_state.pkl",
    restore_sessions=True,
    restore_data=True,
    merge=False  # Remplacer l'état actuel
)

# Importer l'état (fusionner)
success, msg = app_manager.import_state(
    "settings_only.pkl",
    restore_sessions=False,
    merge=True  # Fusionner avec l'état actuel
)
```

### 8. Résumé de Statut

Vue d'ensemble de l'application.

```python
summary = app_manager.get_status_summary()

print(f"Sessions: {summary['sessions']['total']}")
print(f"Active: {summary['sessions']['active_id']}")

print(f"Datasets: {summary['data']['datasets']}")
print(f"Active: {summary['data']['active_dataset']}")

print(f"Projects: {summary['projects']['total']}")
print(f"Active: {summary['projects']['active']}")

print(f"Cache items: {summary['cache']['size']}")
print(f"Cache enabled: {summary['cache']['enabled']}")

print(f"Actions logged: {summary['actions']['total']}")
```

## Workflows Typiques

### Workflow 1 : Session Utilisateur Complète

```python
# 1. Créer et activer une session
session = app_manager.create_session("analyst@company.com")
app_manager.set_active_session(session.id)

# 2. Configurer les préférences utilisateur
session.set_setting("theme", "dark")
session.set_setting("auto_save", True)

# 3. Charger des données
dm = app_manager.data_manager
df = dm.get_dataset("diamonds")
app_manager.log_action("data_loaded", {"dataset": "diamonds"})

# 4. Effectuer une analyse
from sklearn.linear_model import LinearRegression
# ... analyse ...
app_manager.log_action("analysis_completed", {"r2": 0.85})

# 5. Mettre en cache les résultats
app_manager.cache_set("analysis_results", results)

# 6. Créer un projet
pm = app_manager.project_manager
project = pm.create_project("Diamond Analysis")
dm.add_dataset_to_project("diamonds")

# 7. Sauvegarder l'état
app_manager.export_state("analysis_state.pkl", include_sessions=True)
```

### Workflow 2 : Restauration d'État

```python
# 1. Importer l'état sauvegardé
success, msg = app_manager.import_state(
    "analysis_state.pkl",
    restore_sessions=True,
    restore_data=True
)

# 2. Restaurer la session
if success:
    # Récupérer la session précédente
    sessions = app_manager.list_sessions()
    if sessions:
        app_manager.set_active_session(sessions[0].id)
    
    # Récupérer les résultats en cache
    results = app_manager.cache_get("analysis_results")
    
    # Reprendre le travail
    project = app_manager.get_current_project()
    df = app_manager.get_current_dataset()
```

### Workflow 3 : Multi-Utilisateurs

```python
# Utilisateur 1
alice = app_manager.create_session("alice@company.com")
app_manager.set_active_session(alice.id)
alice.set_data("working_on", "sales_analysis")
app_manager.log_action("user_login", {"user": "alice"})

# Utilisateur 2
bob = app_manager.create_session("bob@company.com")
app_manager.set_active_session(bob.id)
bob.set_data("working_on", "customer_segmentation")
app_manager.log_action("user_login", {"user": "bob"})

# Chaque utilisateur a son propre contexte
app_manager.set_active_session(alice.id)
alice_work = app_manager.get_session().get_data("working_on")

app_manager.set_active_session(bob.id)
bob_work = app_manager.get_session().get_data("working_on")
```

## Bonnes Pratiques

### 1. Journalisation Structurée

```python
# ✓ Bon - Actions claires avec contexte
app_manager.log_action("model_trained", {
    "model_type": "random_forest",
    "features": ["age", "income"],
    "accuracy": 0.92,
    "duration_ms": 1250
})

# ✗ Mauvais - Trop vague
app_manager.log_action("done")
```

### 2. Nommage de Cache

```python
# ✓ Bon - Clés descriptives et uniques
app_manager.cache_set("correlation_matrix_diamonds_2026", matrix)
app_manager.cache_set("model_rf_v2_predictions", predictions)

# ✗ Mauvais - Clés génériques
app_manager.cache_set("data", something)
app_manager.cache_set("result", result)
```

### 3. Gestion de Session

```python
# ✓ Bon - Nettoyer régulièrement
app_manager.cleanup_inactive_sessions(timeout_seconds=1800)

# ✓ Bon - Vérifier l'existence
session = app_manager.get_session(session_id)
if session:
    session.update_activity()

# ✗ Mauvais - Ne jamais nettoyer les sessions
```

### 4. Utilisation du Cache

```python
# ✓ Bon - Vérifier avant d'utiliser
result = app_manager.cache_get("expensive_computation")
if result is None:
    result = perform_expensive_computation()
    app_manager.cache_set("expensive_computation", result)

# ✗ Mauvais - Supposer que le cache existe toujours
result = app_manager.cache_get("computation")  # Peut être None
result.shape  # Erreur si None!
```

## Tests

```bash
# Exécuter tous les tests
pytest tests/utils/test_app_manager.py -v

# Tests spécifiques
pytest tests/utils/test_app_manager.py::TestSessionManagement -v
pytest tests/utils/test_app_manager.py::TestSettingsManagement -v

# Couverture
pytest tests/utils/test_app_manager.py --cov=aiml_dash.utils.app_manager
```

## Exemples

Voir les exemples complets dans `examples/app_manager_example.py` :

```bash
python examples/app_manager_example.py
```

## Performance et Limites

### Considérations de Performance

- **Mémoire** : Le cache et les sessions sont en mémoire - surveiller l'utilisation
- **Sessions** : Nettoyer régulièrement les sessions inactives
- **Historique** : L'historique d'actions peut devenir volumineux

### Limitations

- Pas de persistance automatique (utiliser export_state)
- Cache en mémoire uniquement (pas Redis/Memcached)
- Sessions perdues au redémarrage (sauf si exportées)
- Pas de partage entre processus (singleton par processus)

## API Complète

### AppManager

| Méthode | Description |
|---------|-------------|
| `create_session(user_id)` | Créer une nouvelle session |
| `get_session(session_id)` | Obtenir une session |
| `set_active_session(session_id)` | Définir la session active |
| `list_sessions()` | Lister toutes les sessions |
| `remove_session(session_id)` | Supprimer une session |
| `cleanup_inactive_sessions(timeout)` | Nettoyer les sessions inactives |
| `get_setting(key, default)` | Obtenir un paramètre |
| `set_setting(key, value)` | Définir un paramètre |
| `update_settings(dict)` | Mettre à jour plusieurs paramètres |
| `reset_settings()` | Réinitialiser aux valeurs par défaut |
| `export_settings(path)` | Exporter les paramètres |
| `import_settings(path)` | Importer les paramètres |
| `log_action(action, details)` | Enregistrer une action |
| `get_action_history(...)` | Obtenir l'historique |
| `clear_action_history()` | Effacer l'historique |
| `cache_set(key, value, ttl)` | Mettre en cache |
| `cache_get(key, default)` | Récupérer du cache |
| `cache_delete(key)` | Supprimer du cache |
| `cache_clear()` | Vider le cache |
| `cache_keys()` | Lister les clés |
| `export_state(path, ...)` | Exporter l'état |
| `import_state(path, ...)` | Importer l'état |
| `get_current_dataset()` | Dataset actuel (DataManager) |
| `get_current_project()` | Projet actuel (ProjectManager) |
| `get_status_summary()` | Résumé de statut |

### Session

| Méthode | Description |
|---------|-------------|
| `set_data(key, value)` | Définir des données |
| `get_data(key, default)` | Obtenir des données |
| `set_setting(key, value)` | Définir un paramètre |
| `get_setting(key, default)` | Obtenir un paramètre |
| `add_to_history(action, details)` | Ajouter à l'historique |
| `update_activity()` | Mettre à jour l'activité |
| `to_dict()` | Convertir en dict |
| `from_dict(data)` | Créer depuis dict |

## Changelog

### Version 1.0 (2026-01-13)
- ✨ Création initiale du AppManager
- ✓ Gestion des sessions multi-utilisateurs
- ✓ Système de paramètres configurables
- ✓ Journalisation complète des actions
- ✓ Cache en mémoire avec TTL
- ✓ Export/Import d'état
- ✓ Intégration DataManager et ProjectManager
- ✓ 37 tests unitaires (100% pass)
