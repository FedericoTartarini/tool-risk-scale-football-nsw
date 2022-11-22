import os

from dash import html, dcc, Output, Input, State, callback
import dash_bootstrap_components as dbc
import dash_leaflet as dl
from dash.exceptions import PreventUpdate
from my_app.charts import hss_palette, risk_map
import dash
import pandas as pd

from utils import sma_risk_messages, sports_category

dash.register_page(__name__, path="/")


def layout():
    return dbc.Container(
        children=[html.Div(id="map-component"), html.Div(id="body-home")],
        className="p-2",
    )


@callback(
    Output("body-home", "children"),
    Input("local-storage-settings", "data"),
)
def body(data):
    print(data)
    if not data:
        return (
            dbc.Alert(
                "Please select a sport in the Settings Page",
                id="sport-selection",
                color="danger",
                className="mt-2",
            ),
        )
    if not data["id-class"]:
        return (
            dbc.Alert(
                "Please return to the Settings Page and select a sport",
                id="sport-selection",
                color="danger",
                className="mt-2",
            ),
        )
    else:
        return [
            dbc.Row(
                html.Div(
                    id="id-icon-sport",
                    className="p-2",
                ),
                justify="center",
            ),
            dbc.Row(
                dbc.Alert(
                    [
                        dbc.Col(
                            [
                                html.H3(
                                    "The current Heat Stress Risk:",
                                ),
                                dcc.Loading(
                                    html.H1(
                                        className="alert-heading",
                                        id="value-hss-current",
                                    ),
                                ),
                            ],
                            style={"text-align": "center"},
                        ),
                        html.Hr(),
                        html.Div(id="div-icons-suggestions"),
                    ],
                    className="mt-1",
                    id="id-alert-risk-current",
                ),
            ),
            dbc.Accordion(
                dbc.AccordionItem(
                    [
                        html.P(
                            id="value-risk-description",
                        ),
                        html.P(
                            "You should:",
                        ),
                        dcc.Markdown(
                            id="value-risk-suggestions",
                            className="mb-0",
                        ),
                    ],
                    title="Suggestions: ",
                ),
                start_collapsed=True,
                # flush=True,
                className="my-2",
                id="id-accordion-risk-current",
            ),
            html.H2("Risk value (next 20 hours)"),
            html.Div(id="fig-hss-trend"),
        ]


def icon_component(src, message, size="50px"):
    return dbc.Row(
        [
            dbc.Col(
                html.Img(src=src, width=size),
                style={"text-align": "right"},
                width="auto",
            ),
            dbc.Col(
                message,
                width="auto",
                style={"text-align": "left"},
            ),
        ],
        align="center",
        justify="center",
        className="my-1",
    )


@callback(
    Output("local-storage-location", "data"),
    Input("map", "location_lat_lon_acc"),
    State("local-storage-location", "data"),
)
def update_location_and_forecast(location, data):
    data = data or {"lat": -33.888, "lon": 151.185}

    if location:
        data["lat"] = location[0]
        data["lon"] = location[1]

    return data


@callback(
    Output("id-icon-sport", "children"),
    Input("local-storage-settings", "data"),
)
def update_location_and_forecast(data_sport):

    file_name = f"{data_sport['id-class']}.png"
    path = os.path.join(os.getcwd(), "assets", "icons", file_name)
    # source https://www.theolympicdesign.com/olympic-design/pictograms/tokyo-2020/
    if os.path.isfile(path):
        return icon_component(
            f"../assets/icons/{data_sport['id-class']}.png", data_sport["id-class"]
        )
    else:
        return icon_component("../assets/icons/sports.png", data_sport["id-class"])


@callback(
    Output("fig-hss-trend", "children"),
    Input("session-storage-weather", "modified_timestamp"),
    State("session-storage-weather", "data"),
    State("local-storage-settings", "data"),
)
def update_fig_hss_trend(ts, data, data_sport):
    try:
        df = pd.read_json(data, orient="table")
        return dcc.Graph(
            figure=risk_map(df, sports_category[data_sport["id-class"]]),
            config={"staticPlot": True},
        )
    except ValueError:
        raise PreventUpdate


@callback(
    Output("value-hss-current", "children"),
    Output("id-alert-risk-current", "color"),
    Output("value-risk-description", "children"),
    Output("value-risk-suggestions", "children"),
    Output("div-icons-suggestions", "children"),
    Input("session-storage-weather", "modified_timestamp"),
    State("session-storage-weather", "data"),
)
def update_alert_hss_current(ts, data):
    try:
        df = pd.read_json(data, orient="table")
        color = hss_palette[df["risk_value"][0]]
        description = sma_risk_messages[df["risk"][0]]["description"].capitalize()
        suggestion = sma_risk_messages[df["risk"][0]]["suggestions"].capitalize()
        icons = [
            icon_component("../assets/icons/water-bottle.png", "Stay hydrated"),
            icon_component("../assets/icons/tshirt.png", "Wear light clothing"),
        ]
        if suggestion == "moderate":
            icons.append(
                icon_component("../assets/icons/pause.png", "Rest Breaks"),
            )
        if suggestion == "high":
            icons.append(
                icon_component("../assets/icons/pause.png", "Rest Breaks"),
            )
            icons.append(
                icon_component("../assets/icons/slush-drink.png", "Active Cooling"),
            )
        if suggestion == "extreme":
            icons = [
                icon_component(
                    "../assets/icons/stop.png", "Stop Activity", size="100px"
                ),
            ]
        return f"{df['risk'][0]}".capitalize(), color, description, suggestion, icons
    except ValueError:
        raise PreventUpdate


@callback(
    Output("map-component", "children"),
    Input("local-storage-location", "modified_timestamp"),
    State("local-storage-location", "data"),
)
def on_location_change(ts, data):

    start_location_control = True
    if data:
        start_location_control = False
    print(data)

    data = data or {"lat": -33.888, "lon": 151.185}
    return dl.Map(
        [
            dl.TileLayer(maxZoom=13, minZoom=9),
            dl.LocateControl(
                startDirectly=start_location_control,
                options={"locateOptions": {"enableHighAccuracy": True}},
            ),
            dl.Marker(position=[data["lat"], data["lon"]]),
            dl.GestureHandling(),
        ],
        id="map",
        style={
            "width": "100%",
            "height": "25vh",
            "margin": "auto",
            "display": "block",
            # "-webkit-filter": "grayscale(100%)",
            # "filter": "grayscale(100%)",
        },
        center=(data["lat"], data["lon"]),
        zoom=13,
    )
