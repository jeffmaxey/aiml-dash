"""
Central Limit Theorem Simulation
Interactive demonstration of the Central Limit Theorem.
"""

from dash import dcc, callback, Input, Output, State
import dash_mantine_components as dmc
from dash_iconify import DashIconify
import numpy as np
from scipy import stats
import plotly.graph_objects as go
from plotly.subplots import make_subplots


def layout():
    """Create layout for CLT simulation page."""
    return dmc.Container(
        fluid=True,
        p="md",
        children=[
            # Page Header
            dmc.Stack(
                gap="md",
                children=[
                    dmc.Group(
                        [
                            DashIconify(icon="mdi:chart-bell-curve-cumulative", width=32),
                            dmc.Title("Central Limit Theorem", order=2),
                        ],
                        gap="sm",
                    ),
                    dmc.Text(
                        "Visualize how sample means converge to a normal distribution",
                        c="dimmed",
                        size="sm",
                    ),
                    dmc.Divider(),
                ],
            ),
            # Main Content
            dmc.Grid(
                gutter="md",
                children=[
                    # Left Column - Controls
                    dmc.GridCol(
                        span={"base": 12, "md": 4},
                        children=[
                            dmc.Paper(
                                p="md",
                                withBorder=True,
                                children=[
                                    dmc.Stack(
                                        gap="md",
                                        children=[
                                            dmc.Text(
                                                "Population Distribution",
                                                fw=500,
                                                size="lg",
                                            ),
                                            dmc.Select(
                                                id="clt-distribution",
                                                label="Distribution Type",
                                                data=[
                                                    {
                                                        "label": "Uniform",
                                                        "value": "uniform",
                                                    },
                                                    {
                                                        "label": "Normal",
                                                        "value": "normal",
                                                    },
                                                    {
                                                        "label": "Exponential",
                                                        "value": "exponential",
                                                    },
                                                    {
                                                        "label": "Binomial",
                                                        "value": "binomial",
                                                    },
                                                    {
                                                        "label": "Poisson",
                                                        "value": "poisson",
                                                    },
                                                    {
                                                        "label": "Beta (Skewed)",
                                                        "value": "beta",
                                                    },
                                                ],
                                                value="uniform",
                                                clearable=False,
                                            ),
                                            dmc.Divider(),
                                            dmc.Text("Sampling Parameters", fw=500, size="lg"),
                                            dmc.NumberInput(
                                                id="clt-sample-size",
                                                label="Sample Size (n)",
                                                description="Number of observations per sample",
                                                value=30,
                                                min=2,
                                                max=200,
                                                step=1,
                                            ),
                                            dmc.NumberInput(
                                                id="clt-num-samples",
                                                label="Number of Samples",
                                                description="How many samples to draw",
                                                value=1000,
                                                min=100,
                                                max=10000,
                                                step=100,
                                            ),
                                            dmc.NumberInput(
                                                id="clt-seed",
                                                label="Random Seed",
                                                description="For reproducibility (optional)",
                                                value=42,
                                                min=0,
                                                max=9999,
                                                step=1,
                                            ),
                                            dmc.Button(
                                                "Run Simulation",
                                                id="clt-run",
                                                leftSection=DashIconify(icon="mdi:play"),
                                                fullWidth=True,
                                                variant="filled",
                                            ),
                                            dmc.Divider(),
                                            dmc.Alert(
                                                title="About CLT",
                                                color="blue",
                                                icon=DashIconify(icon="mdi:information"),
                                                children=dmc.Text(
                                                    "The Central Limit Theorem states that the distribution of "
                                                    "sample means approaches a normal distribution as sample size increases, "
                                                    "regardless of the population distribution.",
                                                    size="sm",
                                                ),
                                            ),
                                        ],
                                    ),
                                ],
                            ),
                        ],
                    ),
                    # Right Column - Results
                    dmc.GridCol(
                        span={"base": 12, "md": 8},
                        children=[
                            dmc.Stack(
                                gap="md",
                                children=[
                                    dmc.Paper(
                                        id="clt-stats",
                                        p="md",
                                        withBorder=True,
                                        children=[
                                            dmc.Text(
                                                "Set parameters and click 'Run Simulation' to see results",
                                                c="dimmed",
                                                ta="center",
                                                py="xl",
                                            ),
                                        ],
                                    ),
                                    dmc.Paper(
                                        id="clt-plot-container",
                                        p="md",
                                        withBorder=True,
                                        style={"display": "none"},
                                        children=[
                                            dcc.Graph(
                                                id="clt-plot",
                                                config={"displayModeBar": False},
                                            ),
                                        ],
                                    ),
                                ],
                            ),
                        ],
                    ),
                ],
            ),
        ],
    )


# ==============================================================================
# CALLBACKS
# ==============================================================================


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
def run_clt_simulation(n_clicks, distribution, sample_size, num_samples, seed):
    """Run CLT simulation."""
    try:
        # Set random seed for reproducibility
        np.random.seed(seed)

        # Generate population based on distribution type
        pop_size = 100000

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
            population = np.random.binomial(10, 0.5, pop_size)
            pop_mean = 5.0
            pop_std = np.sqrt(10 * 0.5 * 0.5)
        elif distribution == "poisson":
            population = np.random.poisson(5, pop_size)
            pop_mean = 5.0
            pop_std = np.sqrt(5.0)
        else:  # beta (skewed)
            population = np.random.beta(2, 5, pop_size) * 10
            pop_mean = (2 / (2 + 5)) * 10
            pop_std = np.sqrt((2 * 5) / ((2 + 5) ** 2 * (2 + 5 + 1))) * 10

        # Draw samples and calculate means
        sample_means = []
        for _ in range(num_samples):
            sample = np.random.choice(population, size=sample_size, replace=True)
            sample_means.append(np.mean(sample))

        sample_means = np.array(sample_means)

        # Calculate statistics
        mean_of_means = np.mean(sample_means)
        std_of_means = np.std(sample_means, ddof=1)
        theoretical_std = pop_std / np.sqrt(sample_size)

        # Normality test (Shapiro-Wilk)
        if len(sample_means) <= 5000:
            shapiro_stat, shapiro_p = stats.shapiro(sample_means)
        else:
            # Use Kolmogorov-Smirnov for large samples
            shapiro_stat, shapiro_p = stats.kstest((sample_means - mean_of_means) / std_of_means, "norm")

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
                                                    dmc.Text("Mean", size="xs", c="dimmed"),
                                                    dmc.Text(f"{pop_mean:.3f}", fw=600),
                                                ],
                                            ),
                                            dmc.Stack(
                                                gap=2,
                                                children=[
                                                    dmc.Text("Std Dev", size="xs", c="dimmed"),
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
                                                    dmc.Text("Mean", size="xs", c="dimmed"),
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
                                                    dmc.Text("Std Dev", size="xs", c="dimmed"),
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
                                    dmc.Text("Theory", fw=500, size="sm", mb="xs", c="dimmed"),
                                    dmc.Group(
                                        [
                                            dmc.Stack(
                                                gap=2,
                                                children=[
                                                    dmc.Text("SE(x̄)", size="xs", c="dimmed"),
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
                                                    dmc.Text("Error", size="xs", c="dimmed"),
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
        pop_sample = np.random.choice(population, size=min(10000, len(population)), replace=False)
        fig.add_trace(
            go.Histogram(
                x=pop_sample,
                name="Population",
                marker=dict(color="#868e96"),
                nbinsx=50,
                showlegend=False,
            ),
            row=1,
            col=1,
        )

        # Sampling distribution histogram
        fig.add_trace(
            go.Histogram(
                x=sample_means,
                name="Sample Means",
                marker=dict(color="#1c7ed6", opacity=0.7),
                nbinsx=50,
                showlegend=False,
            ),
            row=2,
            col=1,
        )

        # Overlay normal distribution on sampling distribution
        x_range = np.linspace(sample_means.min(), sample_means.max(), 200)
        normal_pdf = stats.norm.pdf(x_range, mean_of_means, std_of_means)
        # Scale to match histogram
        hist_counts, _ = np.histogram(sample_means, bins=50)
        bin_width = (sample_means.max() - sample_means.min()) / 50
        scale_factor = len(sample_means) * bin_width

        fig.add_trace(
            go.Scatter(
                x=x_range,
                y=normal_pdf * scale_factor,
                name="Normal Distribution",
                mode="lines",
                line=dict(color="red", width=2),
                showlegend=True,
            ),
            row=2,
            col=1,
        )

        # Add vertical lines for means
        fig.add_vline(
            x=pop_mean,
            line=dict(color="red", dash="dash", width=2),
            annotation_text=f"μ = {pop_mean:.2f}",
            row=1,
            col=1,
        )

        fig.add_vline(
            x=mean_of_means,
            line=dict(color="red", dash="dash", width=2),
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
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        )

        return stats_content, {"display": "block"}, fig

    except Exception as e:
        return (
            [
                dmc.Alert(
                    f"Error: {str(e)}",
                    title="Error",
                    color="red",
                    icon=DashIconify(icon="mdi:alert-circle"),
                )
            ],
            {"display": "none"},
            {},
        )
