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
df = pd.read_pickle('results_summary_new.pkl')
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

    [Download](https://re-lab.hs-emden-leer.de/s/S4wazTQdDELPJPi/download) des Ergebnis-Datensatz als CSV Datei (CC-BY-4.0)
    
''',
    link_target="_blank",
)

Überschrift_Ergebnis1 = dbc.Card(dcc.Markdown('''
    >
    > **Ergebnisse für ein EFH mit 10 kWp, ohne Batteriespeicher** 
    >
'''))

Überschrift_Ergebnis2 = dbc.Card(dcc.Markdown(
'''
    >
    > **Reduktion in Abhängigkeit eines Batteriespeichers** 
    > (bitte auf den Balken einer bestimmten Wärmepumpe klicken)
    >
'''))

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
                id='region',
            ),
            html.Div("Gebäudetyp: "),
            dcc.Dropdown(
                df['Gebäudetyp'].unique(),
                'Neubau (150 Qm und 0.6 W/(K*Qm))',
                id='sort2',
            ),
            html.Div("PV-Ausrichtung: "),
            dcc.Dropdown(
                df['PV-Ausrichtung'].unique(),
                'Süd',
                id='sort3',
            ),
            ],body=True)

parameter2 = dbc.Card([
            dcc.Markdown('''
            Ökonomische Parameter zur Bestimmung der bilanziellen Stromkosten
            '''),
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

ergebnis1 = dbc.Card([
            dcc.Graph(
            id='crossfilter-indicator-scatter',
            hoverData={'points': [{'curveNumber': 0,'x':'geregelt','hovertext': 'Generic Luft/Wasser geregelt'}]},
            clickData={'points': [{'curveNumber': 0,'x':'geregelt','hovertext': 'Generic Luft/Wasser geregelt'}]}
            ),
            ])

ergebnis2 = dbc.Card([
            dcc.Graph(
            id='graph2',
            hoverData={'points': [{'curveNumber': 0,'x':'geregelt','hovertext': 'Generic Luft/Wasser geregelt'}]},
            clickData={'points': [{'curveNumber': 0,'x':'geregelt','hovertext': 'Generic Luft/Wasser geregelt'}]}
            ),
            ])

ergebnis3 = [
            dcc.Markdown(
            id='wp-infos'
            ),
            ]

ergebnisse = dbc.Container(
                    [
                    dbc.Row(
                        [
                        dbc.Col(parameter1, md=6),
                        dbc.Col(parameter2, md=6),
                        ],
                    align="center",
                    ),
                    dbc.Row(
                        [
                        dbc.Col(Überschrift_Ergebnis1, md=12),
                        ],
                    align="center",
                    ),
                    dbc.Row(
                        [
                        dbc.Col(ergebnis1, md=12),
                        ],
                    align="center",
                    ),
                    dbc.Row(
                        [
                        dbc.Col(Überschrift_Ergebnis2, md=12),
                        ],
                    align="center",
                    ),
                    dbc.Row(
                        [
                        dbc.Col(ergebnis2, md=12),
                        ],
                    align="center",
                    ),
                    dbc.Row(
                        [
                        dbc.Col(Überschrift_Ergebnis3, md=12),
                        ],
                    align="center",
                    ),
                    dbc.Row(
                        [
                        dbc.Col(ergebnis3),
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
            ],
            id="tabs",
            active_tab="info",
        ),
        html.Div(id="tab-content", className="p-4"),
    ]
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
    dff = df[(df['Standort'] == region.index(standort)+1)&(df['Gebäudetyp']==gebäudetyp)&(df['Jahr']==2015)&(df['Typ']=='durchschnittliches Jahr')&(df['Batteriespeicher [kWh]']==0)&(df['PV-Ausrichtung']==pv)]
    dff['bilanzielle Energiekosten'] = dff['Netzbezug [kWh]'].values * strombezugskosten/100 - dff['Netzeinspeisung [kWh]'].values * einspeisevergütung/100
    dff.loc[dff['WP-Name']=='Generic','WP-Name']='Generic '+ dff.loc[dff['WP-Name']=='Generic','WP-Kategorie'] +' '+ dff.loc[dff['WP-Name']=='Generic','WP-Typ']
    
    dff=dff.sort_values('bilanzielle Energiekosten')
    fig=px.bar(data_frame=dff,
                    y='WP-Name',                    
                    x='bilanzielle Energiekosten',
                    hover_name='WP-Name',
                    hover_data=['WP-Hersteller'],
                    color='WP-Kategorie',
                    labels=dict(x='Bilanzielle Stromkosten [€/a]',y='WP-Models',color='WP-Kategorie'),
                    height=600
            ).update_yaxes(categoryorder='total descending')
    fig.update_layout(legend=dict(
    orientation="h",
    yanchor="middle",
    y=-0.1,
    x=0.5,
    xanchor="center"
    ))
    fig.update_xaxes(range=[dff['bilanzielle Energiekosten'].min()*0.9,dff['bilanzielle Energiekosten'].max()*1.05])
    fig.update_layout(xaxis_title='Bilanzielle Stromkosten [€/a]',
                xaxis={'side': 'top'},
                yaxis_title='WP-Model')
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
                title='Modell: '+wpname, 
                x='Batteriespeicher [kWh]',
                y='Kosten [1/Jahr]',
                barmode='group',
                color='Typ',
                height=600
                )
    fig.update_layout(xaxis_title='Batteriespeicher [kWh]',
                yaxis_title='Bilanzielle Stromkosten [€/a]',
                title_x=0.5
                )
    fig.update_yaxes(range=[dff['Kosten [1/Jahr]'].min()*0.9,dff['Kosten [1/Jahr]'].max()*1.05])
    fig.update_layout(legend=dict(
    orientation="h",
    yanchor="middle",
    y=-0.2,
    x=0.5,
    xanchor="center"
    ))
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
        hp=hp[['Manufacturer','Modelnamen', 'MAPE_COP']].rename(columns={'Manufacturer':'Hersteller','MAPE_COP':'MAPE'})
    except:
        pass
    return hp.to_markdown()

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
    return "No tab selected"
#############################################

if __name__ == '__main__':
    app.run_server(debug=False)