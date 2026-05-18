import plotly.express as px
from dash import Dash, html, dcc, Input, Output
import pandas as pd
import os

base_dir = os.path.dirname(os.path.abspath(__file__))
stopsCSV = os.path.join(base_dir, "stops.csv")
routesCSV = os.path.join(base_dir, "routes.csv")
linksCSV = os.path.join(base_dir, "links.csv")
stopsdf = pd.read_csv(stopsCSV)
routesdf = pd.read_csv(routesCSV)
linksdf = pd.read_csv(linksCSV)

stopCounts = linksdf["stopID"].value_counts().reset_index()
stopCounts.columns = ["stopID", "routeCount"]
stopsdf = stopsdf.merge(stopCounts, on="stopID", how="left")
stopsdf["routeCount"] = stopsdf["routeCount"].fillna(0)

buttonClicks = 0

fig = px.scatter_mapbox(
    stopsdf,
    lat="lat",
    lon="lon",
    hover_name="name",
    hover_data={"stopID":True},
    color="routeCount",
    color_continuous_scale="Viridis",
    zoom=8,
    height=600
)
fig.update_layout(
    mapbox_style="open-street-map",
    mapbox_center={"lat": 54.57566, "lon": -1.17177},
    margin={"r":0,"t":0,"l":0,"b":0}
)

app = Dash(__name__)
@app.callback(
        Output("stopInfo", "children"),
        Input("map", "clickData")
)
def display_info(clickData):
    if clickData is None:
        return html.Div(
                    style = {
                        "background-color" : "#ffffff",
                        "width" : "100%",
                        "border-radius" : "10px"
                    },
                    children=[
                        "Click a stop to see information"
                    ]
                )
    stopID = clickData["points"][0]["customdata"][0]
    numRoutes = clickData["points"][0]["cluster.color"]
    links = linksdf[linksdf["stopID"] == stopID]
    routes = routesdf[routesdf["routeID"].isin(links["routeID"])]

    if numRoutes < 2:
        connectivity = "Very Poor"
    elif numRoutes < 4:
        connectivity = "Poor"
    elif numRoutes < 10:
        connectivity = "Moderate"
    elif numRoutes < 25:
        connectivity = "Good"
    else:
        connectivity = "Very Good"

    allRoutes = "Routes: "
    for routeID in links["routeID"]:
        allRoutes += routeID + ", "
    
    allOperators = "Operators: "
    for operator in routes["operator"].unique():
        allOperators += operator + ", "

    return html.Div(
                    style = {
                        "background-color" : "#ffffff",
                        "width" : "100%",
                        "border-radius" : "10px"
                    },
                    children=[
                        html.Div(
                            style={
                                "backgroundColor" : "#57b6a7",
                                "width" : "100%",
                                "border-radius" : "10px 10px 0px 0px"
                            },
                            children=[
                                html.H2(
                                    str(clickData["points"][0]["hovertext"]),
                                    style={
                                        "margin" : "0px"
                                    }
                                )
                            ]
                        ),
                        html.Div(
                            style={
                                "padding" : "20px"
                            },
                            children=[
                                html.P(
                                    "Routes Serving Stop: " + str(len(links))
                                ),
                                html.P(
                                    "Operators Serving Stop: " + str(len(routes["operator"].unique()))
                                ),
                                html.P(
                                    "Connectivity of Stop: " + connectivity
                                ),
                                html.P(
                                    allRoutes
                                ),
                                html.P(
                                    allOperators
                                )
                            ]
                        )
                    ]
                )
    
@app.callback(
    Output("map", "figure"),
    Input("route-dropdown", "value"),
    Input("operator-dropdown", "value"),
    Input("routeCount-slider", "value"),
    Input("stopStart-dropdown", "value"),
    Input("stopStop-dropdown", "value"),
    Input("findRoute-button", "n_clicks")
)
def update_map(selectedRoute, selectedOperator, selectedCount,start, end, clicks):
    if start is not None and end is not None and clicks is not None:
        filteredStops = stopsdf
        if clicks >= buttonClicks:
            startStop = stopsdf[stopsdf["name"] == start]["stopID"]
            endStop = stopsdf[stopsdf["name"] == end]["stopID"]

            startRoutes = linksdf[linksdf["stopID"].isin(startStop)]["routeID"]
            endRoutes = linksdf[linksdf["stopID"].isin(endStop)]["routeID"]

            commonRoutes = set(startRoutes).intersection(set(endRoutes))

        if len(commonRoutes) > 0:
            routeLinks = linksdf[linksdf["routeID"].isin(commonRoutes)]
            stopIDs = routeLinks["stopID"]
            filteredStops = stopsdf[stopsdf["stopID"].isin(stopIDs)]
        else:
            filteredStops = stopsdf
    else:
        if selectedRoute == "ALL" or selectedRoute == None:
            filteredStops = stopsdf
        else:
            filtered = linksdf[linksdf["routeID"] == selectedRoute]
            stops = filtered["stopID"]
            filteredStops = stopsdf[stopsdf["stopID"].isin(stops)]

        if selectedOperator == "ALL" or selectedOperator == None:
            filteredStops = filteredStops
        else:
            filteredRoute = routesdf[routesdf["operator"] == selectedOperator]
            routeIDs = filteredRoute["routeID"]
            filtered = linksdf[linksdf["routeID"].isin(routeIDs)]
            stops = filtered["stopID"]
            filteredStops = stopsdf[stopsdf["stopID"].isin(stops)]

        filteredStops = filteredStops[filteredStops["routeCount"] >= selectedCount[0]]
        filteredStops = filteredStops[filteredStops["routeCount"] <= selectedCount[1]]

    fig = px.scatter_mapbox(
        filteredStops,
        lat="lat",
        lon="lon",
        hover_name="name",
        hover_data={"stopID":True},
        color="routeCount",
        color_continuous_scale="Viridis",
        zoom=8,
        height=600
    )
    fig.update_layout(
        mapbox_style="open-street-map",
        mapbox_center={"lat": filteredStops["lat"].mean(), "lon": filteredStops["lon"].mean()},
        margin={"r":0,"t":0,"l":0,"b":0}
    )
    return fig

app.layout = html.Div(
    style={
        "backgroundColor": "#e0e0e0",
        "padding": "20px",
    },
    children = [
        html.H1(
            "Bus Routes"
        ),
        html.Div(
            style={
                "display" : "flex",
                "gap" : "10px",
                "padding-bottom" : "10px"
            },
            children = [
                html.Div(
                    style={
                        "backgroundColor": "#f5f7fa",
                        "color": "#1f2630",
                        "width" : "33%",
                        "margin-right" : "10px",
                        "border-radius" : "10px"
                    },
                    children= [
                        html.Div(
                            style={
                                "backgroundColor" : "#57b6a7",
                                "width" : "100%",
                                "height" : "30%",
                                "border-radius" : "10px 10px 0px 0px"
                            },
                            children= [
                                html.P(
                                    "Number of Stops",
                                    style={
                                        "color" : "#193531",
                                        "margin" : "0",
                                        "padding" : "10px"
                                    }
                                )
                            ]
                        ),
                        html.H1(
                            str(len(stopsdf)),
                            style={
                                "textAlign" : "center"
                            }
                        )
                    ]
                ),
                html.Div(
                    style={
                        "backgroundColor": "#f5f7fa",
                        "color": "#1f2630",
                        "width" : "33%",
                        "margin-right" : "10px",
                        "border-radius" : "10px"
                    },
                    children= [
                        html.Div(
                            style={
                                "backgroundColor" : "#57b6a7",
                                "width" : "100%",
                                "height" : "30%",
                                "border-radius" : "10px 10px 0px 0px"
                            },
                            children= [
                                html.P(
                                    "Number of Routes",
                                    style={
                                        "color" : "#193531",
                                        "margin" : "0",
                                        "padding" : "10px"
                                    }
                                )
                            ]
                        ),
                        html.H1(
                            str(len(routesdf)),
                            style={
                                "textAlign" : "center"
                            }
                        )
                    ]
                ),
                html.Div(
                    style={
                        "backgroundColor": "#f5f7fa",
                        "color": "#1f2630",
                        "width" : "33%",
                        "margin-right" : "10px",
                        "border-radius" : "10px"
                    },
                    children= [
                        html.Div(
                            style={
                                "backgroundColor" : "#57b6a7",
                                "width" : "100%",
                                "height" : "30%",
                                "border-radius" : "10px 10px 0px 0px"
                            },
                            children= [
                                html.P(
                                    "Number of Operators",
                                    style={
                                        "color" : "#193531",
                                        "margin" : "0",
                                        "padding" : "10px"
                                    }
                                )
                            ]
                        ),
                        html.H1(
                            str(len(routesdf["operator"].unique())),
                            style={
                                "textAlign" : "center"
                            }
                        )
                    ]
                ),
            ]
        ),
        html.Div(
            style={
                "display" : "flex",
                "gap" : "10px",
                "padding-bottom" : "10px",
            },
            children = [
                html.Div(
                style={
                    "backgroundColor": "#f5f7fa",
                    "color": "#1f2630",
                    "padding": "20px",
                    "width" : "80%",
                    "margin-right" : "10px",
                    "border-radius" : "10px"
                },
                children= [
                    dcc.Graph(id="map", figure=fig)
                ]
            ),
            html.Div(
                style={
                    "backgroundColor": "#f5f7fa",
                    "color": "#1f2630",
                    "width" : "20%",
                    "border-radius" : "10px"
                },
                children= [
                    html.Div(
                            style={
                                "backgroundColor" : "#57b6a7",
                                "width" : "100%",
                                #"height" : "30%",
                                "border-radius" : "10px 10px 0px 0px"
                            },
                            children= [
                                html.H2(
                                    "Filters",
                                    style={
                                        "color" : "#193531",
                                        "margin" : "0",
                                        "padding" : "10px"
                                    }
                                )
                            ]
                        ),
                    html.Div(
                        style={
                            "padding" : "20px",
                        },
                        children = [
                            html.P(
                                "Route",
                                style={
                                    "margin-top" : "20%"
                                }
                            ),
                            dcc.Dropdown(
                                id="route-dropdown",
                                options = [{"label" : "All", "value" : "ALL"}] + [
                                    {"label" : r, "value" : r} for r in routesdf["routeID"].unique()
                                ],
                                value = "ALL"
                            ),
                            html.P(
                                "Operator",
                                style={
                                    "margin-top" : "20%"
                                }
                            ),
                            dcc.Dropdown(
                                id="operator-dropdown",
                                options = [{"label" : "All", "value" : "ALL"}] + [
                                    {"label" : r, "value" : r} for r in routesdf["operator"].unique()
                                ],
                                value = "ALL"
                            ),
                            html.P(
                                "Routes using Stop",
                                style={
                                    "margin-top" : "20%",
                                }
                            ),
                            dcc.RangeSlider(
                                id = "routeCount-slider",
                                min = 0,
                                max = int(stopsdf["routeCount"].max()),
                                step = 1,
                                value = [0, int(stopsdf["routeCount"].max())],
                                marks = {
                                    i: str(i) for i in range(0, int(stopsdf["routeCount"].max())+1, 5)
                                }
                            ),
                            html.P(
                                "Route Finder",
                                style={
                                    "margin-top" : "20%",
                                }
                            ),
                            dcc.Dropdown(
                                id="stopStart-dropdown",
                                    options = [
                                        {"label" : r, "value" : r} for r in stopsdf["name"].unique()
                                    ],
                                ),
                            dcc.Dropdown(
                                id="stopStop-dropdown",
                                    options = [
                                        {"label" : r, "value" : r} for r in stopsdf["name"].unique()
                                    ],
                                ),
                            dcc.Button(
                                "Find Route",
                                id="findRoute-button",
                                style={
                                    "color" : "#193531",
                                    "background-color" : "#57b6a7"
                                }
                            )
                        ]
                    )
                ]
            )
            ]
        ),
        html.Div(
            style={
                "display" : "flex",
                "gap" : "10px"
            },
            id = "stopInfo",
            children = [
                html.Div(
                    style = {
                        "background-color" : "#ffffff",
                        "width" : "100%",
                        "border-radius" : "10px"
                    },
                    children=[
                        "Click a stop to see information"
                    ]
                )
            ]
        )
    ]
)

app.run()