from dash import html, dcc
import dash_bootstrap_components as dbc


def my_footer():
    return html.Footer(
        dbc.Container(
            children=[
                dbc.Row(
                    [
                        dbc.Col(
                            dcc.Markdown(
                                """
                            © 2022 - Heat and Health Research Incubator, USyd
                            
                            Version: 0.0.3
                            """
                            ),
                            width=True,
                        ),
                        dbc.Col(
                            html.Img(
                                src="../assets/icons/HHRI logo.png", width="125px"
                            ),
                            width="auto",
                        ),
                    ]
                )
            ],
            className="p-2",
        ),
        style={"background": "#E64626"},
    )
