# DataManager et ProjectManager - Intégration

Ce document décrit l'intégration entre `DataManager` et `ProjectManager` dans AIML Dash.

## Vue d'ensemble

Le `DataManager` a été mis à jour pour travailler en synergie avec le `ProjectManager`, permettant une gestion fluide des datasets entre les deux systèmes.

## Fonctionnalités ajoutées

### 1. Accès au ProjectManager

Le `DataManager` maintient une référence lazy au `ProjectManager` via la propriété `project_manager`:

```python
data_manager = DataManager()
project_manager = data_manager.project_manager
```

### 2. Ajouter un dataset au projet actif

```python
# Ajouter un dataset existant dans DataManager au projet actif
success, message = data_manager.add_dataset_to_project("my_dataset")

# Ou spécifier un projet
success, message = data_manager.add_dataset_to_project("my_dataset", project_id="proj-123")
```

### 3. Charger un dataset depuis un projet

```python
# Charger un dataset d'un projet dans DataManager
success, message = data_manager.load_dataset_from_project(
    dataset_id="ds-456",
    dataset_name="imported_data"  # Optionnel
)
```

### 4. Synchroniser avec le projet actif

```python
# Synchroniser tous les datasets du projet actif dans DataManager
success, message = data_manager.sync_with_active_project()
```

### 5. Créer un projet depuis les datasets

```python
# Créer un nouveau projet avec des datasets spécifiques
success, message = data_manager.create_project_from_datasets(
    project_name="Mon Projet",
    dataset_names=["diamonds", "titanic"],  # Optionnel - tous si None
    description="Analyse des données",
    project_type="Analysis"
)
```

### 6. Obtenir les datasets d'un projet

```python
# Obtenir la liste des datasets d'un projet
datasets = data_manager.get_project_datasets()  # Projet actif
datasets = data_manager.get_project_datasets(project_id="proj-123")

# Chaque élément contient: id, name, source, description, rows, columns, size, created
```

### 7. Informations sur le projet actif

```python
# Vérifier s'il y a un projet actif
has_project = data_manager.has_active_project()

# Obtenir les infos du projet actif
info = data_manager.get_active_project_info()
# Retourne: id, name, description, type, created, modified, is_locked, locked_by, 
#           num_experiments, num_datasets
```

## Workflow typique

### Scénario 1 : Importer des datasets existants dans un projet

```python
from aiml_dash.utils.data_manager import data_manager

# 1. Charger des datasets dans DataManager
data_manager.load_from_file(contents, "data.csv")

# 2. Créer un projet avec ces datasets
success, msg = data_manager.create_project_from_datasets(
    project_name="Analyse Marketing",
    description="Analyse des données de ventes"
)

# 3. Le projet est maintenant actif avec les datasets
project_info = data_manager.get_active_project_info()
print(f"Projet: {project_info['name']}, Datasets: {project_info['num_datasets']}")
```

### Scénario 2 : Charger des datasets depuis un projet

```python
# 1. Ouvrir/activer un projet (via ProjectManager)
project_manager = data_manager.project_manager
project_manager.set_active_project("proj-123")

# 2. Synchroniser les datasets dans DataManager
success, msg = data_manager.sync_with_active_project()

# 3. Travailler avec les datasets
df = data_manager.get_dataset("my_dataset")
```

### Scénario 3 : Ajout progressif de datasets

```python
# 1. Créer un projet vide
project_manager = data_manager.project_manager
project = project_manager.create_project("Nouveau Projet")
project_manager.set_active_project(project.id)

# 2. Ajouter des datasets au fur et à mesure
data_manager.load_from_file(contents1, "data1.csv")
data_manager.add_dataset_to_project("data1")

data_manager.load_from_file(contents2, "data2.csv")
data_manager.add_dataset_to_project("data2")

# 3. Vérifier le contenu du projet
datasets = data_manager.get_project_datasets()
print(f"Datasets dans le projet: {len(datasets)}")
```

## Architecture

```
┌─────────────────┐
│  DataManager    │
│  (Singleton)    │
│                 │
│  - datasets     │◄──── Gestion globale des datasets
│  - metadata     │
│  - active_ds    │
└────────┬────────┘
         │
         │ project_manager (lazy)
         │
         ▼
┌─────────────────┐
│ ProjectManager  │
│  (Singleton)    │
│                 │
│  - projects     │◄──── Gestion des projets
│  - active_proj  │
└────────┬────────┘
         │
         │ Contient
         ▼
┌─────────────────┐
│    Project      │
│                 │
│  - experiments  │
│  - datasets     │◄──── Dataset avec données
│  - metadata     │
└─────────────────┘
```

## Tests

Une suite complète de tests d'intégration est disponible dans :
`tests/utils/test_data_project_integration.py`

Exécuter les tests :
```bash
pytest tests/utils/test_data_project_integration.py -v
```

Tous les tests (14/14) passent avec succès ✓

## Notes techniques

- **Lazy import** : Le ProjectManager est importé de manière lazy pour éviter les dépendances circulaires
- **Imports absolus** : Utilisation de `from aiml_dash.utils.project_manager import ...`
- **Singletons** : Les deux managers sont des singletons pour garantir une instance unique
- **Synchronisation** : Les datasets peuvent exister indépendamment dans DataManager ou être liés à un projet
- **Données** : Lors de l'ajout d'un dataset à un projet, les données sont copiées (pas de référence partagée)

## Limitations

- Le `ProjectManager` doit être disponible (installé et importable)
- Les datasets volumineux peuvent consommer beaucoup de mémoire s'ils existent à la fois dans DataManager et Project
- La synchronisation n'est pas automatique - elle doit être déclenchée explicitement

## Améliorations futures

- [ ] Synchronisation automatique optionnelle
- [ ] Gestion des références partagées pour les gros datasets
- [ ] Historique des modifications de datasets
- [ ] Validation des datasets avant ajout au projet
- [ ] Support pour les datasets distribués
