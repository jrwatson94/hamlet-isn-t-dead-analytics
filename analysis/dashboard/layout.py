from dash import dcc, html
import dash_bootstrap_components as dbc
import pandas as pd
from components import metric_card
from figures import make_reach_likes_fig, make_heatmap_image_component, make_top_conversion_table
from data import df, conv

metrics = [
    "Reach", "Likes", "Comments", "Shares", "Saved",
    "Total Interactions", "Plays", "Views", "Follows"
]

for col in metrics:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

total_reach = df["Reach"].sum() if "Reach" in df else 0
average_reach = df["Reach"].mean() if "Reach" in df else 0
total_likes = df["Likes"].sum() if "Likes" in df else 0
total_comments = df["Comments"].sum() if "Comments" in df else 0
total_shares = df["Shares"].sum() if "Shares" in df else 0
total_saves = df["Saved"].sum() if "Saved" in df else 0
total_interactions = df["Total Interactions"].sum() if "Total Interactions" in df else 0
total_views = df["Views"].sum() if "Views" in df else 0
total_follows = df["Follows"].sum() if "Follows" in df else 0

fig = make_reach_likes_fig(df)
insights_component = make_heatmap_image_component()

followers_pct, nonfollowers_pct = 40, 60

cards = [
    metric_card(
        "Views",
        total_views,
        extra=html.Div([
            dbc.Progress(
                children=[
                    dbc.Progress(value=followers_pct, color="primary", bar=True,
                                 style={"borderRadius": "8px 0 0 8px"}),
                ],
                style={"height": "20px", "borderRadius": "8px", "backgroundColor": "#e5e5e5"},
            ),
            html.Div(
                [
                    html.Span(f"From followers — {followers_pct}%", className="me-auto"),
                    html.Span(f"From non-followers — {nonfollowers_pct}%", className="ms-auto"),
                ],
                className="d-flex justify-content-between mt-1 text-dark fw-semibold",
                style={"fontSize": "0.95rem"}
            )
        ])
    ),
    metric_card(
        "Reach",
        total_reach,
        subtext=html.Span(f"Average Reach: {average_reach:,.2f}", style={"fontWeight": "700"})
    ),
    metric_card(
        "Interactions",
        total_interactions,
        subtext=html.Span(
            f"Likes {total_likes:,.0f} | Comments {total_comments:,.0f} | Shares {total_shares:,.0f}",
            style={"fontWeight": "700"}
        )
    ),
    metric_card(
        "Follows",
        total_follows,
        subtext=f"Total Saves: {total_saves:,.0f}"
    ),
]

layout = dbc.Container([
    html.H2("📊 Social Media Overview Dashboard", className="mt-3 mb-4 fw-bold text-center"),

    dbc.Row([
        dbc.Col(cards[0], md=6, className="mb-3"),
        dbc.Col(cards[1], md=6, className="mb-3"),
    ]),
    dbc.Row([
        dbc.Col(cards[2], md=6, className="mb-3"),
        dbc.Col(cards[3], md=6, className="mb-3"),
    ]),

    html.Hr(),

    dbc.Row([
        dbc.Col(dcc.Graph(id="reach-likes-graph", figure=fig), md=12)
    ], className="mt-3"),

    dbc.Row([
        dbc.Col(insights_component, md=12)
    ], className="mt-4"),

    html.Hr(),

    # --- NEW SECTION: TOP CONVERSION POSTS ---
    html.H3("Follow Conversion Rate", className="fw-bold mt-4 mb-3 text-center"),
    dbc.Row([
        dbc.Col(
            make_top_conversion_table(conv),  # <-- new table
            md=12,
            className="mb-4"
        )
    ]),

    dbc.Modal(
        [
            dbc.ModalHeader(dbc.ModalTitle("Post Details"), close_button=True),
            dbc.ModalBody(id="modal-body", style={"fontSize": "1.1rem"})
        ],
        id="details-modal",
        is_open=False,
        centered=True,
        size="md",
        backdrop="static",
    )
], fluid=True)
