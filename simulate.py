import pandas as pd
from hplib import hplib as hpl

def simulate(standort, E_gas, T_vorlauf, n_Personen, eff_tww, Baujahr, wp_model, pv_kwp ,pv_orientation):
    TRJ=pd.read_csv('src/simulation_data/TRJ-Tabelle.csv').head(15)# average year
    eff_heiz=0.9                #average from DIN EN 12831 Tabelle 38
    
    if Baujahr<=2000:           
        if Baujahr<=1995:
            eff_heiz=0.85       #average from DIN EN 12831 Tabelle 38
        Heizgrenztemperatur=15  #IWU Heizgrenztemperatur 
        gtz=TRJ.iloc[standort-1,11]
    elif Baujahr>2015:
        Heizgrenztemperatur=10
        gtz=TRJ.iloc[standort-1,12]
    else:
        Heizgrenztemperatur=12
        gtz=TRJ.iloc[standort-1,10]
    weather=pd.read_csv('src/simulation_data/weather/weather_'+str(standort)+'_a_2015_1min.csv')
    P_th_h_calc=[]
    E_TWW=(14.9*30*n_Personen)/eff_tww
    E_Heiz=(E_gas-E_TWW)* eff_heiz * 1000
    for t in weather.index:
        temp=weather.at[t, 'temperature 24h [degC]']
        if temp < Heizgrenztemperatur:
            P_th_h_calc.append((20-temp)*E_Heiz/(gtz*24))
        else:
            P_th_h_calc.append(0)
    return P_th_h_calc
