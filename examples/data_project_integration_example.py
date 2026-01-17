"""
Exemple d'utilisation de l'intégration DataManager et ProjectManager
=====================================================================

Ce script démontre comment utiliser conjointement DataManager et ProjectManager
pour gérer des datasets et des projets dans AIML Dash.
"""

import pandas as pd
from aiml_dash.managers.data_manager import data_manager
from aiml_dash.managers.project_manager import ProjectManager, Experiment


def exemple_1_creer_projet_avec_datasets():
    """
    Exemple 1: Créer un projet à partir de datasets existants dans DataManager.
    """
    print("\n" + "=" * 70)
    print("EXEMPLE 1: Créer un projet avec des datasets existants")
    print("=" * 70)

    # 1. Ajouter des datasets au DataManager
    df_sales = pd.DataFrame({
        "product": ["A", "B", "C", "A", "B"],
        "quantity": [10, 20, 15, 30, 25],
        "price": [100, 200, 150, 100, 200],
        "region": ["Nord", "Sud", "Est", "Nord", "Ouest"],
    })

    df_customers = pd.DataFrame({
        "customer_id": [1, 2, 3, 4, 5],
        "name": ["Alice", "Bob", "Charlie", "Diana", "Eve"],
        "region": ["Nord", "Sud", "Est", "Nord", "Ouest"],
    })

    data_manager.add_dataset("sales", df_sales, description="Données de ventes")
    data_manager.add_dataset("customers", df_customers, description="Données clients")

    print(f"✓ Datasets ajoutés: {data_manager.get_dataset_names()}")

    # 2. Créer un projet avec ces datasets
    success, msg = data_manager.create_project_from_datasets(
        project_name="Analyse Commerciale",
        dataset_names=["sales", "customers"],
        description="Analyse des ventes par région",
        project_type="Business Analytics",
    )

    print(f"✓ Projet créé: {msg}")

    # 3. Vérifier les informations du projet
    project_info = data_manager.get_active_project_info()
    print(f"\nInformations du projet:")
    print(f"  - Nom: {project_info['name']}")
    print(f"  - Type: {project_info['type']}")
    print(f"  - Datasets: {project_info['num_datasets']}")
    print(f"  - Expériences: {project_info['num_experiments']}")


def exemple_2_ajouter_experiences():
    """
    Exemple 2: Ajouter des expériences à un projet actif.
    """
    print("\n" + "=" * 70)
    print("EXEMPLE 2: Ajouter des expériences au projet")
    print("=" * 70)

    # Récupérer le projet actif
    pm = data_manager.project_manager
    project = pm.get_active_project()

    if project is None:
        print("⚠ Aucun projet actif. Exécutez d'abord exemple_1_creer_projet_avec_datasets()")
        return

    # Créer des expériences
    exp1 = Experiment(
        name="Régression Linéaire - Prix vs Quantité",
        exp_type="Linear Regression",
        description="Prédire les prix en fonction des quantités",
    )
    exp1.set_parameters({"features": ["quantity"], "target": "price", "test_size": 0.2})
    exp1.set_results({"r2_score": 0.85, "mse": 125.3, "mae": 10.2})
    exp1.update_status("Completed")

    exp2 = Experiment(
        name="Analyse par Région", exp_type="Descriptive Statistics", description="Statistiques descriptives par région"
    )
    exp2.set_parameters({"groupby": "region", "metrics": ["mean", "sum", "count"]})
    exp2.update_status("Running")

    # Ajouter les expériences au projet
    project.add_experiment(exp1)
    project.add_experiment(exp2)

    print(f"✓ {len(project.list_experiments())} expériences ajoutées au projet")

    # Afficher les expériences
    for exp in project.list_experiments():
        print(f"\n  - {exp.name}")
        print(f"    Type: {exp.type}")
        print(f"    Statut: {exp.status}")
        if exp.results:
            print(f"    Résultats: {exp.results}")


def exemple_3_synchroniser_depuis_projet():
    """
    Exemple 3: Synchroniser les datasets d'un projet dans DataManager.
    """
    print("\n" + "=" * 70)
    print("EXEMPLE 3: Synchroniser datasets depuis le projet")
    print("=" * 70)

    # Effacer les datasets du DataManager (sauf samples)
    for name in list(data_manager.datasets.keys()):
        if name not in ["diamonds", "titanic"]:
            data_manager.remove_dataset(name)

    print(f"✓ DataManager vidé. Datasets restants: {data_manager.get_dataset_names()}")

    # Synchroniser avec le projet actif
    success, msg = data_manager.sync_with_active_project()
    print(f"✓ Synchronisation: {msg}")

    # Vérifier les datasets
    print(f"✓ Datasets après sync: {data_manager.get_dataset_names()}")

    # Afficher un aperçu
    sales = data_manager.get_dataset("sales")
    if sales is not None:
        print(f"\nAperçu du dataset 'sales':")
        print(sales.head())


def exemple_4_gerer_verrous_projet():
    """
    Exemple 4: Gérer les verrous de projet.
    """
    print("\n" + "=" * 70)
    print("EXEMPLE 4: Gestion des verrous de projet")
    print("=" * 70)

    pm = data_manager.project_manager
    project = pm.get_active_project()

    if project is None:
        print("⚠ Aucun projet actif")
        return

    # Verrouiller le projet
    project.lock(user="alice@example.com")
    print(f"✓ Projet verrouillé par: {project.locked_by}")
    print(f"  Verrouillé à: {project.locked_at}")

    # Tenter de modifier (devrait échouer)
    try:
        project.lock(user="bob@example.com")
    except ValueError as e:
        print(f"✗ Erreur attendue: {e}")

    # Déverrouiller
    project.unlock(user="alice@example.com")
    print(f"✓ Projet déverrouillé")

    # Info du projet
    info = data_manager.get_active_project_info()
    print(f"  Verrouillé: {info['is_locked']}")


def exemple_5_exporter_importer_projet():
    """
    Exemple 5: Exporter et importer un projet.
    """
    print("\n" + "=" * 70)
    print("EXEMPLE 5: Export/Import de projet")
    print("=" * 70)

    pm = data_manager.project_manager
    project = pm.get_active_project()

    if project is None:
        print("⚠ Aucun projet actif")
        return

    # Exporter en JSON (sans données)
    print("\n1. Export JSON (métadonnées seulement)")
    pm.export_project(project.id, "/tmp/projet_meta.json", file_format="json", include_data=False)
    print(f"✓ Projet exporté: /tmp/projet_meta.json")

    # Exporter en JSON (avec données)
    print("\n2. Export JSON (avec données)")
    pm.export_project(project.id, "/tmp/projet_complet.json", file_format="json", include_data=True)
    print(f"✓ Projet exporté: /tmp/projet_complet.json")

    # Exporter en pickle (avec données)
    print("\n3. Export Pickle (avec données)")
    pm.export_project(project.id, "/tmp/projet.pkl", file_format="pickle")
    print(f"✓ Projet exporté: /tmp/projet.pkl")

    # Importer depuis JSON
    print("\n4. Import depuis JSON")
    imported = pm.import_project("/tmp/projet_complet.json", file_format="json")
    print(f"✓ Projet importé: {imported.name}")
    print(f"  - Datasets: {len(imported.list_datasets())}")
    print(f"  - Expériences: {len(imported.list_experiments())}")


def exemple_6_gerer_plusieurs_projets():
    """
    Exemple 6: Gérer plusieurs projets.
    """
    print("\n" + "=" * 70)
    print("EXEMPLE 6: Gestion de plusieurs projets")
    print("=" * 70)

    pm = data_manager.project_manager

    # Créer plusieurs projets
    proj1 = pm.create_project("Projet Marketing", description="Analyse marketing")
    proj2 = pm.create_project("Projet Finance", description="Analyse financière")
    proj3 = pm.create_project("Projet RH", description="Analyse RH")

    print(f"✓ {len(pm.list_projects())} projets créés")

    # Lister tous les projets
    print("\nListe des projets:")
    for proj in pm.list_projects():
        status = "🔒 Verrouillé" if proj.locked else "🔓 Déverrouillé"
        active = "⭐ ACTIF" if proj.id == pm.active_project_id else ""
        print(f"  - {proj.name} ({proj.project_type}) {status} {active}")

    # Changer de projet actif
    pm.set_active_project(proj2.id)
    print(f"\n✓ Projet actif changé: {pm.get_active_project().name}")

    # Archiver un projet
    proj3.archive()
    print(f"✓ Projet '{proj3.name}' archivé")

    # Résumé d'un projet
    summary = pm.get_project_summary(proj1.id)
    print(f"\nRésumé du projet '{summary['name']}':")
    print(f"  - Statut: {summary['status']}")
    print(f"  - Datasets: {summary['num_datasets']}")
    print(f"  - Expériences: {summary['num_experiments']}")


def main():
    """Exécuter tous les exemples."""
    print("\n" + "=" * 70)
    print(" EXEMPLES D'INTÉGRATION DataManager et ProjectManager")
    print("=" * 70)

    try:
        exemple_1_creer_projet_avec_datasets()
        exemple_2_ajouter_experiences()
        exemple_3_synchroniser_depuis_projet()
        exemple_4_gerer_verrous_projet()
        exemple_5_exporter_importer_projet()
        exemple_6_gerer_plusieurs_projets()

        print("\n" + "=" * 70)
        print(" ✓ Tous les exemples ont été exécutés avec succès!")
        print("=" * 70 + "\n")

    except Exception as e:
        print(f"\n⚠ Erreur lors de l'exécution: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
