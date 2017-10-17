import os
import googlemaps

# À mettre dans la partie UI
'''
class Utilisateur:
    """Version test pour rassembler les demandes de l'utilisateur"""

    def __init__(self):
        """Pour l'instant utilisateur défini par son trajet souhaité et sa charge"""
        self.origine = ""
        self.destination = ""
        self.charge = False

    def definir_utilisateur(self):
        self.origine = input("Point de départ : ")
        self.destination = input("Point d'arrivée : ")
        self.charge = input("Charge (laisser vide si aucune charge) : ")
        '''

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
        trajet = googlemaps.Client.directions(client, origin=test.origine, destination=test.destination, mode=self.transport)
        self.distance = trajet[0]['legs'][0]['distance']['text']
        self.temps = trajet[0]['legs'][0]['duration']['text']

    def __repr__(self):
        return self.transport+" - distance : "+str(self.distance)+" / temps : "+str(self.temps)

class Trajet_Lib(Trajet):
    """Version test pour les trajets utilisant le velib ou l'autolib"""

    def __init__(self,origine,destination):
        """On rajoute des emplacements pour indiquer le point de départ et d'arrivée de la partie en transport lib..."""
        Trajet.__init__(self,origine,destination)
        self.origine_lib = ""
        self.destination_lib = ""

class Trajet_Lib_Liste(Trajet_Lib):
    """Classe pour générer et travailler sur un ensemble de Trajet_Lib entre deux points, en fonction des stations à proximité"""

    def __init__(self,origine,destination):
        self.origine = origine
        self.destination = destination
        self.list = []

    def creer_liste(self,distance_depart,distance_arrivee=distance_depart):
        """Il va falloir utiliser l'appel à l'API OpenData Paris pour trouver les stations à proximité."""
        # Pour l'instant on va utiliser les coordonnées au format fourni par Opendata Paris
        liste_trajets = []
        departs =

if __name__ == "__main__":

    test = Utilisateur()
    test.definir_utilisateur()

    trajet_voiture = Trajet(test.origine,test.destination)
    trajet_voiture.calculer('driving')
    print(trajet_voiture)
    trajet_velo = Trajet(test.origine,test.destination)
    trajet_velo.calculer('bicycling')
    print(trajet_velo)
    trajet_pieds = Trajet(test.origine,test.destination)
    trajet_pieds.calculer('walking')
    print(trajet_pieds)
    os.system('pause')