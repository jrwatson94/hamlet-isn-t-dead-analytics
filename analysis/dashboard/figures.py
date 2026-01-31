import plotly.express as px
from dash import html
import base64
from pathlib import Path
from settings import HEATMAP_PATH
from dash import dash_table
import pandas as pd


def make_reach_likes_fig(df):
    custom_cols = []
    if "Publish time" in df.columns:
        custom_cols.append("Publish time")
    if "Permalink" in df.columns:
        custom_cols.append("Permalink")

    fig = px.scatter(
        df,
        x="Reach",
        y="Likes",
        title="Reach vs Likes",
        hover_data={col: True for col in ["Reach", "Likes", *custom_cols]},
        custom_data=custom_cols,
        color_discrete_sequence=["#1f77b4"],
    )
    fig.update_layout(
        xaxis=dict(range=[0, 7000], title="Reach"),
        yaxis=dict(range=[0, 225], title="Likes"),
        template="simple_white",
        height=450,
        margin=dict(l=20, r=20, t=40, b=20),
    )
    fig.update_traces(marker=dict(size=9))
    return fig


def make_heatmap_image_component():
    """
    Return an <img> wrapped in a Div that shows the weekly heatmap PNG.
    Uses base64 data URI so Dash can serve it without copying into assets.
    """
    p = Path(HEATMAP_PATH)
    if not p.exists():
        return html.Div(
            [
                html.H5("Insights"),
                html.Div(
                    f"Heatmap not found at: {p}",
                    className="text-danger",
                    style={"fontWeight": 600},
                ),
            ]
        )

    b64 = base64.b64encode(p.read_bytes()).decode("ascii")
    src = f"data:image/png;base64,{b64}"

    return html.Div(
        [
            html.H5("Insights", className="fw-bold mb-3"),
            html.Img(
                src=src,
                style={
                    "maxWidth": "75%",
                    "height": "auto",
                    "border": "1px solid #e5e5e5",
                    "borderRadius": "10px",
                    "boxShadow": "0 4px 14px rgba(0,0,0,0.06)",
                },
                alt="Weekly heatmap and curve",
            ),
        ],
        className="mt-4",
    )


def make_top_conversion_table(df, limit=15):
    d = df.sort_values("Conversion", ascending=False).head(limit).copy()

    def img_tag(url):
        if isinstance(url, str) and url.startswith("http"):
            return (
                "<img src='{0}' "
                "style='height:80px;width:80px;object-fit:cover;"
                "border-radius:6px'/>"
            ).format(url)
        return ""

    d["Image"] = d["Media URL"].apply(img_tag)
    d["Conversion"] = d["Conversion"].round(5)

    cols = ["Image","Description","Follows","Reach","Likes","Conversion"]
    d = d[cols]

    return dash_table.DataTable(
        data=d.to_dict("records"),
        columns=[
            (
                {"name": c, "id": c, "presentation": "markdown"}
                if c=="Image"
                else {"name": c, "id": c}
            )
            for c in cols
        ],
        markdown_options={"html": True},
        style_cell={
            "fontFamily":"Arial",
            "fontSize":"10px",
            "whiteSpace":"normal",
            "height":"auto",
            "padding":"6px",
        },
        style_data={"lineHeight":"10px"},
        style_table={"overflowX":"auto"},

        # ---- NEW COLUMN SIZING BELOW ----
        style_cell_conditional=[
            { "if": {"column_id":"Image"}, "width":"130px" },
            { "if": {"column_id":"Description"}, "maxWidth":"260px" },
            { "if": {"column_id":"Conversion"}, "fontWeight":"bold", "textAlign": "center", },
        ],
    )
