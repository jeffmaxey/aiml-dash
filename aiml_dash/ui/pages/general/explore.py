import dash_mantine_components as dmc
from dash import dcc, html
from . import styles, widgets
from .widgets import get_download_text_icon_combo
from levseq_dash.app import global_strings as gs


# -------------------------------------------------------
def get_layout():
    return dmc.Container(
        [
            dmc.Stack(
                [
                    dmc.Title(gs.lab_exp, order=2, className="page-title"),
                    dmc.Divider(),
                    dmc.Card(
                        [
                            html.Div(
                                [widgets.get_table_all_experiments()],
                                className="dbc dbc-ag-grid",
                                style=styles.border_table,
                            ),
                            dmc.Space(h="md"),
                            dmc.Grid(
                                [
                                    dmc.GridCol(
                                        dmc.Button(
                                            id="id-button-delete-experiment",
                                            n_clicks=0,
                                            children=html.Span(
                                                [styles.get_icon(styles.icon_del_exp)],
                                                style={"color": "var(--mantine-color-red-6)"},
                                            ),
                                            variant="subtle",
                                            color="red",
                                        ),
                                        span=1,
                                    ),
                                    dmc.GridCol(
                                        dmc.Group(
                                            [
                                                dmc.Button(
                                                    children=[
                                                        get_download_text_icon_combo("Download Selected Experiment(s)")
                                                    ],
                                                    id="id-button-download-all-experiments",
                                                    n_clicks=0,
                                                    disabled=True,
                                                    className="shadow-sm",
                                                    style={"flex": "0 0 auto"},
                                                ),
                                                dmc.Button(
                                                    children=html.Span([
                                                        html.Span(gs.go_to),
                                                        html.Span(
                                                            styles.get_icon(styles.icon_go_to_next),
                                                            style={"marginLeft": "8px"},
                                                        ),
                                                    ]),
                                                    id="id-button-goto-experiment",
                                                    n_clicks=0,
                                                    disabled=True,
                                                    className="shadow-sm",
                                                    style={"flex": "0 0 auto"},
                                                ),
                                            ],
                                            justify="center",
                                            gap="sm",
                                        ),
                                        span=10,
                                    ),
                                    dmc.GridCol(span=1),  # Empty column for balance
                                ],
                                gutter="xs",
                            ),
                        ],
                        shadow="sm",
                        radius="md",
                        padding="xs",
                        withBorder=True,
                    ),
                    html.Div(
                        id="id-alert-explore",
                        style={"display": "flex", "justifyContent": "center"},
                    ),
                ],
                gap="md",
            ),
            # Confirmation modal for deletion
            dmc.Modal(
                id="id-delete-confirmation-modal",
                opened=False,
                centered=True,
                title="Confirm Deletion",
                children=[
                    html.Div(id="id-delete-modal-body"),
                    dmc.Space(h="md"),
                    dmc.Group(
                        [
                            dmc.Button(
                                "Cancel",
                                id="id-delete-modal-cancel",
                                variant="default",
                                n_clicks=0,
                            ),
                            dmc.Button(
                                "Delete",
                                id="id-delete-modal-confirm",
                                color="red",
                                n_clicks=0,
                            ),
                        ],
                        justify="flex-end",
                        gap="sm",
                    ),
                ],
            ),
            # Download component for ZIP files
            dcc.Download(id="id-download-all-experiments-zip"),
        ],
        className=styles.main_page_class,
        fluid=True,
    )
