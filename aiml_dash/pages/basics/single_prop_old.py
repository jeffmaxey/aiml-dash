"""Single Proportion Test Page"""

import dash_mantine_components as dmc
from components.common import create_page_header


def layout():
    return dmc.Container(
        [
            create_page_header(
                "Single Proportion",
                "One-sample test for a single proportion",
                icon="carbon:percentage",
            ),
            dmc.Text(
                "Single Proportion Test - Coming Soon",
                ta="center",
                size="xl",
                c="dimmed",
                mt="xl",
            ),
        ],
        fluid=True,
    )
