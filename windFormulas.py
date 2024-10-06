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
def omrade(infokommune: dict) -> tuple:
    '''bestemmer høydeverdier for c,alt ut fra område/ fylke
    '''
    omrade = infokommune["omrade"]
    if omrade == "1":
        H0o = 900
        Htopp = 1500
    elif omrade == "2":
        H0o = 700
        Htopp = 1300
    else:
        H0o = 400
        Htopp = 1000
    return Htopp, H0o
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

def kr(ruhet) -> float:

    '''gir ut verdien kr ut fra tabell NA.4.1 vindlast'''
    kr = [0.16, 0.17, 0.19, 0.22, 0.24]
    return kr[ruhet]
def z0(ruhet):
    '''gir ut verdien z0 ut fra tabell NA.4.1 vindlast'''
    z0 = [0.003, 0.01, 0.05, 0.3, 1.0]
    return z0[ruhet]

def zmin(ruhet: int) -> int:
    zmin = [2, 2, 3, 8, 16]
    return zmin[ruhet] 
def qpz(Iv:float, vmz:float) -> float:
    """regner ut qp(z)"""
    ro = 1.25
    qpz = (1 + 7*Iv)*(1/2)*ro*vmz*vmz
    return qpz
def crz(kr, z, z0) -> float:
    """regner ut cr(z)"""
    crz = kr*(math.log(z/z0))
    return crz

def Ivz(ki, coz, z, z0):
    Ivz = ki/(coz*math.log(z/z0))
    return Ivz

class Vindtilfeller:
    def __init__(self, z:int, kommune:str, ruhet:int, glattsone:int, avstand_glatt_km:float) -> None:
        self.ruhet = ruhet
        self.zmin = zmin(self.ruhet)
        if z > self.zmin: 
            self.z = z
        else:
            self.z = self.zmin
        self.z0 = z0(self.ruhet)
        self.kommune = kommune
        self.vb0 = float(infoKommune(kommune)["Vb,0"])
        self.kr = kr(self.ruhet)
        self.crz = crz(self.kr, self.z, self.z0)
        self.avstand_glatt_km = avstand_glatt_km
        self.glattsone = glattsone
        self.cdir = 1
        self.cseason = 1
        self.vb = self.cdir * self.cseason * self.vb0
        self.vmz = self.crz * self.vb
        self.k3 = k3(self.ruhet, self.glattsone, self.avstand_glatt_km)

    def get_k3(self):
        return self.k3
                            
class Type1(Vindtilfeller):
    def __init__(self, z: int, kommune: str, ruhet: int, glattsone: int, avstand_glatt_km: float) -> None:
        super().__init__(z, kommune, ruhet, glattsone, avstand_glatt_km)
    
    
class Type3(Vindtilfeller):
    def __init__(self, z: int, kommune: str, glattsone: int, avstand_glatt_km: float,vinkel:float, hoyde:int, avstand_topp:int, ruhet = 2) -> None:
        super().__init__(z, kommune, ruhet, glattsone, avstand_glatt_km)
        self.vinkel = vinkel
        self.hoyde = hoyde
        self.avstand_topp = avstand_topp
        self.qpz = self.calc_qpz()
        self.qkast = self.get_qkast()

    def get_c0z_ki(self):
        hoyde = self.hoyde
        avstand = self.avstand_topp
        vinkel = self.vinkel

        if vinkel >= 40 and (10 * hoyde) <= avstand <= (15*hoyde):
            ki = 1.75
            c0z = 0.9
        elif vinkel >= 40 and avstand < 10 * hoyde:
            ki = 1.75
            C0z = 1.0
        elif 30 <= vinkel < 40 and avstand <= 8 * hoyde:
            ki = 1.75
            C0z = 0.9
        else: 
            ki = 1
            C0z = 1
        return C0z, ki
        
    def calc_qpz(self):

        C0z, ki = self.get_c0z_ki()
        z = self.z
        z0 = self.z0
        vmz = self.vmz
        qpz1 = qpz(Ivz(ki, C0z,z,z0), vmz)
        return qpz1

    def get_qpz(self):
        return self.qpz
    
    def get_qkast(self):
        qpz = self.get_qpz()
        k3 = self.get_k3()
        return qpz*k3
    

class Type5(Vindtilfeller):
    def __init__(self, z: int, kommune: str, ruhet: int, glattsone: int, avstand_glatt_km: float, moh:int) -> None:
        super().__init__(z, kommune, ruhet, glattsone, avstand_glatt_km)
        self.moh = moh
        self.c0z = 1
        self.ki = 1
        self.qp0z = self.calc_qp0z()
        self.c_alt = self.calc_c_alt()
        self.qkast = self.calc_qkast()

    def calc_qp0z(self):
        ki = self.ki
        c0z = self.c0z
        vmz = self.vmz
        z = self.z
        z0 = self.z0
        return qpz(Ivz(ki, c0z,z,z0), vmz)
        

    def calc_c_alt(self) -> float:
        Htopp, H0 = omrade(infoKommune(self.kommune))
        V0 = 30 #m/s
        V_b0 = self.vb0
        H = self.moh
        if V_b0 >= V0 or H<H0:
            c_alt = 1
        else:
            c_alt = 1.0 + (V0-V_b0)*(H-H0)/(V_b0*(Htopp-H0))
        return round(c_alt,2)
    
    def calc_qkast(self):
        qp0z = self.qp0z
        k3 = self.k3
        calt = self.c_alt
        qkast = qp0z *calt*calt*k3
        return qkast
        


a =Type3(30, "aurland", 1, 3, 35, 200, 800)

print(a.qkast)

