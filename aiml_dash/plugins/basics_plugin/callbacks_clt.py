"""Central Limit Theorem simulation callbacks.

This module is part of the basics plugin callback suite.
Callbacks are registered automatically via ``@callback`` decorators on import.
"""

import dash_mantine_components as dmc
import numpy as np
import numpy.typing as npt
import plotly.graph_objects as go
from dash import Input, Output, State, callback
from dash.development.base_component import Component
from dash_iconify import DashIconify
from plotly.subplots import make_subplots
from scipy import stats


@callback(
    [
        Output("clt-stats", "children"),
        Output("clt-plot-container", "style"),
        Output("clt-plot", "figure"),
    ],
    Input("clt-run", "n_clicks"),
    [
        State("clt-distribution", "value"),
        State("clt-sample-size", "value"),
        State("clt-num-samples", "value"),
        State("clt-seed", "value"),
    ],
    prevent_initial_call=True,
)
def run_clt_simulation(
    n_clicks: int | None,
    distribution: str | None,
    sample_size: int | float | None,
    num_samples: int | float | None,
    seed: int | None,
) -> tuple[list[Component], dict[str, str], go.Figure | dict[str, object]]:
    """Run CLT simulation.

    Parameters
    ----------
    n_clicks : int | None
        Input value for ``n_clicks``.
    distribution : str | None
        Input value for ``distribution``.
    sample_size : int | float | None
        Input value for ``sample_size``.
    num_samples : int | float | None
        Input value for ``num_samples``.
    seed : int | None
        Input value for ``seed``.

    Returns
    -------
    value : tuple[list[Component], dict[str, str], go.Figure | dict[str, object]]
        Result produced by this function."""
    try:
        if sample_size is None or num_samples is None:
            raise ValueError("Sample size and number of samples are required.")
        sample_size_int = int(sample_size)
        num_samples_int = int(num_samples)
        if distribution is None:
            distribution = "uniform"
        # Set random seed for reproducibility
        np.random.seed(seed)

        # Generate population based on distribution type
        pop_size = 100000

        population: npt.NDArray[np.float64]
        if distribution == "uniform":
            population = np.random.uniform(0, 10, pop_size)
            pop_mean = 5.0
            pop_std = 10 / np.sqrt(12)  # Theoretical std for uniform(0,10)
        elif distribution == "normal":
            population = np.random.normal(50, 10, pop_size)
            pop_mean = 50.0
            pop_std = 10.0
        elif distribution == "exponential":
            population = np.random.exponential(2, pop_size)
            pop_mean = 2.0
            pop_std = 2.0
        elif distribution == "binomial":
            population = np.random.binomial(10, 0.5, pop_size).astype(np.float64)
            pop_mean = 5.0
            pop_std = np.sqrt(10 * 0.5 * 0.5)
        elif distribution == "poisson":
            population = np.random.poisson(5, pop_size).astype(np.float64)
            pop_mean = 5.0
            pop_std = np.sqrt(5.0)
        else:  # beta (skewed)
            population = np.random.beta(2, 5, pop_size) * 10
            pop_mean = (2 / (2 + 5)) * 10
            pop_std = np.sqrt((2 * 5) / ((2 + 5) ** 2 * (2 + 5 + 1))) * 10

        # Draw samples and calculate means
        sample_means: list[float] = []
        for _ in range(num_samples_int):
            sample = np.random.choice(population, size=sample_size_int, replace=True)
            sample_means.append(float(np.mean(sample)))

        sample_means_array = np.array(sample_means, dtype=np.float64)

        # Calculate statistics
        mean_of_means = np.mean(sample_means_array)
        std_of_means = np.std(sample_means_array, ddof=1)
        theoretical_std = pop_std / np.sqrt(sample_size_int)

        # Normality test (Shapiro-Wilk)
        if len(sample_means_array) <= 5000:
            _shapiro_stat, shapiro_p = stats.shapiro(sample_means_array)
        else:
            # Use Kolmogorov-Smirnov for large samples
            _shapiro_stat, shapiro_p = stats.kstest(
                (sample_means_array - mean_of_means) / std_of_means, "norm"
            )

        # Create statistics display
        stats_content = [
            dmc.Stack(
                gap="md",
                children=[
                    dmc.Text("Simulation Results", fw=600, size="lg"),
                    dmc.SimpleGrid(
                        cols={"base": 2, "sm": 3},
                        spacing="md",
                        children=[
                            dmc.Paper(
                                p="sm",
                                withBorder=True,
                                children=[
                                    dmc.Text(
                                        "Population",
                                        fw=500,
                                        size="sm",
                                        mb="xs",
                                        c="dimmed",
                                    ),
                                    dmc.Group(
                                        [
                                            dmc.Stack(
                                                gap=2,
                                                children=[
                                                    dmc.Text(
                                                        "Mean", size="xs", c="dimmed"
                                                    ),
                                                    dmc.Text(f"{pop_mean:.3f}", fw=600),
                                                ],
                                            ),
                                            dmc.Stack(
                                                gap=2,
                                                children=[
                                                    dmc.Text(
                                                        "Std Dev", size="xs", c="dimmed"
                                                    ),
                                                    dmc.Text(f"{pop_std:.3f}", fw=600),
                                                ],
                                            ),
                                        ],
                                        justify="space-around",
                                    ),
                                ],
                            ),
                            dmc.Paper(
                                p="sm",
                                withBorder=True,
                                children=[
                                    dmc.Text(
                                        "Sample Means",
                                        fw=500,
                                        size="sm",
                                        mb="xs",
                                        c="dimmed",
                                    ),
                                    dmc.Group(
                                        [
                                            dmc.Stack(
                                                gap=2,
                                                children=[
                                                    dmc.Text(
                                                        "Mean", size="xs", c="dimmed"
                                                    ),
                                                    dmc.Text(
                                                        f"{mean_of_means:.3f}",
                                                        fw=600,
                                                        c="blue",
                                                    ),
                                                ],
                                            ),
                                            dmc.Stack(
                                                gap=2,
                                                children=[
                                                    dmc.Text(
                                                        "Std Dev", size="xs", c="dimmed"
                                                    ),
                                                    dmc.Text(
                                                        f"{std_of_means:.3f}",
                                                        fw=600,
                                                        c="blue",
                                                    ),
                                                ],
                                            ),
                                        ],
                                        justify="space-around",
                                    ),
                                ],
                            ),
                            dmc.Paper(
                                p="sm",
                                withBorder=True,
                                children=[
                                    dmc.Text(
                                        "Theory", fw=500, size="sm", mb="xs", c="dimmed"
                                    ),
                                    dmc.Group(
                                        [
                                            dmc.Stack(
                                                gap=2,
                                                children=[
                                                    dmc.Text(
                                                        "SE(x̄)", size="xs", c="dimmed"
                                                    ),
                                                    dmc.Text(
                                                        f"{theoretical_std:.3f}",
                                                        fw=600,
                                                        c="green",
                                                    ),
                                                ],
                                            ),
                                            dmc.Stack(
                                                gap=2,
                                                children=[
                                                    dmc.Text(
                                                        "Error", size="xs", c="dimmed"
                                                    ),
                                                    dmc.Text(
                                                        f"{abs(std_of_means - theoretical_std):.3f}",
                                                        fw=600,
                                                    ),
                                                ],
                                            ),
                                        ],
                                        justify="space-around",
                                    ),
                                ],
                            ),
                        ],
                    ),
                    dmc.Alert(
                        title="Normality Assessment",
                        color="green" if shapiro_p > 0.05 else "yellow",
                        icon=DashIconify(icon="mdi:information"),
                        children=dmc.Text(
                            f"The sampling distribution of means {'appears' if shapiro_p > 0.05 else 'may not be fully'} "
                            f"normally distributed (p = {shapiro_p:.4f}). "
                            f"Standard error: observed = {std_of_means:.3f}, theoretical = {theoretical_std:.3f}. "
                            f"{'Excellent' if abs(std_of_means - theoretical_std) < 0.1 else 'Good'} agreement with theory.",
                            size="sm",
                        ),
                    ),
                ],
            ),
        ]

        # Create visualizations
        fig = make_subplots(
            rows=2,
            cols=1,
            subplot_titles=(
                "Population Distribution",
                "Sampling Distribution of Means",
            ),
            vertical_spacing=0.15,
            row_heights=[0.4, 0.6],
        )

        # Population histogram (sample for display)
        pop_sample = np.random.choice(
            population, size=min(10000, len(population)), replace=False
        )
        fig.add_trace(
            go.Histogram(
                x=pop_sample,
                name="Population",
                marker={"color": "#868e96"},
                nbinsx=50,
                showlegend=False,
            ),
            row=1,
            col=1,
        )

        # Sampling distribution histogram
        fig.add_trace(
            go.Histogram(
                x=sample_means_array,
                name="Sample Means",
                marker={"color": "#1c7ed6", "opacity": 0.7},
                nbinsx=50,
                showlegend=False,
            ),
            row=2,
            col=1,
        )

        # Overlay normal distribution on sampling distribution
        x_range = np.linspace(sample_means_array.min(), sample_means_array.max(), 200)
        normal_pdf = stats.norm.pdf(x_range, mean_of_means, std_of_means)
        # Scale to match histogram
        _hist_counts, _ = np.histogram(sample_means_array, bins=50)
        bin_width = (sample_means_array.max() - sample_means_array.min()) / 50
        scale_factor = len(sample_means_array) * bin_width

        fig.add_trace(
            go.Scatter(
                x=x_range,
                y=normal_pdf * scale_factor,
                name="Normal Distribution",
                mode="lines",
                line={"color": "red", "width": 2},
                showlegend=True,
            ),
            row=2,
            col=1,
        )

        # Add vertical lines for means
        fig.add_vline(
            x=pop_mean,
            line={"color": "red", "dash": "dash", "width": 2},
            annotation_text=f"μ = {pop_mean:.2f}",
            row=1,
            col=1,
        )

        fig.add_vline(
            x=mean_of_means,
            line={"color": "red", "dash": "dash", "width": 2},
            annotation_text=f"x̄ = {mean_of_means:.2f}",
            row=2,
            col=1,
        )

        fig.update_xaxes(title_text="Value", row=1, col=1)
        fig.update_xaxes(title_text="Sample Mean", row=2, col=1)
        fig.update_yaxes(title_text="Frequency", row=1, col=1)
        fig.update_yaxes(title_text="Frequency", row=2, col=1)

        fig.update_layout(
            height=700,
            template="plotly_white",
            showlegend=True,
            legend={
                "orientation": "h",
                "yanchor": "bottom",
                "y": 1.02,
                "xanchor": "right",
                "x": 1,
            },
        )

        return stats_content, {"display": "block"}, fig

    except Exception as e:
        return (
            [
                dmc.Alert(
                    f"Error: {e!s}",
                    title="Error",
                    color="red",
                    icon=DashIconify(icon="mdi:alert-circle"),
                )
            ],
            {"display": "none"},
            {},
        )


