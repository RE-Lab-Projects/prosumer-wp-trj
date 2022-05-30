from dash import Dash, html, dcc, Input, Output
import pandas as pd
import plotly.express as px
from hplib import hplib as hpl
import plotly.graph_objects as go
from PLZtoWeatherRegion import getregion

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = Dash(__name__, external_stylesheets=external_stylesheets)

df = pd.read_pickle('results_summary_new.pkl')
heatpumps=hpl.load_database()
heatpumps=heatpumps[['Manufacturer', 'Model', 'Date', 'SPL indoor [dBA]', 'SPL outdoor [dBA]', 'PSB [W]', 'P_th_h_ref [W]','MAPE_P_el', 'MAPE_COP', 'MAPE_P_th',
       'P_th_c_ref [W]', 'MAPE_P_el_cooling', 'MAPE_EER', 'MAPE_Pdc']]
region=['Nordseeküste','Ostseeküste','Nordwestdeutsches Tiefland','Nordostdeutsches Tiefland','Niederrheinisch-westfälische Bucht und Emsland','Nördliche und westliche Mittelgebirge, Randgebiete',
'Nördliche und westliche Mittelgebirge, zentrale Bereiche','Oberharz und Schwarzwald (mittlere Lagen)','Thüringer Becken und Sächsisches Hügelland','Südöstliche Mittelgebirge bis 1000 m',
'Erzgebirge, Böhmer- und Schwarzwald oberhalb 1000 m','Oberrheingraben und unteres Neckartal','Schwäbisch-fränkisches Stufenland und Alpenvorland','Schwäbische Alb und Baar',
'Alpenrand und -täler']
app.layout = html.Div([
    html.Div([

        html.Div([
            dcc.Input(
                placeholder='Wohnort oder PLZ',
                type='text',
                value='',
                id='Standort',            
            ),'enspricht Wetterregion: ',dcc.Dropdown(region,
                        id='region'),
            html.Div("Gebäudetyp: "),
            dcc.Dropdown(
                df['Gebäudetyp'].unique(),
                'Neubau (150 Qm und 0.6 W/(K*Qm))',
                id='sort2',
            ),
            "PV-Ausrichtung: ",
            dcc.Dropdown(
                df['PV-Ausrichtung'].unique(),
                'Süd',
                id='sort3',
            ),
        ],
        style={'width': '49%', 'display': 'inline-block'}),

        html.Div([
            "Strombezugskosten in ct/kWh: ",
            dcc.Slider(28, 40, 1,
               value=35,
               id='strombezugskosten'
            ),
            "Einspeisevergütung in ct/kWh: ",
            dcc.Slider(0, 12, 1,
               value=6,
               id='einspeisevergütung'
            ),
            
        ], style={'width': '49%', 'float': 'right', 'display': 'inline-block'})
    ], style={
        'padding': '10px 5px'
    }),
    html.Div([
        dcc.Graph(
            id='crossfilter-indicator-scatter',
            hoverData={'points': [{'curveNumber': 0,'x':'geregelt','hovertext': 'Generic'}]},
            clickData={'points': [{'curveNumber': 0,'x':'geregelt','hovertext': 'Generic'}]}
        )
    ], style={'width': '100%', 'display': 'inline-block', 'padding': '10 50'}),
    html.Div([
        dcc.Graph(
            id='graph2',
            hoverData={'points': [{'curveNumber': 0,'x':'geregelt','hovertext': 'Generic'}]},
            clickData={'points': [{'curveNumber': 0,'x':'geregelt','hovertext': 'Generic'}]}
        )
    ]),
    html.Div([
        dcc.Markdown(
         id='wp-infos')
    ]),
])


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
                    title='Strombezug abzüglich Einspeisevergütung eines EFH mit 10 kWp, 0 kWh Batteriespeicher',
                    labels=dict(x='Bilanzielle Energiekosten [€/a]',y='WP-Models',color='WP-Kategorie'),
                    height=600
            ).update_yaxes(categoryorder='total ascending')
    fig.update_layout(legend=dict(
    orientation="h",
    yanchor="bottom",
    y=1.001,
    xanchor="left"
    ))
    fig.update_xaxes(range=[dff['bilanzielle Energiekosten'].min()*0.8,dff['bilanzielle Energiekosten'].max()*1.05])
    fig.update_layout(margin={'l': 0, 'b': 40, 't': 20, 'r': 0},hovermode='closest')
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
    dff = df[(df['Standort'] == region.index(standort)+1)&(df['Gebäudetyp']==gebäudetyp)&(df['PV-Ausrichtung']==pv)&(df['WP-Name']==wpname)]
    dff['Kosten [1/Jahr]'] = dff['Netzbezug [kWh]'].values * strombezugskosten/100 - dff['Netzeinspeisung [kWh]'].values * einspeisevergütung/100

    if wpname=='Generic':
        if wp_name['points'][0]['curveNumber']==0:
            if wp_name['points'][0]['x']=='geregelt':
                dff=dff.loc[(dff['WP-Kategorie']=='Luft/Wasser')&(dff['WP-Typ']=='geregelt')]
            else:
                dff=dff.loc[(dff['WP-Kategorie']=='Luft/Wasser')&(dff['WP-Typ']!='geregelt')]
        else:
            if wp_name['points'][0]['x']=='geregelt':
                dff=dff.loc[(dff['WP-Kategorie']!='Luft/Wasser')&(dff['WP-Typ']=='geregelt')]
            else:
                dff=dff.loc[(dff['WP-Kategorie']!='Luft/Wasser')&(dff['WP-Typ']!='geregelt')]
    fig = go.Figure()
    for year in [2015, 2045]:
        for typ in dff['Typ'].unique():
            fig.add_trace(go.Scatter(x = dff.loc[(dff['Jahr']==year)&(dff['Typ']==typ)]['Batteriespeicher [kWh]'], y=dff.loc[(dff['Jahr']==year)&(dff['Typ']==typ)]['Kosten [1/Jahr]'], name=str(year)+' ' + typ))
    # Edit the layout
    fig.update_layout(title='Laufende Kosten für ein Jahr Wärme und Strom mit '+wpname+' Wärmepumpe',
                    xaxis_title='Batteriespeicher [kWh]',
                    yaxis_title='Betriebskosten [€/Jahr]')
    fig.update_layout(yaxis=dict(range=[dff.sort_values('Kosten [1/Jahr]')['Kosten [1/Jahr]'].head(1),dff.sort_values('Kosten [1/Jahr]')['Kosten [1/Jahr]'].tail(1)]))
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
        hp['Other names']=samehp
        hp=hp[['Manufacturer', 'Model','Other names', 'SPL indoor [dBA]', 'PSB [W]',
            'MAPE_COP', 'P_th_c_ref [W]']].rename(columns={'SPL indoor [dBA]':'Geräuschpegel in dBA','PSB [W]': 'Standby Power in W', 'MAPE_COP': 'Durchschnittlicher qualitativer Fehler in %','P_th_c_ref [W]': 'Kühlen'})
        if hp.loc[hp.index[0],'Kühlen']>0:
            hp['Kühlen']='Ja'
        else:
            hp['Kühlen']='Nein'
    except:
        pass
    return hp.to_markdown()

if __name__ == '__main__':
    app.run_server()