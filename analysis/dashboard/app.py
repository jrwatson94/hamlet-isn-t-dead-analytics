from dash import Dash
import dash_bootstrap_components as dbc
from layout import layout
from callbacks import register_callbacks

app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = "Social Media Overview Dashboard"
app.layout = layout

register_callbacks(app)

server = app.server

if __name__ == "__main__":
    app.run(debug=True)
