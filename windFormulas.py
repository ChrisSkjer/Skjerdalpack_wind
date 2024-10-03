import math
import csv

def infoKommune(kommune: str) -> dict:
    '''
    tar inn en kommune og gir ut en dict med info, om fylke, vb0 og område
    '''
    filePath = 'files/infoNS1.csv'
    kommune = kommune.strip().title()
    with open(filePath, "r", encoding= "utf-8-sig") as fil:
        leser = csv.DictReader(fil, delimiter=";")
        for rad in leser:
            if rad["Kommune"] == kommune:
                info = rad
    return info

def V1tabell() -> list:
    '''returner en liste av tabell V.1 for å bestemme k3'''
    filepath = "files/V.1 tabell for k3.csv"
    with open(filepath, "r") as V1:
        V1 = csv.reader(V1, delimiter=";")
        
        return list(V1)
    
def interpolering(verdi1: float, verdi2:float, delta: float, x:float, start: float=None)  -> float:
    '''Funksjon for interpolering mellom to verdier, om ikkje annet er angit vil starverdien vere 
    x = 0 i xy koordinatsystemet'''
    if start is None:
        start = 0

    formel = verdi1 + ((verdi2-verdi1)/delta)*(x-start)
    return formel
    
def k3(ruhet: int, glattsone: int, avstand: float) -> float:
    '''
    funksjon som skal bestemme konstanten k3
    '''
    if glattsone >= ruhet:
        return 1
    
    v1Tabell = V1tabell()
    delta_nBA = ruhet-glattsone
    verdi1 = float(v1Tabell[delta_nBA-1][glattsone])
    verdi2 = float(v1Tabell[delta_nBA-1][glattsone+4])

    if  0.5 <= avstand <= 2.5:
        k3 = interpolering(verdi1, verdi2,2.00,float(avstand), 0.50)
    elif 2.5 < avstand <= 5:
        verdi1 = float(v1Tabell[delta_nBA-1][glattsone+4])
        verdi2 = float(v1Tabell[delta_nBA-1][glattsone+8])
        k3 = interpolering(verdi1, verdi2, 2.50, avstand, 2.50)
    elif 5 < avstand <= 10:
        verdi1 = float(v1Tabell[delta_nBA-1][glattsone+8])
        verdi2 = float(v1Tabell[delta_nBA-1][glattsone+12])
        k3 = interpolering(verdi1, verdi2, 5.00, avstand, 5.00)
    else: k3 = 1
    return k3

