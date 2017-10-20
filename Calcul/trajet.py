import os
import sys
import googlemaps
sys.path.insert(0,"../API")
import opendataparis

class Trajet:
    """Version test pour caractériser un trajet"""
    api_key = "AIzaSyBZnbh42NFcXC-3JWSX1um84G8RZ9rTmiA"

    def __init__(self,origine,destination):
        self.origine = origine
        self.destination = destination
        self.distance = 0
        self.temps = 0
        self.transport = ""

    def calculer(self,transport):
        self.transport = transport
        client = googlemaps.Client(key=Trajet.api_key)
        trajet = googlemaps.Client.directions(client, origin=self.origine, destination=self.destination, mode=self.transport)
        self.distance = trajet[0]['legs'][0]['distance']['value']
        self.temps = trajet[0]['legs'][0]['duration']['value']

    def definir(self,transport,distance,temps):
        """Au lieu de calculer le distance et le temps de transport, on les rentre directement (par exemple s'ils ont été calculés par un autre moyen)."""
        self.transport = transport
        self.distance = distance
        self.temps = temps

    def __repr__(self):
        return self.transport+" - distance : "+str(self.distance)+" / temps : "+str(self.temps)

class Trajet_Lib(Trajet):
    """Version test pour les trajets utilisant le velib ou l'autolib"""

    def __init__(self,origine,destination,trajet_initial,trajet_lib,trajet_final):
        """On ajoute 3 sous-trajets pour représenter les passages à pied et les passages en transport."""
        Trajet.__init__(self,origine,destination)
        self.trajet_initial = trajet_initial
        self.trajet_lib = trajet_lib
        self.trajet_final = trajet_final

    #Penser à changer la méthode calculer (en particulier car le calcul des trajets en transport lib doit être fait en parallèle sur les différents trajets).

#Pour ne pas faire trop d'appels à l'API google, utiliser le calcul des distances en matrice pour les différentes stations. Par conséquent il faut pouvoir créer les différents trajets lib en même temps.
class Trajet_Lib_Liste:
    """Classe pour générer et travailler sur un ensemble de Trajet_Lib entre deux points, en fonction des stations à proximité"""
    api_key = "AIzaSyBZnbh42NFcXC-3JWSX1um84G8RZ9rTmiA"

    def __init__(self,origine,destination,transport):
        #Attention, origine et destination doivent être fournies en coordonnées géographiques
        self.origine = origine
        self.destination = destination
        self.transport = transport
        if transport=="velib":
            self.client = opendataparis.Client_Velib()
            self.mode = "bicycling" #Vérifier le nom des modes de Google
        elif transport=="autolib":
            self.client = opendataparis.Client_Autolib()
            self.mode="driving"
        else:
            self.client = None
            self.mode ="walking"
        self.stations_departs = []
        self.stations_arrivees = []

    def stations(self,distance_depart,distance_arrivee):
        """Il va falloir utiliser l'appel à l'API OpenData Paris pour trouver les stations à proximité."""
        # Pour l'instant on va utiliser les coordonnées au format fourni par Opendata Paris
        self.stations_departs = self.client.cherche_depart(self.origine[0],self.origine[1],distance_depart)
        self.stations_arrivees = self.client.cherche_arrivee(self.destination[0],self.destination[1],distance_arrivee)

    def calculer_sous_trajets(self):
        client_google = googlemaps.Client(key=Trajet.api_key)
        liste_trajets = []

        #Trajets lib
        matrice_trajets_lib = []
        resultat_api_trajets_lib = googlemaps.Client.distance_matrix(client_google,self.stations_departs,self.stations_arrivees,mode=self.mode)
        nombre_departs = len(self.stations_departs)
        nombre_arrivees = len(self.stations_arrivees)
        for indice_depart in range(0,nombre_departs):
            matrice_trajets_lib.append([])
            for indice_arrivee in range (0,nombre_arrivees):
                matrice_trajets_lib[indice_depart].append([])
                matrice_trajets_lib[indice_depart][indice_arrivee] = Trajet(resultat_api_trajets_lib['origin_addresses'][indice_depart],resultat_api_trajets_lib['destination_addresses'][indice_arrivee])
                matrice_trajets_lib[indice_depart][indice_arrivee].definir(self.mode,resultat_api_trajets_lib['rows'][indice_depart]['elements'][indice_arrivee]['distance']['value'],resultat_api_trajets_lib['rows'][indice_depart]['elements'][indice_arrivee]['duration']['value'])

        #Trajets initiaux
        liste_trajets_initiaux = []
        resultat_api_trajets_initiaux = googlemaps.Client.distance_matrix(client_google,[self.origine],self.stations_departs,mode='walking')
        for indice_depart in range(0,nombre_departs):
            liste_trajets_initiaux.append([])
            liste_trajets_initiaux[indice_depart] = Trajet(resultat_api_trajets_initiaux['origin_addresses'][0],resultat_api_trajets_initiaux['destination_addresses'][indice_depart])
            liste_trajets_initiaux[indice_depart].definir(self.mode,resultat_api_trajets_initiaux['rows'][0]['elements'][indice_depart]['distance']['value'],resultat_api_trajets_initiaux['rows'][0]['elements'][indice_depart]['duration']['value'])

        #Trajets finaux
        liste_trajets_finaux = []
        resultat_api_trajets_finaux = googlemaps.Client.distance_matrix(client_google,self.stations_arrivees,[self.destination],mode='walking')
        for indice_arrivee in range(0,nombre_departs):
            liste_trajets_finaux.append([])
            liste_trajets_finaux[indice_arrivee] = Trajet(resultat_api_trajets_finaux['origin_addresses'][indice_arrivee],resultat_api_trajets_finaux['destination_addresses'][0])
            liste_trajets_finaux[indice_arrivee].definir(self.mode,resultat_api_trajets_finaux['rows'][indice_arrivee]['elements'][0]['distance']['value'],resultat_api_trajets_finaux['rows'][indice_arrivee]['elements'][0]['duration']['value'])

        #Construction des trajets entiers
        for indice_depart in range(0,nombre_departs):
            for indice_arrivee in range (0,nombre_arrivees):
                liste_trajets.append(Trajet_Lib(self.origine,self.destination,liste_trajets_initiaux[indice_depart],matrice_trajets_lib[indice_depart][indice_arrivee],liste_trajets_finaux[indice_arrivee]))
                distance_totale = liste_trajets[-1].trajet_initial.distance + liste_trajets[-1].trajet_lib.distance + liste_trajets[-1].trajet_final.distance
                temps_total = liste_trajets[-1].trajet_initial.temps + liste_trajets[-1].trajet_lib.temps + liste_trajets[-1].trajet_final.temps
                liste_trajets[-1].definir(self.transport,distance_totale,temps_total)
        return liste_trajets

if __name__ == "__main__":

    test = Trajet_Lib_Liste([48.9,2.34],[48.85,2.33],"autolib")
    test.stations(1000,1000)
    liste_trajets = test.calculer_sous_trajets()
    for i in range(len(liste_trajets)):
        print(liste_trajets[i])
    print(liste_trajets[3].trajet_initial.temps)
    os.system('pause')

