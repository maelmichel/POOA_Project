import requests
import os
"""à faire:
- Faire les getter et setter pour les Vélibs et Autolibs"""

class Client_Lib:
    """Classe pour compléter un appel à l'API OpenData Paris, en particulier pour construire une méthode permettant de retrouver les informations sur les stations (Autolib ou Vélib)
     dans un rayon donné autour d'un point """

    def __init__(self):
        self._uri = ""

    def _stations(self,latitude,longitude,distance):
        """Récupère la liste des stations (avec toutes les informations disponibles, comme les coordonées) autour d'un lieu donné (Latitude,Longitude)."""
        new_uri = self.uri+"&geofilter.distance="+str(latitude)+"%2C"+str(longitude)+"%2C"+str(distance)
        try:
            reponse = requests.get(new_uri)
            status_code = reponse.status_code
            assert status_code == 200
            message = reponse.json()
            message = message['records']
            return message
        except AssertionError:
            raise AssertionError("Erreur de connexion à l'API.")
        except requests.exceptions.ConnectionError:
            raise ConnectionError ("Veuillez vérifier votre connexion Internet")


    @property
    def uri(self):
        return self._uri

class Client_Autolib(Client_Lib):
    """Appel à l'API OpenData Paris pour les stations Autolib"""
    def __init__(self):
        Client_Lib.__init__(self)
        self._uri = "https://opendata.paris.fr/api/records/1.0/search/?dataset=autolib-disponibilite-temps-reel&lang=fr&rows=-1"

    def stations(self,latitude,longitude,distance):
        """Methode permettant de créer un objet de la classe Stations_Autolib pour chaque stations trouvés par l'API"""
        message = Client_Lib._stations(self,latitude,longitude,distance)
        liste_stations = []
        for i in range(0,len(message)):
            status = message[i]['fields']['status']
            dist = message[i]['fields']['dist']
            charging_status = message[i]['fields']['charging_status']
            rental_status = message[i]['fields']['rental_status']
            cars = message[i]['fields']['cars']
            geo_point = message[i]['fields']['geo_point']
            charge_slots = message[i]['fields']['charge_slots']
            postal_code = message[i]['fields']['postal_code']
            subscription_status = message[i]['fields']['subscription_status']
            slots = message[i]['fields']['slots']
            address = message[i]['fields']['address']
            liste_stations.append(Station_Autolib(status,dist,charging_status,rental_status,cars,geo_point,charge_slots,postal_code,subscription_status,slots,address))
        return liste_stations

    def cherche_depart(self, latitude, longitude, distance):
        """Récupère la liste des coordonnées de stations utilisables pour un départ dans un rayon donné."""
        liste = self.stations(latitude, longitude, distance)
        nouvelle_liste = []
        for i in range(0, len(liste)):
            if (liste[i].status == "ok") & (liste[i]._cars > 0):
                # Remarque : on pourra soulever une alerte tout de même si le nombre de voitures restantes est faible
                nouvelle_liste.append(liste[i].geo_point)
        return nouvelle_liste

    def cherche_arrivee(self,latitude,longitude,distance):
        """Récupère la liste des coordonnées de stations utilisables pour une arrivée dans un rayon donné."""
        liste = self.stations(latitude, longitude, distance)
        nouvelle_liste = []
        for i in range(0, len(liste)):
            if (liste[i].status == "ok") & (liste[i]._slots > 0):
                # Remarque : on pourra soulever une alerte tout de même si le nombre de places restantes est faible
                nouvelle_liste.append(liste[i].geo_point)
        return nouvelle_liste

    @property
    def uri(self):
        return self._uri

class Client_Velib(Client_Lib):
    """Appel à l'API OpenData Paris pour les stations Vélib"""
    def __init__(self):
        Client_Lib.__init__(self)
        self._uri = "https://opendata.paris.fr/api/records/1.0/search/?dataset=stations-velib-disponibilites-en-temps-reel&lang=fr&rows=-1"

    def stations(self, latitude, longitude, distance):
        """Methode permettant de créer un objet de la classe Stations_Velib pour chaque stations trouvés par l'API"""
        message = Client_Lib._stations(self, latitude, longitude, distance)
        liste_stations = []
        for i in range(0, len(message)):
            status = message[i]['fields']['status']
            dist = message[i]['fields']['dist']
            name = message[i]['fields']['name']
            available_bike_stands = message[i]['fields']['available_bike_stands']
            banking = message[i]['fields']['banking']
            available_bikes = message[i]['fields']['available_bikes']
            address = message[i]['fields']['address']
            position = message[i]['fields']['position']
            liste_stations.append(Station_Velib(status,dist,name,available_bike_stands,banking,available_bikes,address,position))
        return liste_stations

    def cherche_depart(self, latitude, longitude, distance):
        """Récupère la liste des coordonnées de stations utilisables pour un départ dans un rayon donné."""
        liste = self.stations(latitude, longitude, distance)
        nouvelle_liste = []
        for i in range(0, len(liste)):
            if (liste[i].status == "OPEN") & (liste[i]._available_bikes > 0):
                # Remarque : on pourra soulever une alerte tout de même si le nombre de vélos restant est faible
                nouvelle_liste.append(liste[i].position)
        return nouvelle_liste

    def cherche_arrivee(self,latitude,longitude,distance):
        """Récupère la liste des coordonnées de stations utilisables pour une arrivée dans un rayon donné."""
        liste = self.stations(latitude, longitude, distance)
        nouvelle_liste = []
        for i in range(0, len(liste)):
            if (liste[i].status == "OPEN") & (liste[i]._available_bike_stands > 0):
                # Remarque : on pourra soulever une alerte tout de même si le nombre de places restantes est faible
                nouvelle_liste.append(liste[i].position)
        return nouvelle_liste

    @property
    def uri(self):
        return self._uri

class Station_Velib:
    """Classe permettant de formaliser une station Vélib avec les données issues de l'API"""

    def __init__(self,status,dist,name,available_bike_stands,banking,available_bikes,address,position):
        self._status = status
        self._dist = dist
        self._name = name
        self._available_bike_stands = available_bike_stands
        self._banking = banking
        self._available_bikes = available_bikes
        self._address = address
        self._position = position

    # On protège tous nos attributs. Aucune méthode pour modifier les attributs n'est requise car on ne veut pas modifier les résultats de l'API
    @property
    def status(self):
        return self._status

    @property
    def name(self):
        return self._name

    @property
    def banking(self):
        return self._banking

    @property
    def available_bikes(self):
        return self._available_bikes

    @property
    def address(self):
        return self._address

    @property
    def position(self):
        return self._position

    @property
    def dist(self):
        return self._dist


class Station_Autolib:
    """Classe permettant de formaliser une station Autolib avec les données issus de l'API"""
    def __init__(self,status,dist,charging_status,rental_status,cars,geo_point,charge_slots,postal_code,subscription_status,slots,id,address):
        self._status = status
        self._dist = dist
        self._charging_status = charging_status
        self._rental_status = rental_status
        self._cars = cars
        self._geo_point = geo_point
        self._charge_slots = charge_slots
        self._postal_code = postal_code
        self._subscription_status = subscription_status
        self._slots = slots
        self._id = id
        self._address = address

    # On protège tous nos attributs. Aucune méthode pour modifier les attributs n'est requise car on ne veut pas modifier les résultats de l'API
    @property
    def status(self):
        return self._status

    @property
    def dist(self):
        return self._dist

    @property
    def charging_status(self):
        return self._charging_status

    @property
    def rental_status(self):
        return self._rental_status

    @property
    def cars(self):
        return self._cars

    @property
    def geo_point(self):
        return self._geo_point

    @property
    def charge_slots(self):
        return self._charge_slots

    @property
    def postal_code(self):
        return self._postal_code

    @property
    def subscription_status(self):
        return self._subscription_status

    @property
    def slots(self):
        return self._slots

    @property
    def id(self):
        return self._id

    @property
    def adress(self):
        return self._address

if __name__ == "__main__":

    latitude = 48.852
    longitude = 2.347
    distance = 500

    latitude_bis = 48.900
    longitude_bis = 2.340
    distance_bis = 500

    test = Client_Velib()

    departs = test.cherche_depart(latitude,longitude,distance)
    arrivees = test.cherche_arrivee(latitude_bis,longitude_bis,distance_bis)
    testest = test.stations(latitude,longitude,distance)
    print(testest[0].position)

    print(len(departs))
    print(len(arrivees))

    os.system("pause")