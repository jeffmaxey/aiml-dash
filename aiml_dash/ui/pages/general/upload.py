"""
Upload Page - Experiment Data Submission Interface

This module implements the upload page where users can submit new experimental data:
- Enter experiment metadata (name, date, DOI, additional info)
- Input substrate and product SMILES strings with validation
- Select assay technique and mutagenesis method
- Upload CSV data files and PDB protein structure files
- Validate inputs before submission

The page uses Dash Mantine Components for a modern, responsive UI with:
- Text inputs for experiment metadata
- Textarea components for SMILES string input
- Dropdown for assay selection
- Radio buttons for mutagenesis method selection
- File upload buttons with visual feedback
- Form validation and submission controls
- Alert messages for upload restrictions

Components:
    - get_form(): Main upload form with all input fields
    - get_upload_disabled_alert(): Warning alert when uploads are disabled
    - get_layout(): Complete page layout composition

Features:
    - Real-time SMILES validation
    - File upload with type checking (CSV, PDB)
    - Form state management (submit button enabled/disabled)
    - Visual feedback for file uploads
    - Responsive centered layout
    - Clear error messaging

Author: Conversion to Mantine Components
Date: January 7, 2026
"""

import dash_mantine_components as dmc
from dash import dcc, html

from aiml_dash.utils.settings import app_settings
# Note: levseq_dash imports have been removed - these modules are not part of aiml_dash
# from levseq_dash.app import global_strings as gs
# from levseq_dash.app.data_manager.experiment import MutagenesisMethod

from . import styles
from . import widgets


def get_form():
    """
    Create the experiment upload form.

    Generates a comprehensive form with multiple input types:
    1. Experiment Name - text input with placeholder
    2. Experiment Date - date picker for selection
    3. Substrate SMILES - textarea with validation
    4. Product SMILES - textarea with validation
    5. Assay Technique - dropdown selection
    6. Mutagenesis Method - radio button choice (epPCR/SSM)
    7. DOI Reference - text input for publication
    8. Additional Info - textarea for notes
    9. Data File Upload - CSV file button
    10. Structure File Upload - PDB file button
    11. Submit Button - validates and submits form

    The form includes:
    - Input validation for SMILES strings
    - File type checking for uploads
    - Dynamic submit button state (disabled until valid)
    - Visual feedback for file uploads
    - Centered responsive layout

    Returns:
        dmc.Stack: Form layout with all input components

    Component IDs:
        - id-input-experiment-name: Experiment name input
        - id-input-experiment-date: Date picker
        - id-input-substrate: Substrate SMILES textarea
        - id-input-product: Product SMILES textarea
        - id-list-assay: Assay technique dropdown
        - id-radio-epr: Mutagenesis method radio buttons
        - id-input-experiment-doi: DOI input
        - id-input-experiment-info: Additional info textarea
        - id-button-upload-data: CSV upload button
        - id-button-upload-structure: PDB upload button
        - id-button-upload-data-info: CSV upload status display
        - id-button-upload-structure-info: PDB upload status display
        - id-button-submit: Form submission button
        - id-alert-upload: Alert message container

    Form Validation:
        - Submit button disabled until all required fields valid
        - SMILES strings validated on input
        - File types checked on upload
    """
    # Main form container with vertical stack layout
    return dmc.Stack(
        [
            dmc.Space(h="md"),
            dmc.Space(h="md"),
            # Experiment Name input row
            dmc.Grid(
                [
                    widgets.get_label_fixed_for_form(gs.experiment_name),
                    dmc.GridCol(
                        dmc.TextInput(
                            id="id-input-experiment-name",
                            placeholder=gs.experiment_name_placeholder,
                        ),
                        span="auto",
                    ),
                ],
                mb="xs",
            ),
            # Experiment Date picker row
            dmc.Grid(
                [
                    widgets.get_label_fixed_for_form(gs.experiment_date),
                    dmc.GridCol(
                        [
                            dcc.DatePickerSingle(
                                id="id-input-experiment-date",
                                clearable=True,
                            )
                        ],
                        span="auto",
                    ),
                ],
                mb="xs",
            ),
            # Substrate SMILES input row
            dmc.Grid(
                [
                    widgets.get_label_fixed_for_form(gs.substrate_smiles_input),
                    dmc.GridCol(
                        dmc.Textarea(
                            id="id-input-substrate",
                            placeholder=gs.smiles_input_placeholder,
                            error=True,  # Shows validation state
                            autosize=True,
                            minRows=2,
                        ),
                        span="auto",
                    ),
                ],
                mb="xs",
            ),
            # Product SMILES input row
            dmc.Grid(
                [
                    widgets.get_label_fixed_for_form(gs.product_smiles_input),
                    dmc.GridCol(
                        dmc.Textarea(
                            id="id-input-product",
                            placeholder=gs.smiles_input_placeholder,
                            error=True,  # Shows validation state
                            autosize=True,
                            minRows=2,
                        ),
                        span="auto",
                    ),
                ],
                mb="xs",
            ),
            # Assay Technique dropdown row
            dmc.Grid(
                [
                    widgets.get_label_fixed_for_form(gs.assay),
                    dmc.GridCol(
                        [
                            html.Div(
                                [
                                    dcc.Dropdown(
                                        id="id-list-assay",
                                        placeholder="Select Assay Technique.",
                                    ),
                                ],
                                className="dbc",
                            ),
                        ],
                        span="auto",
                    ),
                ],
                mb="xs",
            ),
            # Mutagenesis Method radio buttons row
            dmc.Grid(
                [
                    widgets.get_label_fixed_for_form(gs.tech),
                    dmc.GridCol(
                        [
                            dmc.RadioGroup(
                                [
                                    dmc.Radio(MutagenesisMethod.epPCR, value=MutagenesisMethod.epPCR),
                                    dmc.Radio(MutagenesisMethod.SSM, value=MutagenesisMethod.SSM),
                                ],
                                id="id-radio-epr",
                                value=MutagenesisMethod.epPCR,
                                # Horizontal layout with gap
                                style={"display": "flex", "flexDirection": "row", "gap": "20px"},
                            )
                        ],
                        span="auto",
                    ),
                ],
                mb="xs",
            ),
            # DOI input row
            dmc.Grid(
                [
                    widgets.get_label_fixed_for_form(gs.experiment_doi),
                    dmc.GridCol(
                        dmc.TextInput(
                            id="id-input-experiment-doi",
                            placeholder=gs.experiment_doi_placeholder,
                        ),
                        span="auto",
                    ),
                ],
                mb="xs",
            ),
            # Additional Info textarea row
            dmc.Grid(
                [
                    widgets.get_label_fixed_for_form(gs.experiment_additional_info),
                    dmc.GridCol(
                        dmc.Textarea(
                            id="id-input-experiment-info",
                            placeholder=gs.experiment_additional_info_placeholder,
                            autosize=True,
                            minRows=3,
                        ),
                        span="auto",
                    ),
                ],
                mb="xs",
            ),
            dmc.Space(h="md"),
            # File upload buttons row (CSV and PDB)
            dmc.Grid(
                [
                    # CSV Data Upload
                    dmc.GridCol(
                        dcc.Upload(
                            id="id-button-upload-data",
                            children=dmc.Button(
                                gs.button_upload_csv,
                                variant="outline",
                                color="gray",
                                fullWidth=True,
                            ),
                            multiple=False,
                            style=styles.upload_default,
                        ),
                        span=6,
                    ),
                    # PDB Structure Upload
                    dmc.GridCol(
                        dcc.Upload(
                            id="id-button-upload-structure",
                            children=dmc.Button(
                                gs.button_upload_pdb,
                                variant="outline",
                                color="gray",
                                fullWidth=True,
                            ),
                            multiple=False,
                            style=styles.upload_default,
                        ),
                        span=6,
                    ),
                ],
                mb="xs",
            ),
            # Upload status display row
            dmc.Grid(
                [
                    # CSV upload status
                    dmc.GridCol(
                        html.Div(
                            id="id-button-upload-data-info",
                            style={
                                "word-break": "break-all",  # Break long filenames
                                "whiteSpace": "normal",  # Enable text wrapping
                                "width": "100%",  # Full container width
                            },
                        ),
                        span=6,
                    ),
                    # PDB upload status
                    dmc.GridCol(
                        html.Div(id="id-button-upload-structure-info"),
                        span=6,
                    ),
                ],
            ),
            dmc.Space(h="md"),
            # Submit button row
            dmc.Grid(
                [
                    dmc.GridCol(
                        dmc.Button(
                            "Submit",
                            id="id-button-submit",
                            n_clicks=0,
                            size="md",
                            fullWidth=True,
                            disabled=True,  # Disabled until form is valid
                        ),
                        span=6,
                    ),
                ],
                mb="lg",
            ),
            # Alert message container (dynamically populated)
            html.Div(
                id="id-alert-upload",
                className="d-flex justify-content-center",
            ),
        ],
        gap="xs",
        style={
            "width": "70%",  # Form width
            "margin": "0 auto",  # Center horizontally
        },
    )


def get_upload_disabled_alert():
    """
    Create an alert message for when data uploads are disabled.

    This alert appears on instances where direct data modification
    is not permitted (e.g., public/demo instances). It informs users
    that they need to use a local instance for actual uploads while
    still allowing them to validate their data format.

    The alert includes:
    - Clear explanation of upload restrictions
    - Direction to use local instance instead
    - Note that validation features still work
    - Reference to About page for formatting guidance

    Returns:
        html.Div: Alert container with warning message

    Display Conditions:
        - Shown when settings.is_data_modification_enabled() returns False
        - Typically on public demo instances
        - Hidden on local/authorized instances

    Message Content:
        - Upload restriction notice
        - Validation availability note
        - Link to formatting documentation (About page)
    """
    # Container for centered alert
    return html.Div(
        children=[
            dmc.Alert(
                children=([
                    "To upload data, please use the local instance. "
                    "You may continue to use the form to validate your SMILES strings and data files. "
                    "For guidance on formatting your data for public release via the local instance, refer to the ",
                    html.B("About"),
                    " page. ",
                ]),
                title="Upload Restricted",
                color="red",
                className="p-4 user-alert-error",
            )
        ],
        style={
            "width": "70%",  # Match form width
            "margin": "0 auto",  # Center horizontally
        },
    )


def get_layout():
    """
    Create the main upload page layout.

    Assembles the complete upload interface with:
    - Page title and divider
    - Upload form with all input fields
    - Optional alert message (if uploads disabled)

    The layout conditionally includes an alert message based on
    whether data modification is enabled in the application settings.
    This allows the same page to work in both local (full upload)
    and public (validation only) modes.

    Returns:
        html.Div: Complete page layout with all components

    Layout Structure:
        1. Page title (H4)
        2. Divider line
        3. Alert message (conditional - only if uploads disabled)
        4. Upload form (always shown)

    Configuration:
        - Upload availability: settings.is_data_modification_enabled()
        - Form width: 70% of page width
        - Layout class: styles.main_page_class

    Features:
        - Dynamic alert insertion based on settings
        - Consistent page styling
        - Responsive centered layout
        - Form validation regardless of upload permission
    """
    # Build layout components list
    layout = [dmc.Title(gs.nav_upload, order=4, className="page-title"), dmc.Divider(size="sm"), get_form()]

    # Conditionally add upload restriction alert
    if not settings.is_data_modification_enabled():
        layout.insert(2, get_upload_disabled_alert())

    # Return complete page layout
    return html.Div(
        layout,
        className=styles.main_page_class,
    )
