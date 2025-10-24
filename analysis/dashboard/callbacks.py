from dash import Input, Output
import dash
from dash import html

def register_callbacks(app):
    @app.callback(
        Output("details-modal", "is_open"),
        Output("modal-body", "children"),
        Input("reach-likes-graph", "clickData"),
        Input("details-modal", "is_open"),
        prevent_initial_call=True,
    )
    def show_post_details(clickData, is_open):
        ctx = dash.callback_context
        if not ctx.triggered:
            return is_open, None

        trigger = ctx.triggered[0]["prop_id"].split(".")[0]

        if trigger == "reach-likes-graph" and clickData:
            pt = clickData["points"][0]
            reach = pt.get("x")
            likes = pt.get("y")
            custom = pt.get("customdata", []) or []
            date = custom[0] if len(custom) >= 1 else None
            link = custom[1] if len(custom) >= 2 else None

            if not date or str(date).strip().lower() in ["nan", "none", ""]:
                date = "—"

            permalink = ""
            if link and isinstance(link, str) and link.startswith("http"):
                permalink = html.A(
                    "Open Post ↗",
                    href=link,
                    target="_blank",
                    style={"color": "#1f77b4", "fontWeight": "600", "textDecoration": "none"},
                )

            body = html.Div([
                html.P(f"Reach: {reach:,.0f}", className="mb-1 fw-semibold"),
                html.P(f"Likes: {likes:,.0f}", className="mb-1 fw-semibold"),
                html.P(f"Date: {date}", className="mb-1 fw-semibold"),
                permalink,
            ])

            return True, body

        if trigger == "details-modal" and is_open:
            return False, None

        return is_open, None
