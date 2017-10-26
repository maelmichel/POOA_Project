import requests
import datetime
import googlemaps

class PasLeBonFormatDeDateError(Exception):
    pass

class ClePasValideError(Exception):
    pass

class ServeurSurchargeError(Exception):
    pass

class QuotatRequeteError(Exception):
    pass

class ConnectionError(Exception):
    pass

class Meteo():
    """Classe qui va construire un objet résultant de l'appel à l'API
    Document JSON avec des données météo par période de 3h"""

    def __init__(self):
        self._url = "http://www.infoclimat.fr/public-api/gfs/json?_ll=48.85341,2.3488&_auth=UUsAFwd5UnBWewM0VCJXfgdvAzYJfwQjBHhSMVo%2FAn8DaFAxBGQDZQVrA34EK1FnV3pQMwswCDgDaFIqWigDYlE7AGwHbFI1VjkDZlR7V3wHKQNiCSkEIwRmUjZaPwJ%2FA2FQPQRiA38FaANhBDFRe1dmUDULMQgvA39SNFoyA2BRNQBmB2RSOVY6A2NUZFd8BysDZgk%2FBGgEYVI2WjcCZwNoUDQEYANgBWMDMwQzUXtXY1A0CzAINwNmUjNaNgNoUS0AewcdUkNWJAMhVCZXNgdyA34JYwRiBDM%3D&_c=272acb338257c36795529d891a5b0a9d"
        try:
            self._donnees_api = requests.get(self._url)
            self._doc = self._donnees_api.json()
            code_requete = self._doc['request_state']
        except:
            raise ConnectionError("Vérifiez votre connexion Internet ou l'URL d'appel")
        if code_requete == 200:
            pass
        elif code_requete == 400:
            raise UrlPasValideError
        elif code_requete == 409:
            raise ServeurSurchargeError
        elif code_requete == 509:
            raise QuotatRequeteError
        else:
            raise ConnectionError

    @property
    def url(self):
        return self._url
    @property
    def donnees_api(self):
        return self._donnees_api
    @property
    def doc(self):
        return self._doc

    def __repr__(self):
        return "{0}".format(self._doc)


    def get_pluie(self,date):
        """Prend en argument un string sous la forme d'une date YYYY-mm-dd HH:MM:SS ou dd-mm-YYYY HH:MM:SS
        Renvoie un float qui correspond au niveau de précipitation en mm"""

        #On va vérifier que la date est bien: soit une chaine de caractère sous le bon format ou alors un objet datetime
        if isinstance(date,str):
            try:
                dateconvert = datetime.datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
            except ValueError:
                dateconvert = datetime.datetime.strptime(date, "%d-%m-%Y %H:%M:%S") # derniere exception?
        elif isinstance(date,datetime.datetime):
            dateconvert = date
            pass
        else:
            raise PasLeBonFormatDeDateError("Date sous la forme YYYY-mm-dd HH:MM:SS ou dd-mm-YYYY HH:MM:SS")

        for i in self._doc.keys():
            if isinstance(self._doc[i],dict):
                datedict = datetime.datetime.strptime(i, "%Y-%m-%d %H:%M:%S")
                diff = ((dateconvert - datedict).total_seconds() / 60)
                if abs(diff) > 90: # On compare chaque date issues de l'API à la date paramètre et on récupère les données associés à la période de 3h la plus proche (à 90 min avant et après)
                    continue
                else:
                    niveau_pluie = float(self._doc[i]['pluie'])
                    return niveau_pluie

    def get_temperature(self,date):
        """Prend en argument un string sous la forme d'une date YYYY-mm-dd HH:MM:SS
        Renvoie un flaot avec la valeur en °C de la température dans la plage de temps la plus proche de 'date'"""

        #On va vérifier que la date est bien, soit une chaine de caractère sous le bon format soit un objet datetime
        if isinstance(date,str):
            try:
                dateconvert = datetime.datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
            except ValueError:
                dateconvert = datetime.datetime.strptime(date, "%d-%m-%Y %H:%M:%S")
        elif isinstance(date,datetime.datetime):
            dateconvert = date
            pass
        else:
            raise PasLeBonFormatDeDateError("Date sous la forme YYYY-mm-dd HH:MM:SS ou dd-mm-YYYY HH:MM:SS")

        for i in self._doc.keys():
            if isinstance(self._doc[i],dict):
                datedict = datetime.datetime.strptime(i, "%Y-%m-%d %H:%M:%S")
                diff = ((dateconvert - datedict).total_seconds() / 60)
                if abs(diff) > 90: # On compare chaque date issues de l'API à la date paramètre et on récupère les données associés à la période de 3h la plus proche (à 90 min avant et après)
                    continue
                else:
                    tempK = round(float(self._doc[i]['temperature']['2m']), 3)
                    tempC = round(tempK - 273.15, 2)
                    return tempC

    def description_temperature(self,date):
        temp = self.get_temperature(date)
        if temp < 12:
            return "Il fait froid"
        elif (temp >= 12) and (temp < 25):
            return "Parfait pour marcher"
        else:
            return "Oula Commence à faire chaud"


if __name__ == "__main__":
    test = Meteo()
    print(test)
    print(test.url)
    temp = test.get_temperature('2017-10-28 14:20:00')
    pluie = test.get_pluie(datetime.datetime.now())
    comment = test.description_temperature(datetime.datetime.now())
    print("résultat temp",temp)
    print("résultat pluie",pluie)
    print("Commentaire Temps",comment)
