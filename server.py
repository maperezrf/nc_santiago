# ---------- Libraries
from turtle import ht, width
from dash import Dash, html, dcc, Input, Output
from matplotlib.pyplot import title
import plotly.express as px
import pandas as pd
import dash_bootstrap_components as dbc 

# ---------- Init
app = Dash(__name__,external_stylesheets=[dbc.themes.BOOTSTRAP], suppress_callback_exceptions=True)

# ---------- Styles
SIDEBAR_STYLE = {
    "position": "fixed",
    "top": 0,
    "left": 0,
    "bottom": 0,
    "width": "16rem",
    "padding": "2rem 1rem",
    "background-color": "#f8f9fa",
}

CONTENT_STYLE = {
    "margin-left": "18rem",
    "margin-right": "2rem",
    "padding": "2rem 1rem",
}

# ---------- Data 
con = pd.read_csv('input/con_fixed.csv', dtype=object) # Consolidado con arreglos 
alertas = pd.read_excel('input/220303_consolidado_alertas_nc.xlsx') # Alertas 

# ---------- Filters
hora = alertas.loc[alertas.tipo_alerta=='hora'].reset_index()
monto = alertas.loc[alertas.tipo_alerta=='monto'].reset_index()

# ---------- Groupby's
gb_cant_mes = con.groupby(['mes-nc'], sort=False)['Cautoriza'].nunique().reset_index()
#gb_cant_locales = con.groupby(['Desc_local'], sort=False)['Cautoriza'].nunique().reset_index()
h_x_fig = hora.groupby(["Desc_local","indicador"]).agg({"Cautoriza":"nunique",}).reset_index().sort_values("Cautoriza", ascending=False)
m_x_fig = monto.groupby(["Desc_local","indicador"]).agg({"Cautoriza":"nunique",}).reset_index().sort_values("Cautoriza", ascending=False)
gb_estado_alerta = alertas.groupby('indicador')['Cautoriza'].nunique().reset_index()

# ---------- Graphs

## Cantidad de NCs según mes de creación
fig = px.bar(gb_cant_mes, x="mes-nc", y="Cautoriza", text='Cautoriza', title='Cantidad de NCs según mes de creación',
labels={"mes-nc":'Mes de creación', 'Cautoriza':'Cantidad de NCS'})

## Cantidad de alertas por hora revisadas por tienda
fig_hora = px.bar(h_x_fig, x="Desc_local", y="Cautoriza",color="indicador",text="Cautoriza",
color_discrete_sequence=['rgb(170, 57, 57)','rgb(45, 136, 45)'], title="Cantidad de alertas por hora revisadas por tienda", 
labels={"Desc_local":"Local","Cautoriza":"Cantidad NCs", 'indicador':'Estado'}) 
fig_hora.update_layout(xaxis_categoryorder = 'total descending', legend=dict(yanchor="top", 
y=0.95, xanchor="left", x=0.7))

## Cantidad de alertas por monto revisadas por tienda
fig_monto = px.bar(m_x_fig, x="Desc_local", y="Cautoriza",color="indicador",text="Cautoriza",
color_discrete_sequence=['rgb(170, 57, 57)','rgb(45, 136, 45)'], title="Cantidad de alertas por monto revisadas por tienda", 
labels={"Desc_local":"Local","Cautoriza":"Cantidad NCs", 'indicador':'Estado'}) 
fig_monto.update_layout(xaxis_categoryorder = 'total descending',legend=dict(yanchor="top", 
y=0.95, xanchor="left", x=0.7))

## Estado de revisión
fig_alerta = px.pie(gb_estado_alerta, values='Cautoriza', names='indicador', 
title='Estado de revisión',color_discrete_sequence=['rgb(170, 57, 57)','rgb(45, 136, 45)'])

# ---------- Tabs

tab0_content = dbc.Card(
    dbc.CardBody(
        [
            html.H4(f'Alertas por hora = {hora.shape[0]:,.0f}', className="card-text"), 
            html.H4(f'Alertas por monto = {monto.shape[0]:,.0f}')
        ]
    ),
    className="mt-3",
)

tab1_content = dbc.Card(
    dbc.CardBody(
        [
            html.P("This is tab 1!", className="card-text")
        ]
    ),
    className="mt-3",
)

tab2_content = dbc.Card(
    dbc.CardBody(
        [
            html.P("This is tab 2!", className="card-text")
        ]
    ),
    className="mt-3",
)

tabs = dbc.Tabs(
    [   dbc.Tab(tab0_content, label="Resumen"),
        dbc.Tab(tab1_content, label="Por hora"),
        dbc.Tab(tab2_content, label="Por monto")
    ]
)

# HTML Components

alertas = html.Div([
    html.H3('Alertas NC'), 
    tabs
])

progreso_tiendas = html.Div([
    html.H3('Estado de revisión de alertas por parte de las tiendas'),
    dbc.Row(
        dbc.Col(
            dcc.Graph(
                id='estado_diligenciamiento',
                figure=fig_alerta,
                style={'width': '100vh', 'height': '40vh'}
            )
        )
    ),
    dbc.Row([
        dbc.Col(
            dcc.Graph(
                id='alerta_hora',
                figure=fig_hora
            )
        ), 
        dbc.Col(
            dcc.Graph(
                id='alerta_monto',
                figure=fig_monto
            )

        )]
    )
])

creacion = html.Div(children=[
    dbc.Row(
       [ dbc.Col(html.H3('Creación de notas crédito'), width=5), 
        dbc.Col(
            [dbc.Label("Mes de creación"),
            dcc.Dropdown(
                id="mes-creacion",
                options=[
                    {"label": col, "value": col} for col in con['mes-nc'].unique()
                ],
                value="Feb-22"),
            ], width=7 
        )]
    ),

    dbc.Row(
        [dbc.Col(
            html.Div(
                dcc.Graph(id='ncs_x_mes',figure=fig)
            ), width=5
        ), 
        dbc.Col(
            [
                dcc.Graph(id="ncs_x_local_filtro")
            ], width=7
        )]
    ), 
])

agrupaciones = html.Div([
    dbc.Row(html.H3('Agrupaciones')),
    dbc.Row(html.P('Tipo producto')),
    dbc.Row(
        [
            dbc.Col(html.P('Línea')),
            dbc.Col(html.P('Marca'))
        ]
    )
])

sidebar = html.Div(
    [
        html.H2("Panel NC", className="display-5"),
        html.Hr(),
        html.P(
            "Tiendas Falabella", className="lead"
        ),
        dbc.Nav(
            [
                dbc.NavLink("Alertas", href="/", active="exact"),
                dbc.NavLink("Progreso tiendas", href="/page-2", active="exact"),
                dbc.NavLink("Histórico", href="/page-1", active="exact"),
                dbc.NavLink('Agrupaciones', href='/page-0', active='exact')
            ],
            vertical=True,
            pills=True,
        ),
    ],
    style=SIDEBAR_STYLE,
)

content = html.Div(id="page-content", style=CONTENT_STYLE)

app.layout = html.Div([dcc.Location(id="url"), sidebar, content])

@app.callback(
    Output('ncs_x_local_filtro', 'figure'),
    Input("mes-creacion", 'value')
)
def make_local_filtro_graph(mes):
    filtro_mes = con.loc[con['mes-nc']==mes]
    gb_cant_locales = filtro_mes.groupby(['Desc_local'], sort=False)['Cautoriza'].nunique().reset_index()
    fig_2 = px.bar(gb_cant_locales, orientation='h',y="Desc_local", x="Cautoriza", text='Cautoriza',
    labels={'Cautoriza':'Cantidad de NCS', 'Desc_local':'Local'}, height=700, 
    title='Cantidad de NCs por tienda')
    fig_2.update_yaxes(categoryorder='total ascending')
    return fig_2


@app.callback(Output("page-content", "children"), [Input("url", "pathname")])
def render_page_content(pathname):
    if pathname == "/":
        return alertas
    elif pathname=='/page-0':
        return agrupaciones
    elif pathname == "/page-1":
        return creacion
    elif pathname == "/page-2":
        return progreso_tiendas
    # If the user tries to reach a different page, return a 404 message
    return dbc.Jumbotron(
        [
            html.H1("404: Not found", className="text-danger"),
            html.Hr(),
            html.P(f"The pathname {pathname} was not recognised..."),
        ]
    )


if __name__ == '__main__':
    app.run_server(debug=True)