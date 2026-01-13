import os
import socket
import urllib.parse

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import Dash, dcc, html, Input, Output, callback, no_update, ctx
from sqlalchemy import create_engine, text

# --- 1. Database & Data Functions ---

db_connection_str = os.environ.get("NEON_DB")
if not db_connection_str:
    raise ValueError("NEON_DB environment variable is not set.")

engine = create_engine(db_connection_str)
with open("sqls/get_latest_price.sql") as f:
    sql_latest_price = f.read()
with open("sqls/get_price.sql") as f:
    sql_price_per_station = f.read()

def get_latest_prices(fuel_type):
    query = text(sql_latest_price)
    return pd.read_sql(query, engine, params={"fuel_type": fuel_type})


def get_historical_prices(station_id):
    query = text(sql_price_per_station)
    return pd.read_sql(query, engine, params={"station_id": station_id})


def get_station_name(station_id):
    try:
        query = "SELECT name FROM public.stations WHERE station_id = %s"
        df = pd.read_sql(query, engine, params=(station_id,))
        if not df.empty:
            return df.iloc[0]['name']
    except Exception:
        pass
    return "Unknown Station"


def get_available_fuel_types():
    try:
        df = pd.read_sql(
            "SELECT DISTINCT fuel_type FROM public.fuel_prices ORDER BY fuel_type",
            engine)
        return df['fuel_type'].tolist()
    except Exception:
        return []


# --- 2. Styles ---

FLOAT_CARD_STYLE = {
    'position': 'absolute',
    'top': '20px',
    'left': '20px',
    'zIndex': '1000',
    'backgroundColor': 'white',
    'padding': '15px',
    'borderRadius': '8px',
    'boxShadow': '0 4px 6px rgba(0,0,0,0.1)',
    'width': '300px',
    'fontFamily': 'Arial, sans-serif'
}

DETAIL_CARD_STYLE = {
    'position': 'absolute',
    'bottom': '30px',
    'right': '30px',
    'zIndex': '1000',
    'backgroundColor': 'white',
    'padding': '20px',
    'borderRadius': '8px',
    'boxShadow': '0 4px 15px rgba(0,0,0,0.2)',
    'width': '350px',
    'display': 'none',
    'fontFamily': 'Arial, sans-serif'
}

# --- 3. App Initialization ---

app = Dash(__name__, suppress_callback_exceptions=True)
server = app.server

app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
        <style>
            body, html {
                margin: 0;
                padding: 0;
                width: 100%;
                height: 100%;
                overflow: hidden; 
                font-family: Arial, sans-serif;
            }
        </style>
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''

fuel_types = get_available_fuel_types()
initial_fuel = fuel_types[0] if fuel_types else None


# --- 4. Helper to Generate Map Figure ---

def generate_map_figure(fuel_type):
    fig = go.Figure()

    lat_center, lon_center = -40.9, 174.8
    zoom_level = 5

    if fuel_type:
        df = get_latest_prices(fuel_type)
        if not df.empty:
            # FIX: Use scatter_map (no deprecation warning)
            fig = px.scatter_map(
                df, lat="latitude", lon="longitude", color="price",
                custom_data=["brand", "price", "station_id", "name"],
                color_continuous_scale="Inferno",
                zoom=zoom_level,
                height=None
            )

            # FIX: Removed 'line' property which causes the crash in scatter_map
            fig.update_traces(
                hoverinfo='none',
                hovertemplate=None,
                marker=dict(size=12, opacity=0.9)
            )

    fig.update_layout(
        autosize=True,
        uirevision='fuel_map_constant_revision',
        map_style="carto-positron",
        map=dict(center=dict(lat=lat_center, lon=lon_center), zoom=zoom_level),
        margin={"r": 0, "t": 0, "l": 0, "b": 0},
        coloraxis_colorbar=dict(
            title="Price",
            yanchor="top", y=0.95,
            xanchor="right", x=0.99,
            len=0.4,
            thickness=15,
            bgcolor="rgba(255,255,255,0.9)",
            tickfont=dict(color="#333"),
            title_font=dict(color="#333")
        )
    )
    return fig


# --- 5. Layouts ---

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content',
             style={'width': '100vw', 'height': '100vh', 'position': 'relative'})
])


def layout_map():
    fig = generate_map_figure(initial_fuel)

    return html.Div([
        html.Div([
            html.H4("Fuel Price Dashboard", style={'marginTop': 0}),
            html.Label("Select Fuel Type:"),
            dcc.Dropdown(
                id='fuel-type-dropdown',
                options=[{'label': ft, 'value': ft} for ft in fuel_types],
                value=initial_fuel,
                clearable=False
            )
        ], style=FLOAT_CARD_STYLE),

        dcc.Graph(
            id='station-map',
            figure=fig,
            style={'position': 'absolute', 'top': 0, 'left': 0, 'height': '100%',
                   'width': '100%'},
            config={'scrollZoom': True, 'displayModeBar': True, 'responsive': True}
        ),

        html.Div(id='detail-card', style=DETAIL_CARD_STYLE, children=[
            html.Button("✕", id='close-card-btn', n_clicks=0,
                        style={'float': 'right', 'background': 'none', 'border': 'none',
                               'cursor': 'pointer',
                               'fontSize': '16px'}),
            html.H3(id='card-title', style={'marginTop': '0', 'paddingRight': '20px'}),
            html.Div(id='card-content'),
            html.Br(),
            html.A("View Historical Prices →", id='history-link', href="#",
                   target="_blank",
                   style={'color': 'blue', 'fontWeight': 'bold',
                          'textDecoration': 'underline'})
        ])
    ], style={'width': '100%', 'height': '100%'})


def layout_history(station_id):
    history_page_style = {
        'overflowY': 'auto',
        'height': '100vh',
        'width': '100vw',
        'boxSizing': 'border-box',
        'padding': '20px'
    }

    if not station_id:
        return html.Div([html.H3("Invalid Station ID.")], style={'padding': '50px'})

    station_name = get_station_name(station_id)
    df = get_historical_prices(station_id)

    if df.empty:
        fig = go.Figure().update_layout(title="No data available",
                                        font={'family': 'Arial'})
    else:
        fig = px.line(
            df, x="update_time", y="price", color="fuel_type",
            line_shape="hv", markers=True, title=f"Price History: {station_name} (NZ cents/L)"
        )
        fig.update_layout(font={'family': 'Arial'})

    return html.Div([
        html.H2(station_name),
        dcc.Graph(figure=fig, style={'height': '85vh'})
    ], style=history_page_style)


# --- 6. Callbacks ---

@callback(Output('page-content', 'children'),
          Input('url', 'pathname'),
          Input('url', 'search'))
def display_page(pathname, search):
    if pathname == '/history':
        station_id = None
        if search:
            parsed = urllib.parse.parse_qs(search.lstrip('?'))
            station_id = parsed.get('id', [None])[0]
        return layout_history(station_id)
    else:
        return layout_map()


@callback(
    Output('station-map', 'figure'),
    Input('fuel-type-dropdown', 'value'),
    prevent_initial_call=True
)
def update_map_figure(selected_fuel):
    if not selected_fuel: return no_update
    return generate_map_figure(selected_fuel)


@callback(
    Output('detail-card', 'style'),
    Output('card-title', 'children'),
    Output('card-content', 'children'),
    Output('history-link', 'href'),
    Input('station-map', 'clickData'),
    Input('close-card-btn', 'n_clicks'),
    prevent_initial_call=True
)
def handle_map_interaction(clickData, close_clicks):
    triggered_id = ctx.triggered_id

    if triggered_id == 'close-card-btn':
        style = DETAIL_CARD_STYLE.copy()
        style['display'] = 'none'
        return style, no_update, no_update, no_update

    if not clickData:
        return no_update, no_update, no_update, no_update

    point = clickData['points'][0]

    try:
        brand = point['customdata'][0]
        price = point['customdata'][1]
        station_id = point['customdata'][2]
        name = point['customdata'][3]
    except (IndexError, KeyError):
        return no_update, no_update, no_update, no_update

    content = html.Div([
        html.P([html.Strong("Brand: "), str(brand)]),
        html.P([html.Strong("Current Price: "), f"{price} NZ cents/L"]),
        html.P([html.Strong("Location: "),
                f"{point.get('lat', 0):.4f}, {point.get('lon', 0):.4f}"])
    ])

    style = DETAIL_CARD_STYLE.copy()
    style['display'] = 'block'

    history_href = f"/history?id={station_id}"

    return style, name, content, history_href


def find_available_port(start_port: int, tries: int = 100):
    """
    Find the first available port from {start_port} to {start_port + tries}
    :param start_port: The port that the program starts to scan, if it's occupied, the
    program will scan {start_port + 1}. If it's occupied again, try the next one...
    :param tries: Default 100, the maximum trying times from the start port.
    :return:
    """
    for i in range(tries):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.bind(("127.0.0.1", start_port + i))
            s.close()
            return start_port + i
        except OSError:
            pass
    raise Exception(f"Tried {tries} times, no available port from {start_port} to "
                    f"{start_port + tries}.")


if __name__ == '__main__':
    port = find_available_port(1024)
    app.run(debug=True, host='localhost', port=port)
