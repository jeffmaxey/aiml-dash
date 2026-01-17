# Architecture des Managers - AIML Dash

Ce document présente l'architecture complète des gestionnaires de l'application AIML Dash.

## Vue d'ensemble

```
┌──────────────────────────────────────────────────────────────┐
│                        AppManager                             │
│              Orchestration Centrale de l'Application          │
│                                                                │
│  • Sessions (multi-utilisateurs)                              │
│  • Settings (configuration globale)                           │
│  • Action History (traçabilité complète)                      │
│  • Cache (résultats temporaires)                              │
│  • State Management (import/export)                           │
└────────────────────┬─────────────────────┬────────────────────┘
                     │                     │
                     ▼                     ▼
        ┌────────────────────┐   ┌────────────────────┐
        │   DataManager      │   │  ProjectManager    │
        │   (Singleton)      │   │   (Singleton)      │
        │                    │   │                    │
        │ • Datasets         │   │ • Projects         │
        │ • Metadata         │   │ • Experiments      │
        │ • Active dataset   │   │ • Datasets         │
        │ • Load/Export      │   │ • Locking          │
        │ • Filters          │   │ • Serialization    │
        └────────────────────┘   └────────────────────┘
```

## Les Trois Managers

### 1. AppManager (`app_manager.py`)
**Rôle** : Gestionnaire central et orchestrateur

- ✅ **Sessions** : Multi-utilisateurs avec contexte isolé
- ✅ **Settings** : Configuration globale de l'application
- ✅ **Actions** : Journalisation complète des actions
- ✅ **Cache** : Stockage temporaire de résultats
- ✅ **State** : Export/import complet de l'état
- ✅ **Integration** : Accès unifié à DataManager et ProjectManager

**Fichiers** :
- `aiml_dash/utils/app_manager.py` (850 lignes)
- `tests/utils/test_app_manager.py` (37 tests ✓)
- `examples/app_manager_example.py` (9 exemples)
- `APP_MANAGER_GUIDE.md` (documentation complète)

### 2. DataManager (`data_manager.py`)
**Rôle** : Gestion des datasets au niveau application

- ✅ **Datasets** : Stockage en mémoire avec métadonnées
- ✅ **Load/Export** : CSV, Excel, JSON, Pickle
- ✅ **Filters** : Query, sort, row selection
- ✅ **State** : Export/import complet
- ✅ **Integration** : Synchronisation avec ProjectManager

**Fichiers** :
- `aiml_dash/utils/data_manager.py` (850+ lignes)
- `tests/utils/test_data_manager.py` (32 tests ✓)
- `tests/utils/test_data_project_integration.py` (14 tests ✓)
- `DATA_PROJECT_INTEGRATION.md` (guide d'intégration)

### 3. ProjectManager (`project_manager.py`)
**Rôle** : Gestion des projets, expériences et datasets

- ✅ **Projects** : Conteneurs pour expériences et datasets
- ✅ **Experiments** : Paramètres, résultats, statut
- ✅ **Datasets** : Données liées aux projets
- ✅ **Locking** : Verrouillage pour édition exclusive
- ✅ **Serialization** : JSON et Pickle avec/sans données

**Fichiers** :
- `aiml_dash/utils/project_manager.py` (781 lignes)
- `tests/utils/test_project_manager.py` (26 tests ✓)
- `examples/data_project_integration_example.py` (6 exemples)

## Patterns de Design

### Singleton Pattern
Tous les managers utilisent le pattern Singleton pour garantir une instance unique :

```python
class Manager:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
        
    def __init__(self):
        if hasattr(self, '_initialized') and self._initialized:
            return
        # Initialisation...
        self._initialized = True
```

### Lazy Initialization
Les dépendances sont chargées à la demande :

```python
@property
def project_manager(self):
    if self._project_manager is None:
        self._project_manager = ProjectManager()
    return self._project_manager
```

### State Management
Export/import complet de l'état avec sérialisation pickle et JSON.

## Instances Globales

```python
# Accès global recommandé
from aiml_dash.utils.app_manager import app_manager
from aiml_dash.utils.data_manager import data_manager
from aiml_dash.utils.project_manager import ProjectManager

# Utilisation
app_manager.log_action("app_started")
df = data_manager.get_dataset("diamonds")
pm = ProjectManager()
```

## Flux de Données

### Chargement de Données
```
User Upload → DataManager.load_from_file()
                     ↓
            DataManager.add_dataset()
                     ↓
            AppManager.log_action("dataset_loaded")
                     ↓
       [Optional] DataManager.add_dataset_to_project()
                     ↓
            ProjectManager.Project.add_dataset()
```

### Création de Projet
```
User Request → AppManager.project_manager
                     ↓
            ProjectManager.create_project()
                     ↓
            AppManager.log_action("project_created")
                     ↓
            DataManager.add_dataset_to_project()
                     ↓
            Project.add_dataset()
```

### Gestion de Session
```
User Login → AppManager.create_session()
                     ↓
         AppManager.set_active_session()
                     ↓
         Session.set_data() / set_setting()
                     ↓
         AppManager.log_action("session_activity")
```

## Tests et Validation

### Statistiques de Tests

| Manager | Tests | Statut | Couverture |
|---------|-------|--------|------------|
| AppManager | 37 | ✓ Pass | Session, Settings, Actions, Cache, State |
| DataManager | 32 | ✓ Pass | Add, Get, Remove, Export, Import, Filter |
| ProjectManager | 26 | ✓ Pass | Project, Experiment, Dataset, Lock, Serialize |
| Integration | 14 | ✓ Pass | Data-Project sync, bidirectional flow |
| **Total** | **109** | **✓ 100%** | **Complet** |

### Exécuter les Tests

```bash
# Tous les tests
pytest tests/utils/ -v

# Par manager
pytest tests/utils/test_app_manager.py -v
pytest tests/utils/test_data_manager.py -v
pytest tests/utils/test_project_manager.py -v
pytest tests/utils/test_data_project_integration.py -v

# Avec couverture
pytest tests/utils/ --cov=aiml_dash.utils --cov-report=html
```

## Exemples d'Utilisation

### Exemple Complet : Workflow d'Analyse

```python
from aiml_dash.utils.app_manager import app_manager

# 1. Initialiser la session
session = app_manager.create_session("analyst@company.com")
app_manager.set_active_session(session.id)
session.set_setting("theme", "dark")

# 2. Charger des données
dm = app_manager.data_manager
df = dm.get_dataset("diamonds")
app_manager.log_action("data_loaded", {"dataset": "diamonds", "rows": len(df)})

# 3. Créer un projet
pm = app_manager.project_manager
project = pm.create_project("Diamond Analysis 2026")
app_manager.log_action("project_created", {"name": project.name})

# 4. Ajouter dataset au projet
dm.add_dataset_to_project("diamonds")

# 5. Effectuer l'analyse (exemple)
from sklearn.linear_model import LinearRegression
# ... code d'analyse ...
results = {"r2": 0.85, "mse": 125.3}

# 6. Cacher les résultats
app_manager.cache_set("analysis_results", results)
app_manager.log_action("analysis_completed", results)

# 7. Créer une expérience
from aiml_dash.utils.project_manager import Experiment
exp = Experiment(name="Linear Regression", exp_type="Regression")
exp.set_parameters({"features": ["carat"], "target": "price"})
exp.set_results(results)
exp.update_status("Completed")
project.add_experiment(exp)

# 8. Sauvegarder tout
app_manager.export_state("analysis_state.pkl", 
    include_sessions=True, 
    include_data=True, 
    include_projects=True
)

# 9. Résumé
summary = app_manager.get_status_summary()
print(f"Sessions: {summary['sessions']['total']}")
print(f"Datasets: {summary['data']['datasets']}")
print(f"Projects: {summary['projects']['total']}")
print(f"Actions: {summary['actions']['total']}")
```

### Exemple : Restauration d'État

```python
from aiml_dash.utils.app_manager import app_manager

# Restaurer l'état complet
success, msg = app_manager.import_state(
    "analysis_state.pkl",
    restore_sessions=True,
    restore_data=True
)

if success:
    # Reprendre le travail
    session = app_manager.get_session()
    project = app_manager.get_current_project()
    results = app_manager.cache_get("analysis_results")
    
    print(f"Session: {session.user_id}")
    print(f"Project: {project.name}")
    print(f"Results: {results}")
```

## Documentation

### Guides Disponibles

1. **APP_MANAGER_GUIDE.md** : Guide complet de l'AppManager
   - Toutes les fonctionnalités détaillées
   - Exemples de code
   - Bonnes pratiques
   - API complète

2. **DATA_PROJECT_INTEGRATION.md** : Intégration DataManager-ProjectManager
   - Synchronisation bidirectionnelle
   - Workflows typiques
   - Architecture d'intégration

3. **Examples** :
   - `examples/app_manager_example.py` : 9 exemples AppManager
   - `examples/data_project_integration_example.py` : 6 exemples d'intégration

### API Quick Reference

#### AppManager
```python
app_manager.create_session(user_id)
app_manager.get_setting(key, default)
app_manager.log_action(action, details)
app_manager.cache_set(key, value)
app_manager.export_state(path)
app_manager.get_status_summary()
```

#### DataManager
```python
data_manager.add_dataset(name, df, description)
data_manager.get_dataset(name)
data_manager.load_from_file(contents, filename)
data_manager.add_dataset_to_project(name)
data_manager.sync_with_active_project()
```

#### ProjectManager
```python
pm = ProjectManager()
pm.create_project(name, description, project_type)
pm.get_active_project()
pm.export_project(project_id, path, file_format)
```

## Structure des Fichiers

```
aiml_dash/
├── utils/
│   ├── app_manager.py           # AppManager (850 lignes)
│   ├── data_manager.py          # DataManager (850+ lignes)
│   └── project_manager.py       # ProjectManager (781 lignes)
├── tests/
│   └── utils/
│       ├── test_app_manager.py               # 37 tests
│       ├── test_data_manager.py              # 32 tests
│       ├── test_project_manager.py           # 26 tests
│       └── test_data_project_integration.py  # 14 tests
└── examples/
    ├── app_manager_example.py
    └── data_project_integration_example.py

Documentation/
├── APP_MANAGER_GUIDE.md           # Guide AppManager
└── DATA_PROJECT_INTEGRATION.md    # Guide Intégration
```

## Performance et Optimisation

### Considérations Mémoire

- **DataManager** : Datasets en mémoire (utiliser max_memory_mb)
- **AppManager Cache** : Limiter la taille du cache
- **Sessions** : Nettoyer régulièrement (cleanup_inactive_sessions)
- **Action History** : Peut devenir volumineux (clear périodiquement)

### Bonnes Pratiques

1. **Nettoyer régulièrement** :
   ```python
   app_manager.cleanup_inactive_sessions(timeout_seconds=1800)
   app_manager.cache_clear()  # Si besoin
   ```

2. **Utiliser le cache intelligemment** :
   ```python
   result = app_manager.cache_get("key")
   if result is None:
       result = expensive_computation()
       app_manager.cache_set("key", result)
   ```

3. **Journaliser avec contexte** :
   ```python
   app_manager.log_action("model_trained", {
       "model": "rf",
       "accuracy": 0.92,
       "features": feature_names
   })
   ```

4. **Sauvegarder l'état périodiquement** :
   ```python
   if app_manager.get_setting("auto_save"):
       app_manager.export_state("auto_save.pkl")
   ```

## Roadmap Future

### Améliorations Planifiées

- [ ] Support Redis pour cache distribué
- [ ] Persistance automatique configurable
- [ ] Sessions avec authentification OAuth
- [ ] Webhooks pour événements
- [ ] Métriques et monitoring intégrés
- [ ] API REST pour accès externe
- [ ] Dashboard d'administration
- [ ] Support multi-processus

## Support et Contribution

### Rapporter un Bug

Créer une issue GitHub avec :
- Description du problème
- Steps to reproduce
- Version Python et dépendances
- Tests unitaires si possible

### Contribuer

1. Fork le repository
2. Créer une branche feature
3. Ajouter des tests
4. Soumettre une PR

## Licence

Voir LICENSE file dans le repository principal.

---

**Version** : 1.0  
**Date** : 2026-01-13  
**Tests** : 109/109 ✓  
**Couverture** : Complète
