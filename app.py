# Imports
from dash import Dash, html, dcc, Input, Output
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
from hplib import hplib as hpl
import plotly.graph_objects as go
from PLZtoWeatherRegion import getregion
from gethpfromHeizlast import fitting_hp

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
            dcc.Input(id='wärmebedarf',type='number',placeholder='Wärmebedarf pro Jahr in kWh'),
            dcc.Input(id='t_heiz',type='number',placeholder='Vorlauftemperatur in °C',),
            dcc.Input(id='baujahr',type='number',placeholder='Baujahr',),
            dcc.Input(id='personen',type='number',placeholder='Personenanzahl',),
            dcc.Dropdown(nutzungsgrad_tww,
            id='eff_tww',placeholder='Art der Trinkwassererwärmung'),
            html.Br(),
            ]),body=True)

parameter10= dbc.Card(dbc.CardBody(
            [
            html.H5('Gebäudeparameter', className="card-title"),
            html.Div('PV-Leistung in kWp: '),
            dcc.Slider(0, 20, 1, value=5),
            html.Div("PV-Ausrichtung: "),
            dcc.Dropdown(
                df['PV-Ausrichtung'].unique(),
                'Süd',
                id='sim_kwp',
            ),]),body=True)

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

ergebnis4 = dbc.Card([
            dcc.Graph(
            id='graph3',
            ),
            ])

ergebnis5 = dbc.Card(dbc.CardBody([
    dcc.Graph(
        id='wptochoose',
    )
]))

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
                        dbc.Col(parameter9, md=12),
                        ],
                    align="top",
                    ),
                    dbc.Row(
                        [
                        dbc.Col(ergebnis5),
                        ],
                    align='top'
                    )
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
        dcc.Store(id='color_graph')
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
    Input('sim_region','value'),
    Input('wärmebedarf','value'),
    Input('t_heiz','value'),
    Input('baujahr','value'),
    Input('personen','value'),
    Input('eff_tww','value'),
)
def clickbutton(sim_region,wärmebedarf,t_heiz,baujahr,personen,eff_tww):
    [0.3,0.45,0.6,0.775][nutzungsgrad_tww.index(eff_tww)]
    hp,Heizlast=fitting_hp(wärmebedarf,region.index(sim_region)+1,t_heiz,baujahr,personen,[0.3,0.45,0.6,0.775][nutzungsgrad_tww.index(eff_tww)])
    fig = px.bar(hp, x='Model',y='COP', color='WP-Kategorie')
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