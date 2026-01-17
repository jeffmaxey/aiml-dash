# Common Components Usage Guide

Ce guide explique comment utiliser les composants réutilisables de `aiml_dash/components/common.py` pour créer des pages cohérentes et maintenables.

## 📚 Table des Matières

1. [Structure de page](#structure-de-page)
2. [Composants de notification](#composants-de-notification)
3. [Composants de layout](#composants-de-layout)
4. [Contrôles d'entrée](#contrôles-dentrée)
5. [Boutons d'action](#boutons-daction)
6. [Composants utilitaires](#composants-utilitaires)
7. [Exemples complets](#exemples-complets)

---

## Structure de Page

### 1. Créer un en-tête de page

```python
from aiml_dash.components.common import create_page_header

create_page_header(
    title="Titre de la Page",
    description="Description de ce que fait cette page",
    icon="carbon:chart-line"  # Icône Iconify
)
```

### 2. Layout en deux colonnes (Contrôles à gauche, Résultats à droite)

```python
from aiml_dash.components.common import create_two_column_layout, create_control_card, create_results_card

layout = create_two_column_layout(
    # Colonne gauche - Contrôles
    create_control_card(
        [
            # Vos contrôles ici
            dmc.Select(...),
            dmc.Button(...),
        ],
        title="Settings"  # Optionnel
    ),
    # Colonne droite - Résultats  
    create_results_card(
        [
            # Vos résultats ici
            dcc.Graph(...),
            html.Div(...),
        ]
    ),
    left_span=4,  # Par défaut
    right_span=8, # Par défaut
)
```

---

## Composants de Notification

### Notifications de succès/erreur

```python
from aiml_dash.components.common import create_success_notification, create_error_notification

# Dans un callback
@callback(Output("notification-div", "children"), ...)
def my_callback(...):
    try:
        # Votre logique
        return create_success_notification(
            message="Operation completed successfully!",
            title="Success"  # Optionnel, défaut = "Success"
        )
    except Exception as e:
        return create_error_notification(
            message=str(e),
            title="Error"  # Optionnel, défaut = "Error"
        )
```

### Alertes (inline)

```python
from aiml_dash.components.common import (
    create_error_alert,
    create_warning_alert,
    create_info_alert
)

# Alerte d'erreur
create_error_alert(
    message="Please select a dataset before proceeding",
    title="Missing Input"
)

# Alerte d'avertissement  
create_warning_alert(
    message="This operation may take several minutes",
    title="Please Wait"
)

# Alerte d'information
create_info_alert(
    message="Click 'Run Analysis' to see results",
    title="Info"
)
```

---

## Composants de Layout

### Cards (boîtes conteneurs)

```python
from aiml_dash.components.common import create_control_card, create_results_card

# Card de contrôles (pour formulaires)
create_control_card(
    [
        dmc.Select(...),
        dmc.NumberInput(...),
        dmc.Button(...),
    ],
    title="Configuration"  # Titre optionnel
)

# Card de résultats (pour affichage)
create_results_card(
    dcc.Graph(id="my-plot"),
    title="Results"  # Titre optionnel
)
```

### État vide

```python
from aiml_dash.components.common import create_empty_state

# Quand aucune donnée n'est disponible
create_empty_state(
    message="No dataset selected",
    icon="carbon:data-base",  # Par défaut
    height="400px"  # Par défaut
)
```

---

## Contrôles d'Entrée

### Sélecteur de dataset

```python
from aiml_dash.components.common import create_dataset_selector

create_dataset_selector(
    selector_id="my-dataset-selector",
    label="Dataset",  # Par défaut
    required=True     # Par défaut
)
```

### Entrée numérique

```python
from aiml_dash.components.common import create_numeric_input

create_numeric_input(
    input_id="confidence-level",
    label="Confidence Level",
    value=0.95,
    min_val=0.5,
    max_val=0.99,
    step=0.01,
    description="Statistical confidence level"  # Optionnel
)
```

### Contrôle segmenté (Radio buttons stylisés)

```python
from aiml_dash.components.common import create_segmented_control

create_segmented_control(
    control_id="view-mode",
    options=[
        {"label": "Table", "value": "table"},
        {"label": "Chart", "value": "chart"},
        {"label": "Stats", "value": "stats"},
    ],
    default_value="table",  # Optionnel
    label="View Mode",      # Optionnel
    full_width=True         # Par défaut
)
```

---

## Boutons d'Action

### Bouton d'action standardisé

```python
from aiml_dash.components.common import create_action_button

# Bouton principal (Run, Execute, etc.)
create_action_button(
    button_id="run-analysis",
    label="Run Analysis",
    icon="carbon:play",      # Par défaut
    color="blue",            # Par défaut
    variant="filled",        # Par défaut
    full_width=True,         # Par défaut
    size="md"                # Par défaut, peut être "sm", "md", "lg"
)

# Bouton secondaire (Export, Download, etc.)
create_action_button(
    button_id="export-data",
    label="Export to CSV",
    icon="carbon:download",
    variant="light",
    color="gray"
)
```

### Bouton d'upload

```python
from aiml_dash.components.common import create_upload_button

create_upload_button(
    upload_id="file-upload",
    button_text="Upload File",  # Par défaut
    icon="carbon:upload",       # Par défaut
    multiple=False              # Par défaut
)
```

### Section d'export

```python
from aiml_dash.components.common import create_export_section

# Crée automatiquement les boutons CSV et/ou Excel avec downloads
create_export_section(
    export_csv_id="export-csv",
    export_excel_id="export-excel",
    show_excel=False  # True pour ajouter le bouton Excel
)
```

---

## Composants Utilitaires

### Sélecteur de variables

```python
from aiml_dash.components.common import create_variable_selector

# Sélection multiple (par défaut)
create_variable_selector(
    var_id="x-variables",
    label="X Variables",
    multiple=True,   # Par défaut
    required=False,  # Par défaut
    description="Select one or more variables"  # Optionnel
)

# Sélection simple
create_variable_selector(
    var_id="y-variable",
    label="Y Variable",
    multiple=False,
    required=True
)
```

### Section de filtres

```python
from aiml_dash.components.common import create_filter_section

# Crée un accordéon avec filtres, tri et slice
create_filter_section()
```

### Onglets (Tabs)

```python
from aiml_dash.components.common import create_tabs

create_tabs(
    tabs_id="result-tabs",
    tabs_data=[
        {
            "value": "summary",
            "label": "Summary",
            "icon": "carbon:report",
            "children": dmc.Text("Summary content")
        },
        {
            "value": "plot",
            "label": "Plot",
            "icon": "carbon:chart-line",
            "children": dcc.Graph(...)
        },
    ]
)
```

### AG Grid

```python
from aiml_dash.components.common import create_ag_grid

create_ag_grid(
    grid_id="data-grid",
    row_data=data_dict_list,  # Liste de dictionnaires
    column_defs=[
        {"field": "name", "checkboxSelection": True},  # Première colonne avec checkbox
        {"field": "value"},
    ],
    # Configuration additionnelle optionnelle
    style={"height": "600px"}  # Par défaut
)
```

---

## Exemples Complets

### Exemple 1: Page d'analyse simple

```python
from dash import html, dcc, callback, Input, Output
import dash_mantine_components as dmc
from aiml_dash.components.common import (
    create_page_header,
    create_two_column_layout,
    create_control_card,
    create_results_card,
    create_dataset_selector,
    create_action_button,
    create_empty_state,
    create_success_notification,
    create_error_notification,
)
from aiml_dash.utils.app_manager import app_manager


def layout():
    return dmc.Container([
        create_page_header(
            "My Analysis",
            "Perform statistical analysis on your data",
            icon="carbon:analytics"
        ),
        
        create_two_column_layout(
            # Contrôles
            create_control_card([
                create_dataset_selector(selector_id="dataset"),
                dmc.Select(
                    id="variable",
                    label="Variable",
                    placeholder="Select variable...",
                    data=[],
                ),
                create_action_button(
                    button_id="run-btn",
                    label="Run Analysis",
                ),
            ], title="Settings"),
            
            # Résultats
            create_results_card(
                html.Div(id="results"),
                title="Results"
            ),
        ),
        
        html.Div(id="notification"),
    ])


@callback(
    Output("results", "children"),
    Output("notification", "children"),
    Input("run-btn", "n_clicks"),
    State("dataset", "value"),
    State("variable", "value"),
    prevent_initial_call=True,
)
def run_analysis(n_clicks, dataset, variable):
    if not dataset or not variable:
        return (
            create_empty_state("Please select dataset and variable"),
            create_error_notification("Missing inputs")
        )
    
    try:
        df = app_manager.data_manager.get_dataset(dataset)
        result = df[variable].describe()
        
        return (
            html.Pre(str(result)),
            create_success_notification("Analysis completed!")
        )
    except Exception as e:
        return (
            create_empty_state("Error running analysis"),
            create_error_notification(str(e))
        )
```

### Exemple 2: Page avec onglets

```python
from aiml_dash.components.common import create_tabs

# Dans votre layout
create_tabs(
    tabs_id="analysis-tabs",
    tabs_data=[
        {
            "value": "data",
            "label": "Data",
            "icon": "carbon:data-table",
            "children": create_results_card(
                html.Div(id="data-view")
            )
        },
        {
            "value": "plot",
            "label": "Visualization",
            "icon": "carbon:chart-line",
            "children": create_results_card(
                dcc.Graph(id="plot")
            )
        },
        {
            "value": "stats",
            "label": "Statistics",
            "icon": "carbon:calculator",
            "children": create_results_card(
                html.Div(id="stats")
            )
        },
    ]
)
```

---

## 🎨 Conseils de Style

1. **Cohérence**: Utilisez toujours les mêmes composants pour les mêmes fonctionnalités
2. **Hiérarchie**: 
   - Control cards à gauche (span=4)
   - Results cards à droite (span=8)
3. **Feedback**: Toujours fournir des notifications pour les actions utilisateur
4. **États vides**: Afficher des messages clairs quand il n'y a pas de données
5. **Icons**: Utilisez des icônes du pack "carbon" pour la cohérence

## 🔧 Migration d'un Fichier Existant

### Avant:
```python
dmc.Grid([
    dmc.GridCol([
        dmc.Card([
            dmc.Stack([
                dmc.Select(...),
                dmc.Button("Run", leftSection=DashIconify(icon="carbon:play")),
            ], gap="md")
        ], withBorder=True, radius="md", p="md"),
    ], span=4),
    dmc.GridCol([
        dmc.Card([
            html.Div(id="results")
        ], withBorder=True, radius="md", p="md"),
    ], span=8),
])
```

### Après:
```python
create_two_column_layout(
    create_control_card([
        dmc.Select(...),
        create_action_button("run-btn", "Run"),
    ]),
    create_results_card(
        html.Div(id="results")
    ),
)
```

---

## 📝 Checklist pour Nouvelles Pages

- [ ] Importer les composants nécessaires de `aiml_dash.components.common`
- [ ] Utiliser `create_page_header()` pour l'en-tête
- [ ] Utiliser `create_two_column_layout()` pour la structure principale
- [ ] Utiliser `create_control_card()` pour les contrôles
- [ ] Utiliser `create_results_card()` pour les résultats
- [ ] Utiliser `create_action_button()` pour les boutons principaux
- [ ] Utiliser `create_empty_state()` pour les états sans données
- [ ] Utiliser `create_success_notification()` / `create_error_notification()` pour le feedback
- [ ] Tester la page sur mobile et desktop
- [ ] Vérifier la compilation: `python -m py_compile your_page.py`

---

## 🚀 Prochaines Étapes

Pour refactoriser une page existante:

1. Identifier les patterns répétitifs (Cards, Buttons, Grids)
2. Remplacer par les composants équivalents de common.py
3. Mettre à jour les imports
4. Tester la fonctionnalité
5. Valider la compilation

**Avantages:**
- ✅ Moins de code répétitif
- ✅ Interface cohérente
- ✅ Maintenance simplifiée
- ✅ Changements centralisés
