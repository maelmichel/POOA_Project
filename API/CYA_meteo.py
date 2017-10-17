import requests
import datetime


class Meteo():
    """Classe definissant la meteo lors de l'utilisation du service"""
    url = "http://www.infoclimat.fr/public-api/gfs/json?_ll=48.85341,2.3488&_auth=UUsAFwd5UnBWewM0VCJXfgdvAzYJfwQjBHhSMVo%2FAn8DaFAxBGQDZQVrA34EK1FnV3pQMwswCDgDaFIqWigDYlE7AGwHbFI1VjkDZlR7V3wHKQNiCSkEIwRmUjZaPwJ%2FA2FQPQRiA38FaANhBDFRe1dmUDULMQgvA39SNFoyA2BRNQBmB2RSOVY6A2NUZFd8BysDZgk%2FBGgEYVI2WjcCZwNoUDQEYANgBWMDMwQzUXtXY1A0CzAINwNmUjNaNgNoUS0AewcdUkNWJAMhVCZXNgdyA34JYwRiBDM%3D&_c=272acb338257c36795529d891a5b0a9d"
    info = requests.get(url)
    info = info.json()

    def __init__(self):
        self.doc = Meteo.info

    def get_pluie(self,date):
        """Renvoie un float avec """
        date = date.strptime(date, "%Y-%m-%d %H:%M:%S")
        for i in self.doc.keys():
            if type(self.doc[i]) == dict:
                datedict = datetime.datetime.strptime(i, "%Y-%m-%d %H:%M:%S")
                diff = ((date - datedict).total_seconds() / 60) #integration erreur date
                if abs(diff) > 90:
                    continue
                else:
                    niveau_pluie = float(self.doc[i]['pluie'])
                    return niveau_pluie

    def get_temperature(self,date):
        """Renvoie la valeur en °C de la Température dans la plage de temps la plus proche de 'date'"""
        date = date.strptime(date, "%Y-%m-%d %H:%M:%S")
        for i in self.doc.keys():
            if type(self.doc[i]) == dict:
                datedict = datetime.datetime.strptime(i, "%Y-%m-%d %H:%M:%S")
                diff = ((date - datedict).total_seconds() / 60)
                if abs(diff) > 90:
                    continue
                else:
                    tempK = round(float(self.doc[i]['temperature']['2m']), 3)
                    tempC = round(tempK - 273.15, 2)
                    return tempC

    def __repr__(self):
        """Méthode pour représenter les informations de nos employés avec un minimum de formatage"""
        return "{0}".format(self.doc)

if __name__ == "__main__":
    test=Meteo()
    temp = test.get_temperature(datetime.datetime.now())
    pluie = test.get_pluie(datetime.datetime.now())
    print("résultat temp",temp)
    print("résultat pluie",pluie)
