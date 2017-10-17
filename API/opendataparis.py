import requests
import os

class Station_Velib:
    """Pour caractériser une station velib telle que renvoyée par l'API"""

    def __init__(self,status,contract_name,dist,name,bonus,bike_stands,number,last_update,available_bike_stands,banking,available_bikes,address,position):
        self.status = status
        self.contract_name = contract_name
        self.dist = dist
        self.name = name
        self.bonus = bonus
        self.bike_stands = bike_stands
        self.number = number
        self.last_update = last_update
        self.available_bike_stands = available_bike_stands
        self.banking = banking
        self.available_bikes = available_bikes
        self.address = address
        self.position = position

class Station_Autolib:
    """Pour caractériser une station autolib telle que renvoyée par l'API"""

    def __init__(self,status,city,kind,dist,station_type,charging_status,rental_status,cars_counter_bluecar,cars,public_name,geo_point,charge_slots,postal_code,cars_counter_utilib_1_4,subscription_status,slots,id,address,cars_counter_utilib):
        self.status = status
        self.city = city
        self.kind = kind
        self.dist = dist
        self.station_type = station_type
        self.charging_status = charging_status
        self.rental_status = rental_status
        self.cars_counter_bluecar = cars_counter_bluecar
        self.cars = cars
        self.public_name = public_name
        self.geo_point = geo_point
        self.charge_slots = charge_slots
        self.postal_code = postal_code
        self.cars_counter_utilib_1_4 = cars_counter_utilib_1_4
        self.subscription_status = subscription_status
        self.slots = slots
        self.id = id
        self.address = address
        self.cars_counter_utilib = cars_counter_utilib

class Client_Lib:
    """Classe pour effectuer un appel à l'API OpenData Paris, en particulier pour obtenir les stations à proximité"""

    def __init__(self):
        self.uri = ""

    def stations(self,latitude,longitude,distance):
        """Récupère la liste des stations (avec les informations pertinantes, comme les coordonées) autour d'un lieu donné."""
        new_uri = self.uri+"&geofilter.distance="+str(latitude)+"%2C"+str(longitude)+"%2C"+str(distance)
        reponse = requests.get(new_uri)
        try:
            status_code = reponse.status_code
            assert status_code == 200
            message = reponse.json()
            message = message['records']
            return message
        except AssertionError:
            print("Erreur de connexion à l'API.")


class Client_Autolib(Client_Lib):

    def __init__(self):
        Client_Lib.__init__(self)
        self.uri = "https://opendata.paris.fr/api/records/1.0/search/?dataset=autolib-disponibilite-temps-reel&lang=fr&rows=-1"

    def stations(self,latitude,longitude,distance):
        message = Client_Lib.stations(self,latitude,longitude,distance)
        liste_stations = []
        for i in range(0,len(message)):
            status = message[i]['fields']['status']
            city = message[i]['fields']['city']
            kind = message[i]['fields']['kind']
            dist = message[i]['fields']['dist']
            station_type = message[i]['fields']['station_type']
            charging_status = message[i]['fields']['charging_status']
            rental_status = message[i]['fields']['rental_status']
            cars_counter_bluecar = message[i]['fields']['cars_counter_bluecar']
            cars = message[i]['fields']['cars']
            public_name = message[i]['fields']['public_name']
            geo_point = message[i]['fields']['geo_point']
            charge_slots = message[i]['fields']['charge_slots']
            postal_code = message[i]['fields']['postal_code']
            cars_counter_utilib_1_4 = message[i]['fields']['cars_counter_utilib_1.4']
            subscription_status = message[i]['fields']['subscription_status']
            slots = message[i]['fields']['slots']
            id = message[i]['fields']['id']
            address = message[i]['fields']['address']
            cars_counter_utilib = message[i]['fields']['cars_counter_utilib']
            liste_stations.append(Station_Autolib(status,city,kind,dist,station_type,charging_status,rental_status,cars_counter_bluecar,cars,public_name,geo_point,charge_slots,postal_code,cars_counter_utilib_1_4,subscription_status,slots,id,address,cars_counter_utilib))
        return liste_stations

    def cherche_depart(self, latitude, longitude, distance):
        """Récupère la liste des coordonnées de stations utilisable pour un départ dans un rayon donné."""
        liste = self.stations(latitude, longitude, distance)
        nouvelle_liste = []
        for i in range(0, len(liste)):
            if (liste[i].status == "ok") & (liste[i].cars > 0):
                # Remarque : on pourra soulever une alerte tout de même si le nombre de voitures restantes est faible
                nouvelle_liste.append(liste[i].geo_point)
        return nouvelle_liste

    def cherche_arrivee(self,latitude,longitude,distance):
        """Récupère la liste des coordonnées de stations utilisable pour une arrivée dans un rayon donné."""
        liste = self.stations(latitude, longitude, distance)
        nouvelle_liste = []
        for i in range(0, len(liste)):
            if (liste[i].status == "ok") & (liste[i].slots > 0):
                # Remarque : on pourra soulever une alerte tout de même si le nombre de places restantes est faible
                nouvelle_liste.append(liste[i].geo_point)
        return nouvelle_liste

class Client_Velib(Client_Lib):

    def __init__(self):
        Client_Lib.__init__(self)
        self.uri = "https://opendata.paris.fr/api/records/1.0/search/?dataset=stations-velib-disponibilites-en-temps-reel&lang=fr&rows=-1"

    def stations(self, latitude, longitude, distance):
        message = Client_Lib.stations(self, latitude, longitude, distance)
        liste_stations = []
        for i in range(0, len(message)):
            status = message[i]['fields']['status']
            contract_name = message[i]['fields']['contract_name']
            dist = message[i]['fields']['dist']
            name = message[i]['fields']['name']
            bonus = message[i]['fields']['bonus']
            bike_stands = message[i]['fields']['bike_stands']
            number = message[i]['fields']['number']
            last_update = message[i]['fields']['last_update']
            available_bike_stands = message[i]['fields']['available_bike_stands']
            banking = message[i]['fields']['banking']
            available_bikes = message[i]['fields']['available_bikes']
            address = message[i]['fields']['address']
            position = message[i]['fields']['position']
            liste_stations.append(Station_Velib(status,contract_name,dist,name,bonus,bike_stands,number,last_update,available_bike_stands,banking,available_bikes,address,position))
        return liste_stations

    def cherche_depart(self, latitude, longitude, distance):
        """Récupère la liste des coordonnées de stations utilisable pour un départ dans un rayon donné."""
        liste = self.stations(latitude, longitude, distance)
        nouvelle_liste = []
        for i in range(0, len(liste)):
            if (liste[i].status == "OPEN") & (liste[i].available_bikes > 0):
                # Remarque : on pourra soulever une alerte tout de même si le nombre de vélos restant est faible
                nouvelle_liste.append(liste[i].position)
        return nouvelle_liste

    def cherche_arrivee(self,latitude,longitude,distance):
        """Récupère la liste des coordonnées de stations utilisable pour une arrivée dans un rayon donné."""
        liste = self.stations(latitude, longitude, distance)
        nouvelle_liste = []
        for i in range(0, len(liste)):
            if (liste[i].status == "OPEN") & (liste[i].available_bike_stands > 0):
                # Remarque : on pourra soulever une alerte tout de même si le nombre de places restantes est faible
                nouvelle_liste.append(liste[i].position)
        return nouvelle_liste


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