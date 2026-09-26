"""Dashboard interactivo de retrasos de vuelos (tarea)."""

from pathlib import Path

import pandas as pd
import plotly.express as px
from dash import Dash, Input, Output, dcc, html
from plotly.graph_objects import Figure

# --------------------------------------------------------------------- datos
DATA_FILE = Path(__file__).with_name("airline_data.csv")

df = pd.read_csv(
    DATA_FILE,
    encoding="ISO-8859-1",
    dtype={
        "Div1Airport": str,
        "Div1TailNum": str,
        "Div2Airport": str,
        "Div2TailNum": str,
    },
)

app = Dash(__name__)

# -------------------------------------------------------------------- layout
app.layout = html.Div(
    style={
        "fontFamily": "Segoe UI, Arial, sans-serif",
        "padding": "24px",
        "backgroundColor": "#f4f6f9",
        "minHeight": "100vh",
    },
    children=[
        html.H1(
            "Tablero de Control: Analisis de Retrasos de Vuelos",
            style={
                "textAlign": "center",
                "color": "#1f2937",
                "marginBottom": "20px",
                "fontWeight": "600",
            },
        ),
        html.Div(
            style={
                "display": "flex",
                "justifyContent": "center",
                "alignItems": "center",
                "gap": "12px",
                "marginBottom": "28px",
            },
            children=[
                html.Label(
                    "Seleccione el ano a analizar:",
                    style={
                        "fontSize": "16px",
                        "fontWeight": "500",
                        "color": "#374151",
                    },
                ),
                dcc.Input(
                    id="input-year",
                    type="number",
                    value=2010,
                    min=int(df["Year"].min()),
                    max=int(df["Year"].max()),
                    step=1,
                    style={
                        "height": "38px",
                        "width": "120px",
                        "fontSize": "16px",
                        "padding": "4px 10px",
                        "borderRadius": "6px",
                        "border": "1px solid #d1d5db",
                    },
                ),
            ],
        ),
        html.Div(
            style={"display": "flex", "gap": "20px", "marginBottom": "20px"},
            children=[
                html.Div(
                    dcc.Graph(id="carrier-plot"),
                    style={
                        "flex": "1",
                        "backgroundColor": "#ffffff",
                        "borderRadius": "8px",
                        "padding": "10px",
                        "boxShadow": "0 1px 3px rgba(0,0,0,0.1)",
                    },
                ),
                html.Div(
                    dcc.Graph(id="weather-plot"),
                    style={
                        "flex": "1",
                        "backgroundColor": "#ffffff",
                        "borderRadius": "8px",
                        "padding": "10px",
                        "boxShadow": "0 1px 3px rgba(0,0,0,0.1)",
                    },
                ),
            ],
        ),
        html.Div(
            style={"display": "flex", "gap": "20px", "marginBottom": "20px"},
            children=[
                html.Div(
                    dcc.Graph(id="nas-plot"),
                    style={
                        "flex": "1",
                        "backgroundColor": "#ffffff",
                        "borderRadius": "8px",
                        "padding": "10px",
                        "boxShadow": "0 1px 3px rgba(0,0,0,0.1)",
                    },
                ),
                html.Div(
                    dcc.Graph(id="security-plot"),
                    style={
                        "flex": "1",
                        "backgroundColor": "#ffffff",
                        "borderRadius": "8px",
                        "padding": "10px",
                        "boxShadow": "0 1px 3px rgba(0,0,0,0.1)",
                    },
                ),
            ],
        ),
        html.Div(
            style={"display": "flex", "justifyContent": "center"},
            children=[
                html.Div(
                    dcc.Graph(id="late-plot"),
                    style={
                        "width": "100%",
                        "backgroundColor": "#ffffff",
                        "borderRadius": "8px",
                        "padding": "10px",
                        "boxShadow": "0 1px 3px rgba(0,0,0,0.1)",
                    },
                )
            ],
        ),
    ],
)


# ------------------------------------------------------------------ calculos
def compute_info(datos, entered_year):
    df_year = datos[datos["Year"] == int(entered_year)]

    carrier_data = (
        df_year.groupby(["Month", "Reporting_Airline"])["CarrierDelay"]
        .mean()
        .reset_index()
    )
    weather_data = (
        df_year.groupby(["Month", "Reporting_Airline"])["WeatherDelay"]
        .mean()
        .reset_index()
    )
    nas_data = (
        df_year.groupby(["Month", "Reporting_Airline"])["NASDelay"]
        .mean()
        .reset_index()
    )
    security_data = (
        df_year.groupby(["Month", "Reporting_Airline"])["SecurityDelay"]
        .mean()
        .reset_index()
    )
    late_data = (
        df_year.groupby(["Month", "Reporting_Airline"])["LateAircraftDelay"]
        .mean()
        .reset_index()
    )

    return carrier_data, weather_data, nas_data, security_data, late_data


def _crear_figura_vacia(mensaje):
    fig = Figure()
    fig.update_layout(
        title={"text": mensaje, "x": 0.5, "xanchor": "center"},
        xaxis={"visible": False},
        yaxis={"visible": False},
        template="plotly_white",
        height=380,
    )
    return fig


# ------------------------------------------------------------------ callback
@app.callback(
    [
        Output("carrier-plot", "figure"),
        Output("weather-plot", "figure"),
        Output("nas-plot", "figure"),
        Output("security-plot", "figure"),
        Output("late-plot", "figure"),
    ],
    Input("input-year", "value"),
)
def get_graph(entered_year):
    if entered_year is None:
        fig_vacia = _crear_figura_vacia("Ingrese un ano valido para visualizar los datos")
        return fig_vacia, fig_vacia, fig_vacia, fig_vacia, fig_vacia

    try:
        val_year = int(entered_year)
    except (ValueError, TypeError):
        fig_vacia = _crear_figura_vacia("El ano introducido no es valido")
        return fig_vacia, fig_vacia, fig_vacia, fig_vacia, fig_vacia

    if val_year not in df["Year"].values:
        fig_vacia = _crear_figura_vacia(f"No hay registros disponibles para el ano {val_year}")
        return fig_vacia, fig_vacia, fig_vacia, fig_vacia, fig_vacia

    carrier_data, weather_data, nas_data, security_data, late_data = compute_info(
        df, val_year
    )

    graficos_config = [
        (carrier_data, "CarrierDelay", f"Retraso promedio por Aerolinea (Carrier) - {val_year}"),
        (weather_data, "WeatherDelay", f"Retraso promedio por Clima (Weather) - {val_year}"),
        (nas_data, "NASDelay", f"Retraso promedio por Sistema Aereo (NAS) - {val_year}"),
        (security_data, "SecurityDelay", f"Retraso promedio por Seguridad - {val_year}"),
        (late_data, "LateAircraftDelay", f"Retraso promedio por Aeronave Tardia - {val_year}"),
    ]

    figuras = []
    for data, col_y, titulo in graficos_config:
        fig = px.line(
            data,
            x="Month",
            y=col_y,
            color="Reporting_Airline",
            title=titulo,
            template="plotly_white",
            color_discrete_sequence=px.colors.qualitative.Bold,
            labels={
                "Month": "Mes",
                col_y: "Tiempo promedio (minutos)",
                "Reporting_Airline": "Aerolinea",
            },
        )
        fig.update_layout(
            xaxis=dict(tickmode="linear", dtick=1),
            margin=dict(l=40, r=40, t=50, b=40),
            height=380,
        )
        figuras.append(fig)

    return figuras[0], figuras[1], figuras[2], figuras[3], figuras[4]


# --------------------------------------------------------------- produccion
server = app.server

if __name__ == "__main__":
    app.run(debug=True, port=8050)
```[cite: 1, 3]

5. Haz clic en el botón verde **Commit changes...** abajo a la derecha.

---

### Paso 2: Verificar que `airline_data.csv` esté en la raíz de GitHub

1. En la lista principal de archivos de ese mismo repositorio en GitHub, asegúrate de que el archivo `airline_data.csv` esté visible[cite: 3].
2. Si no está: haz clic en **Add file** -> **Upload files**, arrastra `airline_data.csv` desde tu computadora y presiona **Commit changes**[cite: 3].

---

### Paso 3: Esperar el redespliegue y probar

1. Abre tu panel de **Render** y ve a la sección **Logs**[cite: 7].
2. Verás que Render detectará automáticamente el commit guardado y empezará a desplegar (`Deploying...`)[cite: 3, 13].
3. Espera 1 minuto hasta que vuelva a decir **`Your service is live`**[cite: 3, 13].
4. Abre el enlace en una pestaña nueva o en una ventana de incógnito:  
   `[https://programacion-analisis-de-datos.onrender.com](https://programacion-analisis-de-datos.onrender.com)`[cite: 2, 13]
5. Presiona **Ctrl + F5** para forzar la recarga del navegador sin caché.

Aparecerá el título principal, la caja para ingresar el año con el `2010` puesto por defecto y los 5 gráficos interactivos trazados[cite: 1, 3].
