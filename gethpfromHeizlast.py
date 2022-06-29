import pandas as pd

def fitting_hp(energieverbrauch, standort,Vorlauftemperatur,Baujahr,Personen, eff_tww):
    """
    
    Parameters
    ----------
    energieverbrauch [kWh]
    wohnflaeche [m²]
    standort (1-15)
    max. Nutzungsstunden pro Tag [h]
    Heizgrenztemperatur (12 or 15) [°C]
    Returns
    -------
    Heizlast (W)
    """
    
    hp=pd.read_csv('src/simulation_data/hp_Normheizlast.csv')
    weather=pd.read_csv('src/simulation_data/TRJ-Tabelle.csv').head(15)# average year
    eff_heiz=0.9                #average from DIN EN 12831 Tabelle 38
    if Baujahr<=2000:           
        if Baujahr<=1995:
            eff_heiz=0.85       #average from DIN EN 12831 Tabelle 38
        Heizgrenztemperatur=15  #IWU Heizgrenztemperatur 
        gtz=weather.iloc[standort-1,11]
    elif Baujahr>2015:
        Heizgrenztemperatur=10
        gtz=weather.iloc[standort-1,12]
    else:
        Heizgrenztemperatur=12
        gtz=weather.iloc[standort-1,10]
    b=gtz*24/(Heizgrenztemperatur-weather.iloc[standort-1,9])   #DIN/TS 12831-1:2020-04 Formel 50
    Q_TWW=(14.9*30*Personen)/eff_tww                            #DIN/TS 12831-1:2020-04 Formel 57
    Heizlast = (energieverbrauch-Q_TWW)* eff_heiz * 1000 / b    #DIN/TS 12831-1:2020-04 Formel 49
    Heizbedarf=Heizlast+200*Personen                            # Aufschlag TWW
    hp=hp.loc[(hp['Standort']==standort)& (hp['Vorlauftemperatur']==Vorlauftemperatur)&(hp['Normheizlast']>=Heizbedarf)&(hp['Normheizlast']<=Heizbedarf*1.25)]
    return hp.sort_values('COP', ascending=False), Heizbedarf
