# Imports
from genericpath import exists
from dash import Dash, html, dcc, Input, Output, State
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
from hplib import hplib as hpl
from PLZtoWeatherRegion import getregion
from gethpfromHeizlast import fitting_hp
from simulate import simulate

# Initialize app with stylsheet and sub-path
app = Dash(__name__,
          suppress_callback_exceptions=True, 
          external_stylesheets=[dbc.themes.BOOTSTRAP],
          url_base_pathname='/PVSYM22/',
          meta_tags=[
          {"name": "viewport", "content": "width=device-width, initial-scale=1"},
          ],
          )
app.title = 'Wärmepumpen Web-Tool'
# Initialize Server
server = app.server

# Prepare data
df = pd.read_pickle('results_summary.pkl')
heatpumps=hpl.load_database()
wp_all=hpl.load_all_heat_pumps()
same_Built=hpl.Same_Built()
heatpumps=heatpumps[['Manufacturer', 'Model', 'Date', 'SPL indoor [dBA]', 'SPL outdoor [dBA]', 'PSB [W]', 'P_th_h_ref [W]','MAPE_P_el', 'MAPE_COP', 'MAPE_P_th',
       'P_th_c_ref [W]', 'MAPE_P_el_cooling', 'MAPE_EER', 'MAPE_Pdc']]
region=['Nordseeküste','Ostseeküste','Nordwestdeutsches Tiefland','Nordostdeutsches Tiefland','Niederrheinisch-westfälische Bucht und Emsland','Nördliche und westliche Mittelgebirge, Randgebiete',
'Nördliche und westliche Mittelgebirge, zentrale Bereiche','Oberharz und Schwarzwald (mittlere Lagen)','Thüringer Becken und Sächsisches Hügelland','Südöstliche Mittelgebirge bis 1000 m',
'Erzgebirge, Böhmer- und Schwarzwald oberhalb 1000 m','Oberrheingraben und unteres Neckartal','Schwäbisch-fränkisches Stufenland und Alpenvorland','Schwäbische Alb und Baar',
'Alpenrand und -täler']
nutzungsgrad_tww=['gebäudezentral EFH (mit Zirkulation)','gebäudezentral MFH (mit Zirkulation)','gebäudezentral (ohne Zirkulation)','wohnungszental']
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
                'Nordostdeutsches Tiefland',
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
            dcc.Slider(0, 12, 0.5,
               value=6,
               marks= {
                    0: '0',
                    1: '1',
                    2: '2',
                    3: '3',   
                    4: '4',
                    5: '5',
                    6: '6',
                    7: '7', 
                    8: '8',
                    9: '9',
                    10: '10',
                    11: '11',
                    12: '12',
               },
               id='einspeisevergütung'
            ),
            ],body=True)

parameter3 = dbc.Card(dbc.CardBody(
            [
            html.H5("Darstellungsart", className="card-title"),
            dcc.Dropdown(
                ['Boxplot', 'Scatterplot', 'Histogramm'],
                'Scatterplot',
                id='plottype')
            ]),body=True)

parameter4 = dbc.Card(dbc.CardBody(
            [
            html.H5("X-Achse", className="card-title"),
            dcc.Dropdown(
                df.columns,
                'Standort',
                id='crossfilter-xaxis-column', 
            ),
            ]),body=True)

parameter5 = dbc.Card(dbc.CardBody(
            [
            html.H5("Y-Achse", className="card-title"),
            dcc.Dropdown(
                df.columns,
                'JAZ',
                id='crossfilter-yaxis-column',
            ),
            ]),body=True)

parameter6 = dbc.Card(dbc.CardBody(
            [
            html.H5("Reihen", className="card-title"),
            dcc.Dropdown(
                df.select_dtypes(include=['object', 'int64' ]).columns,
                'Jahr',
                id='facet-column',
            ),
            ]),body=True)

parameter7 = dbc.Card(dbc.CardBody(
            [
            html.H5("Farbe", className="card-title"),
            dcc.Dropdown(
                df.select_dtypes(include=['object', 'int64' ]).columns,
                'WP-Kategorie',
                id='colour',
            ),
            ]),body=True)

parameter8 = dbc.Card(dbc.CardBody(
            [
            html.H5("Wetter", className="card-title"),
            dcc.Checklist(
                df['Art des Jahres'].unique(),
                ['durchschnittliches Jahr'],
                id='crossfilter-typ',
                inline=True,
            ),
            dcc.Checklist(
                df['Jahr'].unique(),
                [2015],
                id='crossfilter-jahr',
                inline=True,
            ),
            ]),body=True)

parameter9 = dbc.Card(dbc.CardBody(
            [
            html.H5('Gebäudeparameter', className="card-title"),
            dcc.Input(
                placeholder='Wohnort oder PLZ',
                type='text',
                value='',
                id='sim_Standort',            
            ),
            html.Div("entspricht Wetterregion: "),
            dcc.Dropdown(
                region,
                'Nordostdeutsches Tiefland',
                id='sim_region',
            ),
            html.Div('Gebäudeinformationen: '),
            dcc.Input(id='wärmebedarf',type='number',placeholder='Gasbedarf pro Jahr in kWh', step=1000),
            dcc.Input(id='t_heiz',type='number',placeholder='Vorlauftemperatur in °C',min=25, max=70,),
            dcc.Input(id='baujahr',type='number',placeholder='Baujahr/Sanierungsstand',min=1980, max=2030,),
            dcc.Input(id='personen',type='number',placeholder='Personenanzahl',max=200),
            dcc.Dropdown(nutzungsgrad_tww,
            id='eff_tww',placeholder='Art der Trinkwassererwärmung'),
            html.Br(),
            dcc.Markdown(id='heizlast'),
            ]),body=True)

parameter10 = dbc.Card(dbc.CardBody(
            [
            html.H5('Technische Geräte', className="card-title"),
            html.Div('PV-Leistung in kWp: '),
            dcc.Slider(0, 20, 1, value=5, id='sim_pv_kwp'),
            html.Div("PV-Ausrichtung: "),
            dcc.Dropdown(
                df['PV-Ausrichtung'].unique(),
                'Süd',
                id='sim_pv_ausrichtung',
            ),
            ]),body=True)

parameter11 = dbc.Card(dbc.CardBody(
            [
            html.H5('...oder Wärmepumpe suchen', className="card-title"),
            html.Div('Wärmepumpen-Modelname: '),
            
            dcc.Dropdown(wp_all['Model'].unique(),placeholder='Type here to search', id='search_hp'),
            html.Br(),
            html.Button('Zum Simulationsframe hinzufügen',id='add_hp', n_clicks=0),
        
            ]),body=True)

parameter12 = dbc.Card([html.Div(
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
               id='sim_strombezugskosten'
            ),
            html.Div("Einspeisevergütung in Ct/kWh: "),
            dcc.Slider(0, 12, 0.5,
               value=6,
               marks= {0: '0',1: '1',2: '2',3: '3',4: '4',5: '5',6: '6',7: '7', 8: '8',9: '9',10: '10',11: '11',12: '12',},
               id='sim_einspeisevergütung'
            ),
            ],body=True)

button = dbc.Card(dbc.CardBody(
    [
        html.Button('Start Simulation with choosen Data',id='startsim', n_clicks=0),
        html.Br(),
        html.Button('Delete all',id='delete_all', n_clicks=0),
        html.Br(),
        html.Button('Delete last',id='delete_last', n_clicks=0),
    ]))

ergebnis1 = dbc.Card(dbc.CardBody(
        [
            html.H5("Ausgewähltes Gebäude", className="card-title"),
            html.H6(["mit ", html.Span(
                            "10 kWp",
                            id="tooltip-PV",
                            style={"textDecoration": "underline", "cursor": "pointer"},
                        )," PV, ohne Batteriespeicher"], className="card-subtitle"),
                        dbc.Tooltip(
                        "Neigung: 35°",
                        target="tooltip-PV"),
            
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
            html.H6("(vorab auf Balken einer Wärmepumpe klicken)", className="card-subtitle"),
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

ergebnis4 = dbc.Card(
            [
            dcc.Graph(
            id='graph3',
            ),
            ])

ergebnis5 = dbc.Card(dbc.CardBody([
    html.H5('Vorgeschlagene Wärmepumpen', className="card-title"),
    html.Div('Auf einen Balken klicken, um sie dem Simulationsframe hinzuzufügen.'),
    dcc.Graph(
        id='wptochoose',
    )]))

ergebnis6 = dbc.Card(dbc.CardBody([
    dcc.Markdown(
        id='sim_hp',
    )]))

ergebnis7 = dbc.Card(dbc.CardBody([
    dcc.Graph(
        id='economics',
    )]))

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
                        dbc.Col(parameter3, md=4),
                        dbc.Col(parameter4, md=4),
                        dbc.Col(parameter5, md=4),
                        ],
                    align="top",
                    ),
                    dbc.Row(
                        [
                        dbc.Col(parameter6, md=4),
                        dbc.Col(parameter7, md=4),
                        dbc.Col(parameter8, md=4),
                        ],
                    align="top",
                    ),
                    dbc.Row(
                        [
                        dbc.Col(ergebnis4),
                        ],
                    align="top",
                    ),  
                    ],
                    fluid=True,
)

simulieren = dbc.Container(
                    [
                    dbc.Row(
                        [
                        dbc.Col(parameter9, md=12, lg=8),
                        dbc.Col(parameter10, md=12,lg=4)
                        ],
                    align="top",
                    ),
                    dbc.Row(
                        [
                        dbc.Col(ergebnis5,md=8),
                        dbc.Col(parameter11, md=4),
                        ],
                    align='top'
                    ),
                    dbc.Row(
                        [
                        dbc.Col(ergebnis6, md=8),
                        dbc.Col(button, md=4)
                        ],
                    align='center'
                    ),
                    dbc.Row(
                        [
                        dbc.Col(parameter12,md=8),
                        ],
                    align="middle",
                    ), 
                    dbc.Row(
                        [
                        dbc.Col(ergebnis7),
                        ],
                    align='top'
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
                dbc.Tab(label="Stromkosten", tab_id="ergebnisse"),
                dbc.Tab(label="eigene Auswertung", tab_id="auswertungsergebnisse"),
                dbc.Tab(label="eigene Simulation", tab_id="simulieren"),
            ],
            id="tabs",
            active_tab="info",
        ),
        html.Div(id="tab-content", className="p-4"),
        dcc.Store(id='color_graph'),     
        dcc.Store(id='simhp'),
        dcc.Store(id='simresults'),
        dcc.Store(data=0,id='clicks_add_hp')
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
    Output('color_graph','data'),
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
                xaxis_title='Wärmepumpe (klicken für mehr Infos)',
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
    return fig, fig['data'][0]['marker']['color']

@app.callback(
    Output('graph2', 'figure'),
    Input('crossfilter-indicator-scatter', 'clickData'),
    Input('region', 'value'),
    Input('sort2', 'value'),
    Input('sort3', 'value'),
    Input('strombezugskosten', 'value'),
    Input('einspeisevergütung', 'value'),
    Input('color_graph', 'data')
    )
def update_graph2(wp_name,standort, gebäudetyp, pv, strombezugskosten, einspeisevergütung, color_graph):
    df_f = df[(df['Standort'] == region.index(standort)+1)&(df['Gebäudetyp']==gebäudetyp)&(df['Jahr']==2015)&(df['Art des Jahres']=='durchschnittliches Jahr')&(df['Batteriespeicher [kWh]']==0)&(df['PV-Ausrichtung']==pv)]
    df_f['bilanzielle Energiekosten'] = df_f['Netzbezug [kWh]'].values * strombezugskosten/100 - df_f['Netzeinspeisung [kWh]'].values * einspeisevergütung/100
    df_f.loc[df_f['WP-Name']=='Generic','WP-Name']='Generic '+ df_f.loc[df_f['WP-Name']=='Generic','WP-Kategorie'] +' '+ df_f.loc[df_f['WP-Name']=='Generic','WP-Typ']
    
    df_f=df_f.sort_values('bilanzielle Energiekosten')
    wpname=wp_name['points'][0]['hovertext']

    if wp_name['points'][0]['hovertext'].startswith('Generic'):
        if wp_name['points'][0]['hovertext'].endswith('Luft/Wasser einstufig'):
            df_f = df[(df['Standort'] == region.index(standort)+1)&(df['Jahr']==2015)&(df['Gebäudetyp']==gebäudetyp)&(df['PV-Ausrichtung']==pv)&(df['WP-Name']=='Generic')&(df['WP-Kategorie']=='Luft/Wasser')&(df['WP-Typ']=='einstufig')]
        elif wp_name['points'][0]['hovertext'].endswith('Luft/Wasser geregelt'):
            df_f = df[(df['Standort'] == region.index(standort)+1)&(df['Jahr']==2015)&(df['Gebäudetyp']==gebäudetyp)&(df['PV-Ausrichtung']==pv)&(df['WP-Name']=='Generic')&(df['WP-Kategorie']=='Luft/Wasser')&(df['WP-Typ']=='geregelt')]
        elif wp_name['points'][0]['hovertext'].endswith('einstufig'):
            df_f = df[(df['Standort'] == region.index(standort)+1)&(df['Jahr']==2015)&(df['Gebäudetyp']==gebäudetyp)&(df['PV-Ausrichtung']==pv)&(df['WP-Name']=='Generic')&(df['WP-Kategorie']!='Luft/Wasser')&(df['WP-Typ']=='einstufig')]
        elif wp_name['points'][0]['hovertext'].endswith('geregelt'):
            df_f = df[(df['Standort'] == region.index(standort)+1)&(df['Jahr']==2015)&(df['Gebäudetyp']==gebäudetyp)&(df['PV-Ausrichtung']==pv)&(df['WP-Name']=='Generic')&(df['WP-Kategorie']!='Luft/Wasser')&(df['WP-Typ']=='geregelt')]
    else:
        df_f = df[(df['Standort'] == region.index(standort)+1)&(df['Jahr']==2015)&(df['Gebäudetyp']==gebäudetyp)&(df['PV-Ausrichtung']==pv)&(df['WP-Name']==wpname)]
    
    df_f['Kosten [€/a]'] = df_f['Netzbezug [kWh]'].values * strombezugskosten/100 - df_f['Netzeinspeisung [kWh]'].values * einspeisevergütung/100

    fig = px.bar(df_f,
                x='Batteriespeicher [kWh]',
                y='Kosten [€/a]',
                barmode='group',
                color='Art des Jahres',
                height=450
                )
    fig.update_layout(xaxis_title='Batteriespeicher [kWh]',
                yaxis_title='Bilanzielle Stromkosten [€/a]',
                title_x=0
                )
    fig.update_yaxes(range=[df_f['Kosten [€/a]'].min()*0.9,df_f['Kosten [€/a]'].max()*1.05])
    fig.update_xaxes(dtick=1)
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
    if wp_name['points'][0]['curveNumber']==0:
        fig['data'][0]['marker']['color']=color_graph
        if color_graph=='#636efa':
            fig['data'][1]['marker']['color']='#CBCEFF'
            fig['data'][2]['marker']['color']='#0410AE'
        else:
            fig['data'][1]['marker']['color']='#F2C2B9'
            fig['data'][2]['marker']['color']='#AC1B03'
    else:
        if color_graph=='#636efa':
            fig['data'][0]['marker']['color']='#ef553b'
            fig['data'][1]['marker']['color']='#F2C2B9'
            fig['data'][2]['marker']['color']='#AC1B03'
        else:
            fig['data'][0]['marker']['color']='#636efa'
            fig['data'][1]['marker']['color']='#CBCEFF'
            fig['data'][2]['marker']['color']='#0410AE'

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
        hp=hp[['Manufacturer','Modelnamen']].rename(columns={'Manufacturer':'Hersteller &emsp;&emsp;&emsp;&emsp;'})
    except:
        hp=heatpumps.loc[heatpumps['Model']==wpname[0:7]]
        if wp_name['points'][0]['hovertext'].endswith('Luft/Wasser einstufig'):
            name='Luft/Wasser einstufig'
        elif wp_name['points'][0]['hovertext'].endswith('Luft/Wasser geregelt'):
            name='Luft/Wasser geregelt'
        elif wp_name['points'][0]['hovertext'].endswith('einstufig'):
            name='Sole/Wasser einstufig'
        elif wp_name['points'][0]['hovertext'].endswith('geregelt'):
            name='Sole/Wasser geregelt'
        hp['Modelnamen']=name
        hp=hp[['Manufacturer','Modelnamen']].rename(columns={'Manufacturer':'Hersteller &emsp;&emsp;&emsp;&emsp;'}).head(1)
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
    dfff = pd.DataFrame()
    for weathertyp in typ:
        for jahr in year:
            dfff=pd.concat([dfff,df.loc[(df['Jahr'] == jahr)&(df['Art des Jahres']==weathertyp)]])
    if plottype == 'Histogramm':
        fig = px.histogram(x=dfff[xaxis_column_name],
                    hover_name=dfff['WP-Name'],
                    facet_row=dfff[facetcolumn],
                    facet_col_wrap=2,
                    color=dfff[colour],
                    height=400*len(dfff[facetcolumn].unique()),
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
                    height=400*len(dfff[facetcolumn].unique()),
                    facet_row_spacing=0.14/len(dfff[facetcolumn].unique()),
                    points=False, 
            )
        fig.update_yaxes(title=yaxis_column_name)
    elif plottype == 'Scatterplot':
        fig = px.scatter(x=dfff[xaxis_column_name],
                    y=dfff[yaxis_column_name],
                    hover_name=dfff['WP-Name'],
                    facet_row=dfff[facetcolumn],
                    facet_col_wrap=2,
                    color=dfff[colour],
                    height=400*len(dfff[facetcolumn].unique()),
                    facet_row_spacing=0.14/len(dfff[facetcolumn].unique()), 
            )
        fig.update_yaxes(title=yaxis_column_name)
    fig.update_traces(customdata=dfff['WP-Name'])
    fig.update_xaxes(title=xaxis_column_name)
    fig.update_layout(legend=dict(
    yanchor="top",
    y=0.99,
    xanchor="right",
    x=0.99,
    ))
    fig.update_layout(margin=dict(
        t=15,
        r=0,
        b=0,
        l=0,
    ),)
    return fig

@app.callback(
    Output('sim_region', 'value'),
    Input('sim_Standort', 'value'))
def standorttoregion(standort):
    return region[getregion(standort)-1]

@app.callback(
    Output('wptochoose','figure'),
    Output('heizlast','children'),
    Input('sim_region','value'),
    Input('wärmebedarf','value'),
    Input('t_heiz','value'),
    Input('baujahr','value'),
    Input('personen','value'),
    Input('eff_tww','value'),
)
def clickbutton(sim_region,wärmebedarf,t_heiz,baujahr,personen,eff_tww):
    hp,Heizlast, T_min=fitting_hp(wärmebedarf,region.index(sim_region)+1,t_heiz,baujahr,personen,[0.4,0.6,0.7,0.85][nutzungsgrad_tww.index(eff_tww)])
    fig = px.bar(hp, x='Model',y='COP', color='WP-Kategorie', hover_data=hp.columns)
    fig.layout.xaxis.update(showticklabels=False)
    fig.update_layout(legend=dict(yanchor="top",y=0.99,xanchor="right",x=0.99,))
    fig.update_layout(yaxis_title='Arbeitszahl im Arbeitspunkt (' + str(T_min)+'/'+str(t_heiz)+')',xaxis_title='Wärmepumpe (klicken um dem Simulationsframe hinzuzufügen)',title_x=0)
    return fig, 'Dies entspricht einer berechneten Wärmepumpe mit einer Leitstung von mindestens '+str(round(Heizlast))+' Watt'

@app.callback(
    Output("simhp", "value"),
    Output('clicks_add_hp','value'),
    Input("wptochoose", "clickData"),
    State('sim_region','value'),
    State('wärmebedarf','value'),
    State('t_heiz','value'),
    State('baujahr','value'),
    State('personen','value'),
    State('eff_tww','value'),
    State('sim_pv_kwp','value'),
    State('sim_pv_ausrichtung','value'),
    State('simhp','value'),
    Input("add_hp", "n_clicks"),
    State('search_hp','value'),
    State('clicks_add_hp','value'),
)
def simulatehp(heatpumps,sim_region,wärmebedarf,t_heiz,baujahr,personen,eff_tww,pv_kwp,pv_ausrichtung,df,n_clicks,search_hp,n_clicks_before):
    try: # for button click
        if (n_clicks>n_clicks_before):
            heatpump=same_Built.all_to_database(search_hp)
            heatpumps=dict({'points': [{'x': heatpump}]})      
    except: # if the first hp is on button click
        if (n_clicks>0):
            heatpump=same_Built.all_to_database(search_hp)
            heatpumps=dict({'points': [{'x': heatpump}]})
    model=(heatpumps['points'][0]['x']).replace('/','')
    if exists('src/simulation_data/simulations/'+str(region.index(sim_region)+1)+'_'+str(wärmebedarf)+'_'+str(t_heiz)+'_'+str(personen)+'_'+str([0.4,0.6,0.7,0.85][nutzungsgrad_tww.index(eff_tww)])+'_'+str(baujahr)+'_'+model+'_'+str(pv_kwp)+'_'+pv_ausrichtung+'.csv'):
        sim='Ja'
    else:
        sim='Nein'
    try:
        df=pd.DataFrame.from_dict(df)
        if (len(df)>=10):
            df=pd.DataFrame()
        simhp_value=pd.concat([df, pd.DataFrame({'Region':[region.index(sim_region)+1],'Wärmebedarf':[wärmebedarf],'Vorlauf':[t_heiz],'Personen':[personen],'Nutzungsgrad_TWW':[eff_tww],'Baujahr':[baujahr],'Models':[heatpumps['points'][0]['x']], 'kWp':[pv_kwp],'PV-Ausrichtung':[pv_ausrichtung],'Bereits simuliert':[sim]})])
    except:
        simhp_value=pd.DataFrame({'Region':[region.index(sim_region)+1],'Wärmebedarf':[wärmebedarf],'Vorlauf':[t_heiz],'Personen':[personen],'Nutzungsgrad_TWW':[eff_tww],'Baujahr':[baujahr],'Models':[heatpumps['points'][0]['x']], 'kWp':[pv_kwp],'PV-Ausrichtung':[pv_ausrichtung],'Bereits simuliert':[sim]})

    return simhp_value.to_dict(orient='list'),n_clicks

@app.callback(
    Output('sim_hp', 'children'),
    Input('simhp','value')
)
def showsimhp(simhp):
    return(pd.DataFrame.from_dict(simhp).to_markdown())

@app.callback(
    Output('simresults','value'),
    Input('startsim', 'n_clicks'),
    State('simhp', 'value')
)
def cleardata(click,para):
    del para['Bereits simuliert']
    para_dict=para
    para=pd.DataFrame.from_dict(para)
    results_summary=pd.DataFrame()
    
    for simulation in para.index:
        eff_tww=[0.4,0.6,0.7,0.85][nutzungsgrad_tww.index(para.iloc[simulation,4])]
        path='src/simulation_data/simulations/'
        for element in para_dict:
            if element=='Nutzungsgrad_TWW':
                path=path+str(eff_tww)+'_'
            else:
                if element=='Models':
                    path=path+(para_dict[element][simulation].replace('/',''))+'_'
                else:
                    path=path+(str(para_dict[element][simulation]))+'_'
        path=path[:-1]+'.csv'
        if exists(path):
            results_summary=pd.concat([results_summary,pd.read_csv(path)])
        else:
            results_summary=pd.concat([results_summary,simulate(para.iloc[simulation,0],para.iloc[simulation,1],para.iloc[simulation,2],para.iloc[simulation,3],eff_tww,para.iloc[simulation,5],para.iloc[simulation,6],para.iloc[simulation,7],para.iloc[simulation,8])])
    return(results_summary.to_dict(orient='list'))

"""@app.callback(
    Output('simhp', 'value'),
    Input('delete_last','n_clicks')
    State('simhp', 'value')
)
def delete_last(clicks, simhp):
    simhp=pd.DataFrame.from_dict(simhp)
    return pd.DataFrame().to_dict(orient='list')"""

@app.callback(
    Output('economics','figure'),
    Input('simresults','value'),
    Input('sim_strombezugskosten', 'value'),
    Input('sim_einspeisevergütung','value')
)
def calceconomics(results_summary,strombezugskosten,einspeisevergütung):
    results_summary=pd.DataFrame.from_dict(results_summary)
    results_summary['bilanzielle Stromkosten'] = results_summary['E_gs'].values * strombezugskosten/100 - results_summary['E_gf'].values * einspeisevergütung/100
    fig=px.line(results_summary, x='E_bat', y='bilanzielle Stromkosten', color='WP-Name', hover_data=['WP-Laufzeit','WP-Typ'])
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
        elif active_tab=='simulieren':
            return simulieren
    return "No tab selected"
#############################################

if __name__ == '__main__':
    app.run_server(debug=False)