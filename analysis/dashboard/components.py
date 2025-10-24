import dash_bootstrap_components as dbc
from dash import html

def metric_card(title, value, subtext=None, extra=None):
    return dbc.Card(
        dbc.CardBody([
            html.H6(title, className="text-muted mb-1"),
            html.H3(f"{value:,}", className="fw-bold mb-2"),
            html.Div(subtext, className="text-secondary", style={"fontSize": "1.15rem"}),
            html.Div(extra or "", className="mt-2"),
        ]),
        class_name="shadow-sm h-100",
        style={
            "borderRadius": "12px",
            "border": "1px solid #E0E0E0",
            "minHeight": "160px",
        },
    )
