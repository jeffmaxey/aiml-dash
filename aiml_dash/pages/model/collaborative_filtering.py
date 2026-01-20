"""
Collaborative Filtering Page
=============================

Build recommendation systems using collaborative filtering.
"""

import dash_ag_grid as dag
import dash_mantine_components as dmc
import numpy as np
import pandas as pd
from components.common import create_page_header
from dash import Input, Output, State, callback, dcc, html
from dash_iconify import DashIconify
from sklearn.metrics.pairwise import cosine_similarity
from utils.data_manager import data_manager


def layout():
    """Create the collaborative filtering page layout."""
    return dmc.Container(
        [
            create_page_header(
                "Collaborative Filtering",
                "Build recommendation systems using user-based and item-based collaborative filtering.",
                icon="carbon:recommend",
            ),
            dmc.Grid([
                # Left panel
                dmc.GridCol(
                    [
                        dmc.Card(
                            [
                                dmc.Stack(
                                    [
                                        dmc.Title("Model Settings", order=4),
                                        dmc.Select(
                                            id="collab-dataset",
                                            label="Dataset",
                                            placeholder="Select dataset...",
                                            data=[],
                                        ),
                                        dmc.Select(
                                            id="collab-user",
                                            label="User ID Column",
                                            placeholder="Select user column...",
                                            data=[],
                                        ),
                                        dmc.Select(
                                            id="collab-item",
                                            label="Item ID Column",
                                            placeholder="Select item column...",
                                            data=[],
                                        ),
                                        dmc.Select(
                                            id="collab-rating",
                                            label="Rating Column",
                                            placeholder="Select rating column...",
                                            data=[],
                                        ),
                                        dmc.SegmentedControl(
                                            id="collab-method",
                                            label="Filtering Method",
                                            data=[
                                                {
                                                    "label": "User-Based",
                                                    "value": "user",
                                                },
                                                {
                                                    "label": "Item-Based",
                                                    "value": "item",
                                                },
                                            ],
                                            value="user",
                                        ),
                                        dmc.NumberInput(
                                            id="collab-neighbors",
                                            label="Number of Neighbors",
                                            description="K nearest neighbors to consider",
                                            value=5,
                                            min=1,
                                            max=50,
                                            step=1,
                                        ),
                                        dmc.Button(
                                            "Build Model",
                                            id="collab-build-btn",
                                            leftSection=DashIconify(icon="carbon:play", width=20),
                                            fullWidth=True,
                                            size="lg",
                                            color="blue",
                                        ),
                                        dmc.Divider(
                                            label="Get Recommendations",
                                            labelPosition="center",
                                        ),
                                        dmc.TextInput(
                                            id="collab-target-user",
                                            label="User ID",
                                            placeholder="Enter user ID...",
                                        ),
                                        dmc.NumberInput(
                                            id="collab-top-n",
                                            label="Top N Recommendations",
                                            value=10,
                                            min=1,
                                            max=50,
                                            step=1,
                                        ),
                                        dmc.Button(
                                            "Get Recommendations",
                                            id="collab-recommend-btn",
                                            leftSection=DashIconify(icon="carbon:recommend", width=20),
                                            fullWidth=True,
                                            color="green",
                                        ),
                                    ],
                                    gap="sm",
                                )
                            ],
                            withBorder=True,
                            radius="md",
                            p="md",
                        ),
                    ],
                    span={"base": 12, "md": 4},
                ),
                # Right panel
                dmc.GridCol(
                    [
                        dmc.Tabs(
                            [
                                dmc.TabsList([
                                    dmc.TabsTab(
                                        "Model Summary",
                                        value="summary",
                                        leftSection=DashIconify(icon="carbon:report"),
                                    ),
                                    dmc.TabsTab(
                                        "Recommendations",
                                        value="recommendations",
                                        leftSection=DashIconify(icon="carbon:list"),
                                    ),
                                    dmc.TabsTab(
                                        "Similarity Matrix",
                                        value="similarity",
                                        leftSection=DashIconify(icon="carbon:grid"),
                                    ),
                                ]),
                                dmc.TabsPanel(
                                    [
                                        dmc.Card(
                                            [
                                                html.Div(id="collab-summary"),
                                            ],
                                            withBorder=True,
                                            radius="md",
                                            p="md",
                                            mt="md",
                                        ),
                                    ],
                                    value="summary",
                                ),
                                dmc.TabsPanel(
                                    [
                                        dmc.Card(
                                            [
                                                html.Div(id="collab-recommendations"),
                                            ],
                                            withBorder=True,
                                            radius="md",
                                            p="md",
                                            mt="md",
                                        ),
                                    ],
                                    value="recommendations",
                                ),
                                dmc.TabsPanel(
                                    [
                                        dmc.Card(
                                            [
                                                dcc.Graph(id="collab-similarity-plot"),
                                            ],
                                            withBorder=True,
                                            radius="md",
                                            p="md",
                                            mt="md",
                                        ),
                                    ],
                                    value="similarity",
                                ),
                            ],
                            value="summary",
                            id="collab-tabs",
                        ),
                    ],
                    span={"base": 12, "md": 8},
                ),
            ]),
            # Hidden storage
            dcc.Store(id="collab-model-store"),
            html.Div(id="collab-notification"),
        ],
        fluid=True,
        style={"maxWidth": "1400px"},
    )


# Callbacks
@callback(
    Output("collab-dataset", "data"),
    Input("collab-dataset", "id"),
)
def update_datasets(_):
    """Update available datasets."""
    datasets = data_manager.get_dataset_names()
    return [{"label": name, "value": name} for name in datasets]


@callback(
    [
        Output("collab-user", "data"),
        Output("collab-item", "data"),
        Output("collab-rating", "data"),
    ],
    Input("collab-dataset", "value"),
)
def update_columns(dataset_name):
    """Update available columns when dataset changes."""
    if not dataset_name:
        return [], [], []

    try:
        df = data_manager.get_dataset(dataset_name)
        all_cols = [{"label": col, "value": col} for col in df.columns]
        numeric_cols = [{"label": col, "value": col} for col in df.select_dtypes(include=[np.number]).columns]
        return all_cols, all_cols, numeric_cols
    except Exception:
        return [], [], []


@callback(
    [
        Output("collab-summary", "children"),
        Output("collab-similarity-plot", "figure"),
        Output("collab-model-store", "data"),
        Output("collab-notification", "children"),
    ],
    Input("collab-build-btn", "n_clicks"),
    [
        State("collab-dataset", "value"),
        State("collab-user", "value"),
        State("collab-item", "value"),
        State("collab-rating", "value"),
        State("collab-method", "value"),
        State("collab-neighbors", "value"),
    ],
    prevent_initial_call=True,
)
def build_model(n_clicks, dataset_name, user_col, item_col, rating_col, method, n_neighbors):
    """Build collaborative filtering model."""
    if not all([dataset_name, user_col, item_col, rating_col]):
        return (
            dmc.Text("Please select all required columns.", c="red"),
            {},
            None,
            dmc.Notification(
                title="Error",
                message="Missing required inputs",
                color="red",
                action="show",
            ),
        )

    try:
        # Get data
        df = data_manager.get_dataset(dataset_name)

        # Create user-item matrix
        matrix = df.pivot_table(values=rating_col, index=user_col, columns=item_col, fill_value=0)

        # Calculate similarity
        if method == "user":
            similarity = cosine_similarity(matrix)
            similarity_df = pd.DataFrame(similarity, index=matrix.index, columns=matrix.index)
            label = "User"
        else:  # item-based
            similarity = cosine_similarity(matrix.T)
            similarity_df = pd.DataFrame(similarity, index=matrix.columns, columns=matrix.columns)
            label = "Item"

        # Summary statistics
        n_users = matrix.shape[0]
        n_items = matrix.shape[1]
        n_ratings = (matrix > 0).sum().sum()
        sparsity = 1 - (n_ratings / (n_users * n_items))

        summary = dmc.Stack(
            [
                dmc.Text(
                    f"Method: {method.title()}-based Collaborative Filtering",
                    fw=600,
                    size="lg",
                ),
                dmc.Divider(),
                dmc.Text(f"Number of Users: {n_users}"),
                dmc.Text(f"Number of Items: {n_items}"),
                dmc.Text(f"Total Ratings: {n_ratings}"),
                dmc.Text(f"Sparsity: {sparsity:.2%}"),
                dmc.Text(f"Neighbors (K): {n_neighbors}"),
                dmc.Divider(),
                dmc.Text(
                    "Model built successfully! Use 'Get Recommendations' to generate predictions.",
                    c="green",
                ),
            ],
            gap="xs",
        )

        # Similarity heatmap (show sample)
        import plotly.express as px

        sample_size = min(20, len(similarity_df))
        sample_sim = similarity_df.iloc[:sample_size, :sample_size]

        similarity_fig = px.imshow(
            sample_sim,
            title=f"{label} Similarity Matrix (Sample)",
            labels=dict(color="Similarity"),
            color_continuous_scale="RdBu_r",
        )

        # Store model data
        model_data = {
            "matrix": matrix.to_dict(),
            "similarity": similarity_df.to_dict(),
            "method": method,
            "n_neighbors": n_neighbors,
            "user_col": user_col,
            "item_col": item_col,
        }

        return (
            summary,
            similarity_fig,
            model_data,
            dmc.Notification(
                title="Success",
                message="Model built successfully",
                color="green",
                action="show",
            ),
        )

    except Exception as e:
        return (
            dmc.Text(f"Error: {e!s}", c="red"),
            {},
            None,
            dmc.Notification(
                title="Error",
                message=str(e),
                color="red",
                action="show",
            ),
        )


@callback(
    Output("collab-recommendations", "children"),
    Input("collab-recommend-btn", "n_clicks"),
    [
        State("collab-target-user", "value"),
        State("collab-top-n", "value"),
        State("collab-model-store", "data"),
    ],
    prevent_initial_call=True,
)
def get_recommendations(n_clicks, target_user, top_n, model_data):
    """Generate recommendations for a user."""
    if not model_data or not target_user:
        return dmc.Text("Please build model first and enter a user ID.", c="red")

    try:
        # Reconstruct data
        matrix = pd.DataFrame.from_dict(model_data["matrix"])
        similarity_df = pd.DataFrame.from_dict(model_data["similarity"])
        method = model_data["method"]
        n_neighbors = model_data["n_neighbors"]

        # Convert target_user to appropriate type
        if target_user not in matrix.index:
            # Try converting to int/float
            try:
                if matrix.index.dtype == np.int64:
                    target_user = int(target_user)
                elif matrix.index.dtype == np.float64:
                    target_user = float(target_user)
            except ValueError:
                pass

        if target_user not in matrix.index:
            return dmc.Text(f"User '{target_user}' not found in the dataset.", c="red")

        # Get user's ratings
        user_ratings = matrix.loc[target_user]

        if method == "user":
            # User-based: find similar users
            user_sim = similarity_df.loc[target_user]
            similar_users = user_sim.nlargest(n_neighbors + 1).index[1:]  # Exclude self

            # Aggregate ratings from similar users
            recommendations = pd.Series(dtype=float)
            for item in matrix.columns:
                if user_ratings[item] == 0:  # Only recommend unrated items
                    # Weighted average of similar users' ratings
                    similar_ratings = matrix.loc[similar_users, item]
                    weights = user_sim[similar_users]

                    # Remove users who haven't rated this item
                    mask = similar_ratings > 0
                    if mask.any():
                        weighted_rating = (similar_ratings[mask] * weights[mask]).sum() / weights[mask].sum()
                        recommendations[item] = weighted_rating
        else:
            # Item-based: for each unrated item, find similar items
            recommendations = pd.Series(dtype=float)
            rated_items = user_ratings[user_ratings > 0].index

            for item in matrix.columns:
                if user_ratings[item] == 0:  # Only recommend unrated items
                    item_sim = similarity_df.loc[item]

                    # Find similar items that user has rated
                    similar_items = item_sim[rated_items].nlargest(n_neighbors)

                    if len(similar_items) > 0:
                        # Weighted average
                        weights = similar_items
                        ratings = user_ratings[similar_items.index]
                        weighted_rating = (ratings * weights).sum() / weights.sum()
                        recommendations[item] = weighted_rating

        # Get top N recommendations
        if len(recommendations) == 0:
            return dmc.Text("No recommendations available for this user.", c="orange")

        top_recs = recommendations.nlargest(top_n)

        # Create recommendations table
        rec_data = [
            {"Rank": i + 1, "Item": item, "Predicted Rating": f"{rating:.3f}"}
            for i, (item, rating) in enumerate(top_recs.items())
        ]

        return dmc.Stack(
            [
                dmc.Text(
                    f"Top {top_n} Recommendations for User: {target_user}",
                    fw=600,
                    size="lg",
                ),
                dag.AgGrid(
                    rowData=rec_data,
                    columnDefs=[
                        {"field": "Rank", "width": 80},
                        {"field": "Item", "flex": 1},
                        {"field": "Predicted Rating", "width": 150},
                    ],
                    defaultColDef={"sortable": False},
                    style={"height": "400px"},
                ),
            ],
            gap="md",
        )

    except Exception as e:
        return dmc.Text(f"Error: {e!s}", c="red")
