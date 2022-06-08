# Imports
from dash import Dash, html, dcc, Input, Output
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
from hplib import hplib as hpl
import plotly.graph_objects as go
from PLZtoWeatherRegion import getregion

# Initialize app with stylsheet and sub-path
app = Dash(__name__,
          suppress_callback_exceptions=True, 
          external_stylesheets=[dbc.themes.BOOTSTRAP],
          url_base_pathname='/PVSYM22/',
          meta_tags=[
          {"name": "viewport", "content": "width=device-width, initial-scale=1"},
          ],
          )

# Initialize Server
server = app.server

# Prepare data
df = pd.read_pickle('results_summary.pkl')
heatpumps=hpl.load_database()
heatpumps=heatpumps[['Manufacturer', 'Model', 'Date', 'SPL indoor [dBA]', 'SPL outdoor [dBA]', 'PSB [W]', 'P_th_h_ref [W]','MAPE_P_el', 'MAPE_COP', 'MAPE_P_th',
       'P_th_c_ref [W]', 'MAPE_P_el_cooling', 'MAPE_EER', 'MAPE_Pdc']]
region=['Nordseeküste','Ostseeküste','Nordwestdeutsches Tiefland','Nordostdeutsches Tiefland','Niederrheinisch-westfälische Bucht und Emsland','Nördliche und westliche Mittelgebirge, Randgebiete',
'Nördliche und westliche Mittelgebirge, zentrale Bereiche','Oberharz und Schwarzwald (mittlere Lagen)','Thüringer Becken und Sächsisches Hügelland','Südöstliche Mittelgebirge bis 1000 m',
'Erzgebirge, Böhmer- und Schwarzwald oberhalb 1000 m','Oberrheingraben und unteres Neckartal','Schwäbisch-fränkisches Stufenland und Alpenvorland','Schwäbische Alb und Baar',
'Alpenrand und -täler']

# Texte definieren ################
Intro1 = dcc.Markdown('''
    **Veröffentlichung:** 
    
    Einfluss konkreter Wärmepumpen-Typen auf die
    Wirtschaftlichkeit und Netzverträglichkeit von
    PV-Wärme-Systemen in Wohngebäuden
''')
Intro2 = dcc.Markdown('''
    **Autoren:** 
    
    Tjarko Tjaden, Hauke Hoops, Johannes Rolink

    **Konferenz:** 
    
    37. PV-Symposium, 21.-23. Juni 2022
''')
Intro3 = dcc.Markdown('''
    [Download](https://re-lab.hs-emden-leer.de/s/ef42jE6cMcMzNR7/download) der Veröffentlichung zur Erläuterung der Ergebnisse.

    [Download](https://re-lab.hs-emden-leer.de/s/LgMXA3FkTxEr7Py/download) des Ergebnis-Datensatz als CSV Datei (CC-BY-4.0)
    
''',
    link_target="_blank",
)

Überschrift_Ergebnis3 = dbc.Card(dcc.Markdown(
'''
    >
    > **Weitere Informationen** zur gewählten Wärmepumpe, u.a.:
    > 
    > * Hersteller
    > * weitere Modellnahmen, falls OEM-Produkt
    > * MAPE = mittlerer prozentualer Fehler des Modells im Vergleich zu Messdaten
    >
'''))
Überschrift_Auswertung = dbc.Card(dcc.Markdown(
'''
    >
    > **Graphische Darstellung der Simulationsergebnisse**
    > 
    > Mit Auswahl der Parameter für die 
    > * X-Achse
    > * Y-Achse
    > * Farbe
    > * Darstellungsart
'''))
###################################

# Inhalte definieren ##############
info = dbc.Container(
                    [
                    dbc.Row(
                        [
                        dbc.Col(Intro1, md=6),
                        dbc.Col(Intro2, md=6),
                        ],
                    align="top",
                    ),
                    dbc.Row(
                        [
                        dbc.Col(Intro3, md=12),
                        ],
                    align="top",
                    ),
                    ],
                    fluid=True,
                    )

parameter1 = dbc.Card([
            dcc.Input(
                placeholder='Wohnort oder PLZ',
                type='text',
                value='',
                id='Standort',            
            ),
            html.Div("entspricht Wetterregion: "),
            dcc.Dropdown(
                region,
                id='region',
            ),
            html.Div("Gebäudetyp: "),
            dcc.Dropdown(
                df['Gebäudetyp'].unique(),
                'Neubau (35/28)',
                id='sort2',
            ),
            html.Div("PV-Ausrichtung: "),
            dcc.Dropdown(
                df['PV-Ausrichtung'].unique(),
                'Süd',
                id='sort3',
            ),
            ],body=True, outline=True)

parameter2 = dbc.Card([html.Div(
            [
                html.P(
                    [
                        "Ökonomische Parameter zur Bestimmung der ",
                        html.Span(
                            "bilanziellen Stromkosten",
                            id="tooltip-stromkosten",
                            style={"textDecoration": "underline", "cursor": "pointer"},
                        ),
                        ".",
                    ]
                ),
                dbc.Tooltip(
                    "Summe aus Strombezugskosten für das gesamte Gebäude abzüglich "
                    "der Einspeisevergütung.",
                    target="tooltip-stromkosten",
                ),
            ]
            ),
            html.Div("Strombezugskosten in Ct/kWh: "),
            dcc.Slider(28, 40, 1,
               value=35,
               id='strombezugskosten'
            ),
            html.Div("Einspeisevergütung in Ct/kWh: "),
            dcc.Slider(0, 12, 1,
               value=6,
               id='einspeisevergütung'
            ),
            ],body=True)

parameter3 = dbc.Card([
            dcc.Markdown("Darstellungsart: "),
            dcc.Dropdown(
                ['Boxplot', 'Scatterplot', 'Histogramm'],
                'Scatterplot',
                id='plottype')
],body=True)

parameter4 = dbc.Card([
            dcc.Markdown("X-Achse: "),
            dcc.Dropdown(
                df.columns,
                'Standort',
                id='crossfilter-xaxis-column',
                
            ),
            dcc.Markdown("Wetterjahr: "),
            dcc.Checklist(
                df['Jahr'].unique(),
                [2015],
                id='crossfilter-jahr',
                inline=True,
            ),
            dcc.Markdown("Reihen: "),
            dcc.Dropdown(
                df.select_dtypes(include=['object', 'int64' ]).columns,
                'Gebäudetyp',
                id='facet-column',
            ),
            ],body=True)

parameter5=dbc.Card([
            dcc.Markdown("Y-Achse: "),
            dcc.Dropdown(
                df.columns,
                'JAZ',
                id='crossfilter-yaxis-column',
            ),
            dcc.Markdown("Wetterverhältnisse: "),
            dcc.Checklist(
                df['Art des Jahres'].unique(),
                ['durchschnittliches Jahr'],
                id='crossfilter-typ',
                inline=True,
            ),
            dcc.Markdown("Farbe: "),
            dcc.Dropdown(
                df.select_dtypes(include=['object', 'int64' ]).columns,
                'WP-Kategorie',
                id='colour',
            ),
            ],body=True)

ergebnis1 = dbc.Card(dbc.CardBody(
        [
            html.H5("Ausgewähltes Gebäude", className="card-title"),
            html.H6("mit 10 kWp PV, ohne Batteriespeicher", className="card-subtitle"),
            dcc.Graph(
            id='crossfilter-indicator-scatter',
            hoverData={'points': [{'curveNumber': 0,'x':'geregelt','hovertext': 'Generic Luft/Wasser geregelt'}]},
            clickData={'points': [{'curveNumber': 0,'x':'geregelt','hovertext': 'Generic Luft/Wasser geregelt'}]},
            config={
            'displayModeBar': False
            }
            ),
            ]))

ergebnis2 = dbc.Card(dbc.CardBody(
        [
            html.H5("Einfluss eines Batteriespeichers", className="card-title"),
            html.H6("(vorab auf Wärmepumpe klicken)", className="card-subtitle"),
            dcc.Graph(
            id='graph2',
            hoverData={'points': [{'curveNumber': 0,'x':'geregelt','hovertext': 'Generic Luft/Wasser geregelt'}]},
            clickData={'points': [{'curveNumber': 0,'x':'geregelt','hovertext': 'Generic Luft/Wasser geregelt'}]},
            config={
            'displayModeBar': False
            }
            ),
            ]))

ergebnis3 = dbc.Card(dbc.CardBody(
        [
            html.H5("Weitere Informationen zur gewählten Wärmepumpe", className="card-title"),
            dcc.Markdown(
            id='wp-infos'
            ),
            ]))

ergebnis4 = dbc.Card([
            dcc.Graph(
            id='graph3',
            ),
            ])

ergebnisse =        [
                    dbc.Row(
                        [
                        dbc.Col(parameter1, md=6),
                        dbc.Col(parameter2, md=6),
                        ],
                    align="top",
                    ),
                    dbc.Row(
                        [
                        dbc.Col(ergebnis1, md=6),
                        dbc.Col(ergebnis2, md=6)
                        ],
                    align="top",
                    ),
                    dbc.Row(
                        [
                        dbc.Col(ergebnis3),
                        ],
                    align="center",
                    ),
                    ]
                    
auswertungsergebnisse=dbc.Container(
                    [
                    dbc.Row(
                        [
                        dbc.Col(Überschrift_Auswertung, md=12),
                        ],
                    align="center",
                    ),
                    dbc.Row(
                        [
                        dbc.Col(parameter3, md=6),
                        ],
                    align="center",
                    ),
                    dbc.Row(
                        [
                        dbc.Col(parameter4, md=6),
                        dbc.Col(parameter5, md=6),
                        ],
                    align="center",
                    ),
                    dbc.Row(
                        [
                        dbc.Col(ergebnis4),
                        ],
                    align="center",
                    ),  
                    ],
                    fluid=True,
)
###################################

# Layout ##########################
app.layout = dbc.Container(
    [
        html.H1("Wärmepumpen Web-Tool"),
        html.Hr(),
        dbc.Tabs(
            [
                dbc.Tab(label="Info", tab_id="info"),
                dbc.Tab(label="Ergebnisse", tab_id="ergebnisse"),
                dbc.Tab(label="Auswertungsergebnisse", tab_id="auswertungsergebnisse")
            ],
            id="tabs",
            active_tab="info",
        ),
        html.Div(id="tab-content", className="p-4"),
    ],fluid=True
)

# Callbacks und Definitions ######################
@app.callback(
    Output('region', 'value'),
    Input('Standort', 'value'))
def standorttoregion(standort):
    return region[getregion(standort)-1]

@app.callback(
    Output('crossfilter-indicator-scatter', 'figure'),
    Input('region', 'value'),
    Input('sort2', 'value'),
    Input('sort3', 'value'),
    Input('strombezugskosten', 'value'),
    Input('einspeisevergütung', 'value'),
    )
def update_graph(standort, gebäudetyp,pv,strombezugskosten, einspeisevergütung):
    dff = df[(df['Standort'] == region.index(standort)+1)&(df['Gebäudetyp']==gebäudetyp)&(df['Jahr']==2015)&(df['Art des Jahres']=='durchschnittliches Jahr')&(df['Batteriespeicher [kWh]']==0)&(df['PV-Ausrichtung']==pv)]
    dff['bilanzielle Energiekosten'] = dff['Netzbezug [kWh]'].values * strombezugskosten/100 - dff['Netzeinspeisung [kWh]'].values * einspeisevergütung/100
    dff.loc[dff['WP-Name']=='Generic','WP-Name']='Generic '+ dff.loc[dff['WP-Name']=='Generic','WP-Kategorie'] +' '+ dff.loc[dff['WP-Name']=='Generic','WP-Typ']
    
    dff=dff.sort_values('bilanzielle Energiekosten')
    fig=px.bar(data_frame=dff,
                    y='bilanzielle Energiekosten',                    
                    x='WP-Name',
                    hover_name='WP-Name',
                    hover_data=['WP-Hersteller'],
                    color='WP-Kategorie',
                    labels=dict(y='Bilanzielle Stromkosten [€/a]',x='Wärmepumpe',color='WP-Kategorie'),
                    height=450,
            ).update_xaxes(categoryorder='total ascending')
    fig.layout.xaxis.update(showticklabels=False)
    fig.update_layout(legend=dict(
    yanchor="top",
    y=0.99,
    xanchor="right",
    x=0.99,
    ))
    fig.update_yaxes(range=[dff['bilanzielle Energiekosten'].min()*0.9,dff['bilanzielle Energiekosten'].max()*1.05])
    fig.update_layout(yaxis_title='Bilanzielle Stromkosten [€/a]',
                xaxis_title='Wärmepumpe (auswählen für mehr Infos)',
                title_x=0)
    fig.update_layout(legend={'title_text':''})
    fig.update_layout(margin=dict(
        t=15,
        r=0,
        b=0,
        l=0,
    ),)
    if fig['data'][0]['legendgroup']=='Sole/Wasser':
        fig['data'][0]['marker']['color']='#636efa'
        fig['data'][1]['marker']['color']='#EF553B'
    else:
        fig['data'][1]['marker']['color']='#636efa'
        fig['data'][0]['marker']['color']='#EF553B'
    return fig

@app.callback(
    Output('graph2', 'figure'),
    Input('crossfilter-indicator-scatter', 'clickData'),
    Input('region', 'value'),
    Input('sort2', 'value'),
    Input('sort3', 'value'),
    Input('strombezugskosten', 'value'),
    Input('einspeisevergütung', 'value'),
    )
def update_graph2(wp_name,standort, gebäudetyp, pv, strombezugskosten, einspeisevergütung):
    wpname=wp_name['points'][0]['hovertext']

    if wp_name['points'][0]['hovertext'].startswith('Generic'):
        if wp_name['points'][0]['hovertext'].endswith('Luft/Wasser einstufig'):
            dff = df[(df['Standort'] == region.index(standort)+1)&(df['Jahr']==2015)&(df['Gebäudetyp']==gebäudetyp)&(df['PV-Ausrichtung']==pv)&(df['WP-Name']=='Generic')&(df['WP-Kategorie']=='Luft/Wasser')&(df['WP-Typ']=='einstufig')]
        elif wp_name['points'][0]['hovertext'].endswith('Luft/Wasser geregelt'):
            dff = df[(df['Standort'] == region.index(standort)+1)&(df['Jahr']==2015)&(df['Gebäudetyp']==gebäudetyp)&(df['PV-Ausrichtung']==pv)&(df['WP-Name']=='Generic')&(df['WP-Kategorie']=='Luft/Wasser')&(df['WP-Typ']=='geregelt')]
        elif wp_name['points'][0]['hovertext'].endswith('einstufig'):
            dff = df[(df['Standort'] == region.index(standort)+1)&(df['Jahr']==2015)&(df['Gebäudetyp']==gebäudetyp)&(df['PV-Ausrichtung']==pv)&(df['WP-Name']=='Generic')&(df['WP-Kategorie']!='Luft/Wasser')&(df['WP-Typ']=='einstufig')]
        elif wp_name['points'][0]['hovertext'].endswith('geregelt'):
            dff = df[(df['Standort'] == region.index(standort)+1)&(df['Jahr']==2015)&(df['Gebäudetyp']==gebäudetyp)&(df['PV-Ausrichtung']==pv)&(df['WP-Name']=='Generic')&(df['WP-Kategorie']!='Luft/Wasser')&(df['WP-Typ']=='geregelt')]
    else:
        dff = df[(df['Standort'] == region.index(standort)+1)&(df['Jahr']==2015)&(df['Gebäudetyp']==gebäudetyp)&(df['PV-Ausrichtung']==pv)&(df['WP-Name']==wpname)]
    
    dff['Kosten [1/Jahr]'] = dff['Netzbezug [kWh]'].values * strombezugskosten/100 - dff['Netzeinspeisung [kWh]'].values * einspeisevergütung/100

    fig = px.bar(dff,
                x='Batteriespeicher [kWh]',
                y='Kosten [1/Jahr]',
                barmode='group',
                color='Art des Jahres',
                height=450
                )
    fig.update_layout(xaxis_title='Batteriespeicher [kWh]',
                yaxis_title='Bilanzielle Stromkosten [€/a]',
                title_x=0
                )
    fig.update_yaxes(range=[dff['Kosten [1/Jahr]'].min()*0.9,dff['Kosten [1/Jahr]'].max()*1.05])
    fig.update_layout(legend=dict(
    yanchor="top",
    y=0.99,
    xanchor="right",
    x=0.99
    )
    )
    fig.update_layout(legend={'title_text':''})
    fig.update_layout(margin=dict(
        t=15,
        r=0,
        b=0,
        l=0,
    ),)
    return fig

@app.callback(
    Output('wp-infos', 'children'),
    Input('crossfilter-indicator-scatter', 'clickData'),
    Input('graph2', 'clickData'))
def update_table(wp_name, Wp_name):
    wpname=wp_name['points'][0]['hovertext']
    hp=heatpumps.loc[heatpumps['Model']==wpname]
    try:
        samehp=''
        for i in hpl.same_built_type(wpname):
            samehp=samehp+i+' \n'
        samehp=samehp[:-2]
        samehp
        hp['Modelnamen']=samehp
        hp=hp[['Manufacturer','Modelnamen']].rename(columns={'Manufacturer':'Hersteller'})
    except:
        pass
    return hp.to_markdown(index=False)

@app.callback(
    Output('graph3', 'figure'),
    Input('crossfilter-xaxis-column', 'value'),
    Input('crossfilter-yaxis-column', 'value'),
    Input('crossfilter-jahr', 'value'),
    Input('crossfilter-typ', 'value'),
    Input('facet-column', 'value'),
    Input('colour', 'value'),
    Input('plottype', "value"),
    )
def update_graph(xaxis_column_name, yaxis_column_name,
                year, typ,facetcolumn,colour,plottype):
    print(year)
    dfff = pd.DataFrame()
    for weathertyp in typ:
        for jahr in year:
            dfff=pd.concat([dfff,df.loc[(df['Jahr'] == jahr)&(df['Art des Jahres']==weathertyp)]])
    print(dfff)
    if plottype == 'Histogramm':
        fig = px.histogram(x=dfff[xaxis_column_name],
                    hover_name=dfff['WP-Name'],
                    facet_row=dfff[facetcolumn],
                    facet_col_wrap=2,
                    color=dfff[colour],
                    height=300*len(dfff[facetcolumn].unique()),
                    facet_row_spacing=0.14/len(dfff[facetcolumn].unique()), 
                    barmode="overlay",
            )
    elif plottype == 'Boxplot':
        fig = px.box(x=dfff[xaxis_column_name],
                    y=dfff[yaxis_column_name],
                    hover_name=dfff['WP-Name'],
                    facet_row=dfff[facetcolumn],
                    facet_col_wrap=2,
                    color=dfff[colour],
                    height=300*len(dfff[facetcolumn].unique()),
                    facet_row_spacing=0.14/len(dfff[facetcolumn].unique()), 
            )
        fig.update_yaxes(title=yaxis_column_name)
    elif plottype == 'Scatterplot':
        fig = px.scatter(x=dfff[xaxis_column_name],
                    y=dfff[yaxis_column_name],
                    hover_name=dfff['WP-Name'],
                    facet_row=dfff[facetcolumn],
                    facet_col_wrap=2,
                    color=dfff[colour],
                    height=300*len(dfff[facetcolumn].unique()),
                    facet_row_spacing=0.14/len(dfff[facetcolumn].unique()), 
            )
        fig.update_yaxes(title=yaxis_column_name)
    fig.update_traces(customdata=dfff['WP-Name'])
    fig.update_xaxes(title=xaxis_column_name)
    return fig

@app.callback(
    Output("tab-content", "children"),
    [Input("tabs", "active_tab")],
)
def render_tab_content(active_tab):
    """
    This callback takes the 'active_tab' property as input, as well as the
    stored graphs, and renders the tab content depending on what the value of
    'active_tab' is.
    """
    if active_tab is not None:
        if active_tab == "info":
            return info
        elif active_tab == "ergebnisse":
            return ergebnisse
        elif active_tab=="auswertungsergebnisse":
            return auswertungsergebnisse
    return "No tab selected"
#############################################

if __name__ == '__main__':
    app.run_server(debug=True)