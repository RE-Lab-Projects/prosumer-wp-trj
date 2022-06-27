import pandas as pd

def fitting_hp(energieverbrauch, standort,Vorlauftemperatur, P_tww=1000,Heizgrenztemperatur=15):
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
    weather=pd.read_csv('src/simulation_data/TRJ-Tabelle.csv').tail(15)# for extreme Winter year

    if Heizgrenztemperatur==15:
        gtz=weather.iloc[standort-1,11]
    elif Heizgrenztemperatur==12:
        gtz=weather.iloc[standort-1,10]
    Heizlast = (20-weather.iloc[standort-1,9]) * energieverbrauch* 0.86 * 1000 / (24*gtz) + P_tww # delta T * E_gas * eff_gas / GTZ
    hp=hp.loc[(hp['Standort']==standort)& (hp['Vorlauftemperatur']==Vorlauftemperatur)&(hp['Normheizlast']>=Heizlast*0.98)&(hp['Normheizlast']<=Heizlast*1.25)]
    return hp.sort_values('COP', ascending=False)
