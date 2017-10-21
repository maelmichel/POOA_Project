import os
import sys
import copy
import googlemaps
sys.path.insert(0,"../API")
import opendataparis



class Origine_Et_Destination:
    """Plusieurs classes ayant besoin de gérer l'origine et la destination d'un trajet, cette classe rassemble les méthodes communes qu'elles auront en héritant de celle-ci."""
    api_key = "AIzaSyBZnbh42NFcXC-3JWSX1um84G8RZ9rTmiA"
    client_google = googlemaps.Client(key=api_key)

    def __init__(self):
        self._origine = ""
        self._coord_origine = (48.853,2.350)
        self._destination = ""
        self._coord_destination = (48.853,2.350)
        self._transport = ""

    # Propriétés

    def _get_origine(self):
        return self._origine
    def _set_origine(self, origine):
        self.calculer(origine, self._destination, self._transport)
    origine = property(_get_origine, _set_origine)

    def _get_coord_origine(self):
        return self._coord_origine
    def _set_coord_origine(self, coord):
        result_api = googlemaps.Client.reverse_geocode(Origine_Et_Destination.client_google, coord)
        # /!\ Penser à gérer les erreurs de l'API
        self._set_origine(result_api[0]['formatted_address'])
    coord_origine = property(_get_coord_origine, _set_coord_origine)

    def _get_destination(self):
        return self._destination
    def _set_destination(self, destination):
        self.calculer(self._origine, destination, self._transport)
    destination = property(_get_destination, _set_destination)

    def _get_coord_destination(self):
        return self._coord_destination
    def _set_coord_destination(self, coord):
        result_api = googlemaps.Client.reverse_geocode(Origine_Et_Destination.client_google, coord)
        # /!\ Penser à gérer les erreurs de l'API
        self._set_destination(result_api[0]['formatted_address'])
    coord_destination = property(_get_coord_destination, _set_coord_destination)

    def _get_transport(self):
        return self._transport
    def _set_transport(self, transport):
        self.calculer(self._origine, self._destination, transport)
    transport = property(_get_transport, _set_transport)

    # Méthodes

    def _set_origine_destination_transport(self,origine,destination,transport):
        """Remplit les points d'origine et de destination ainsi que le mode de transport en s'assurant de respecter les formats adéquates."""
        result_api_origine = googlemaps.Client.geocode(Origine_Et_Destination.client_google, origine)
        # /!\ À faire : gérer les erreurs de l'API, en particulier si aucun résultat n'est trouvé
        self._origine = result_api_origine[0]['formatted_address']
        self._coord_origine = (result_api_origine[0]['geometry']['location']['lat'],result_api_origine[0]['geometry']['location']['lng'])
        result_api_destination = googlemaps.Client.geocode(Origine_Et_Destination.client_google, destination)
        # /!\ À faire : gérer les erreurs de l'API, en particulier si aucun résultat n'est trouvé
        self._destination = result_api_destination[0]['formatted_address']
        self._coord_destination = (result_api_destination[0]['geometry']['location']['lat'],result_api_destination[0]['geometry']['location']['lng'])
        # /!\ Gérer les erreurs pour s'assurer que le transport est bien l'un de ceux compris par google
        if transport in ["driving","walking","bicycling","transit","velib","autolib"]:
            self._transport = transport
        else:
            print("Erreur : mode de transport saisi non reconnu. Valeur saisie : "+str(transport))

    def calculer(self,origine,destination,transport):
        """Fonction qui effectue le calcul pour la classe qui l'utilise, en remplissant au passage les attributs de Origine_Et_Destination."""
        self._set_origine_destination_transport(origine,destination,transport)



class Trajet(Origine_Et_Destination):
    """Caractérise un trajet classique entre un lieu d'origine et un lieu de destination."""

    def __init__(self):
        Origine_Et_Destination.__init__(self)
        self._distance = 0
        self._temps = 0

    # Propriétés

    def _get_distance(self):
        return self._distance
    def _set_distance(self,distance):
        pass
    distance = property(_get_distance,_set_distance)

    def _get_temps(self):
        return self._temps
    def _set_temps(self,temps):
        pass
    temps = property(_get_temps,_set_temps)

    # Méthode

    def calculer(self,origine,destination,transport):
        """Effectue un appel à l'API google pour calculer la distance et la durée du trajet. Remplit également les caractéristiques du trajet."""
        if transport in ["driving", "walking", "bicycling", "transit"]:
            self._set_origine_destination_transport(origine,destination,transport)
            trajet = googlemaps.Client.directions(Origine_Et_Destination.client_google, origin=self._origine, destination=self._destination, mode=self._transport)
            self._distance = trajet[0]['legs'][0]['distance']['value']
            self._temps = trajet[0]['legs'][0]['duration']['value']
        else:
            print("Erreur : mode de transport saisi non reconnu. Valeur saisie : "+str(transport))

    def _definir(self,origine,destination,transport,distance,temps):
        """Au lieu d'effectuer le calcul de distance et de temps, impose des valeurs (dans le cas où elles ont été calculées par un autre moyen)."""
        self._set_origine_destination_transport(origine,destination,transport)
        self._distance = distance
        self._temps = temps

    def afficher_distance(self):
        """Affiche la distance du trajet sous la forme d'une chaîne de caractères."""
        return (str(round(self._distance/100)/10)+" km")

    def afficher_temps(self):
        """Affiche le temps du trajet sous la forme d'une chaîne de caractères."""
        minutes = max(round(self._temps/60),1)
        heures = minutes//60
        minutes = minutes%60
        temps_trajet = str(minutes)+" min"
        if heures>0:
            temps_trajet = str(heures)+"h "+temps_trajet
        return temps_trajet

    def __repr__(self):
        return self._transport+" - distance : "+self.afficher_distance()+" / temps : "+self.afficher_temps()



class Trajet_Lib(Trajet):
    """Caractérise un trajet utilisant un vélib ou une autolib, divisant en particulier le trajet en trois sous-trajets : origine-station / station-station / station-destination."""

    def __init__(self):
        """On ajoute 3 sous-trajets pour représenter les passages à pied et les passages en transport."""
        Trajet.__init__(self)
        self._trajet_initial = Trajet()
        self._trajet_lib = Trajet()
        self._trajet_final = Trajet()

    # Propriétés

    def _get_trajet_initial(self):
        # On utilise la méthode copy pour ne pas donner le trajet par référence afin d'éviter que l'utilisateur ne le modifie.
        return copy.copy(self._trajet_initial)
    def _set_trajet_initial(self,trajet_initial):
        pass
    trajet_initial = property(_get_trajet_initial,_set_trajet_initial)

    def _get_trajet_lib(self):
        # On utilise la méthode copy pour ne pas donner le trajet par référence afin d'éviter que l'utilisateur ne le modifie.
        return copy.copy(self._trajet_lib)
    def _set_trajet_lib(self,trajet_lib):
        pass
    trajet_lib = property(_get_trajet_lib,_set_trajet_lib)

    def _get_trajet_final(self):
        # On utilise la méthode copy pour ne pas donner le trajet par référence afin d'éviter que l'utilisateur ne le modifie.
        return copy.copy(self._trajet_final)
    def _set_trajet_final(self,trajet_final):
        pass
    trajet_final = property(_get_trajet_final,_set_trajet_final)

    # Méthodes

    def calculer(self,origine,destination,transport):
        """Établit la durée et la distance du trajet, en supposant que les sous-trajets sont déjà calculés."""
        if transport in ["velib","autolib"]:
            self._set_origine_destination_transport(origine, destination, transport)
            self._distance = self._trajet_initial._distance + self._trajet_lib._distance + self._trajet_final._distance
            self._temps = self._trajet_initial._temps + self._trajet_lib._temps + self._trajet_final._temps
        else:
            print("Erreur : mode de transport saisi non reconnu. Valeur saisie : " + str(transport))

    #Penser à changer la méthode calculer (en particulier car le calcul des trajets en transport lib doit être fait en parallèle sur les différents trajets).

    def _definir_trajets(self,trajet_initial,trajet_lib,trajet_final):
        """Établit les trois sous-trajets qui définissent ce trajet. On évite de récupérer ces objets par référence car ils peuvent être utilisés pour d'autres trajets."""
        self._tajet_initial = copy.copy(trajet_initial)
        self._trajet_lib = copy.copy(trajet_lib)
        self._trajet_final = copy.copy(trajet_final)



#Pour ne pas faire trop d'appels à l'API google, utiliser le calcul des distances en matrice pour les différentes stations. Par conséquent il faut pouvoir créer les différents trajets lib en même temps.
class Generateur_Trajets_Lib(Origine_Et_Destination):
    """Classe pour générer et travailler sur un ensemble de Trajet_Lib entre deux points, en fonction des stations à proximité. Cette fonction utilise en particulier une fonction de l'API google maps permettant de calculer en même temps des trajets pour un ensemble de points de départs et d'arrivées, ce qui évite d'effectuer un appel à l'API pour chaque paire de stations possibles."""

    def __init__(self):
        Origine_Et_Destination.__init__(self)
        self._client = None
        self._mode = ""
        self._stations_departs = []
        self._stations_arrivees = []

    # Propriétés

    """Faire les propriétés de cette classe"""

    # Méthodes

    def _choix_client(self):
        """Sélectionne le client et le mode de transport adéquat suivant qu'il s'agisse d'un trajet en velib ou en autolib."""
        if self._transport == "velib":
            self._client = opendataparis.Client_Velib()
            self.mode = "bicycling"
        elif self._transport == "autolib":
            self.client = opendataparis.Client_Autolib()
            self.mode="driving"
        else:
            print("Erreur : mode de transport saisi non reconnu. Valeur saisie : " + str(transport))

    def _stations(self,distance_depart,distance_arrivee):
        """Méthode pour obtenir la liste des stations à proximité des points de départ et d'arrivée. Remarquons qu'actuellement le nombre de stations sélectionnées par défaut est définie dans les objets Client_Velib/Client_Autolib. Il faudra alors utiliser le paramètre limite des méthodes cherche_depart et cherche_arrivee si on souhaite pouvoir modifier ce paramètre à l'avenir."""
        self._stations_departs = self._client.cherche_depart(self._coord_origine[0],self._coord_origine[1],distance_depart)
        self._stations_arrivees = self._client.cherche_arrivee(self._coord_destination[0],self._coord_destination[1],distance_arrivee)

    def calculer(self,origine,destination,transport):
        """Méthode pour construire une liste de trajets lib, c'est-à-dire des trajets décomposés en trois sous trajets : origine-station / station-sttion (velib ou autolib) / station-destination."""
        self._set_origine_destination_transport(origine,destination,transport)
        self._choix_client()
        self._stations(1000,1000)
        liste_trajets = []
        nombre_departs = len(self._stations_departs)
        nombre_arrivees = len(self._stations_arrivees)
        # Dans le cas où une des listes de stations est vide (s'il n'y a pas de stations à proximité, ou bien si la méthode stations n'a pas été appelée), on renvoit directement un résultat vide.
        if (nombre_departs==0) | (nombre_arrivees==0):
            return []

        #Trajets lib
        matrice_trajets_lib = []
        resultat_api_trajets_lib = googlemaps.Client.distance_matrix(Origine_Et_Destination.client_google,self._stations_departs,self._stations_arrivees,mode=self.mode)
        for indice_depart in range(0,nombre_departs):
            matrice_trajets_lib.append([])
            for indice_arrivee in range (0,nombre_arrivees):
                matrice_trajets_lib[indice_depart].append([])
                origine_lib = resultat_api_trajets_lib['origin_addresses'][indice_depart]
                destination_lib = resultat_api_trajets_lib['destination_addresses'][indice_arrivee]
                transport_lib = self.mode
                distance_lib = resultat_api_trajets_lib['rows'][indice_depart]['elements'][indice_arrivee]['distance']['value']
                temps_lib = resultat_api_trajets_lib['rows'][indice_depart]['elements'][indice_arrivee]['duration']['value']
                matrice_trajets_lib[indice_depart][indice_arrivee] = Trajet()
                matrice_trajets_lib[indice_depart][indice_arrivee]._definir(origine_lib,destination_lib,transport_lib,distance_lib,temps_lib)

        #Trajets initiaux
        liste_trajets_initiaux = []
        resultat_api_trajets_initiaux = googlemaps.Client.distance_matrix(Origine_Et_Destination.client_google,[self._origine],self._stations_departs,mode='walking')
        for indice_depart in range(0,nombre_departs):
            liste_trajets_initiaux.append([])
            origine_initial = resultat_api_trajets_initiaux['origin_addresses'][0]
            destination_initial = resultat_api_trajets_initiaux['destination_addresses'][indice_depart]
            transport_initial = "walking"
            distance_initial = resultat_api_trajets_initiaux['rows'][0]['elements'][indice_depart]['distance']['value']
            temps_initial = resultat_api_trajets_initiaux['rows'][0]['elements'][indice_depart]['duration']['value']
            liste_trajets_initiaux[indice_depart] = Trajet()
            liste_trajets_initiaux[indice_depart]._definir(origine_initial,destination_initial,transport_initial,distance_initial,temps_initial)

        #Trajets finaux
        liste_trajets_finaux = []
        resultat_api_trajets_finaux = googlemaps.Client.distance_matrix(Origine_Et_Destination.client_google,self._stations_arrivees,[self._destination],mode='walking')
        for indice_arrivee in range(0,nombre_arrivees):
            liste_trajets_finaux.append([])
            origine_final = resultat_api_trajets_finaux['origin_addresses'][indice_arrivee]
            destination_final = resultat_api_trajets_finaux['destination_addresses'][0]
            transport_final = "walking"
            distance_final = resultat_api_trajets_finaux['rows'][indice_arrivee]['elements'][0]['distance']['value']
            temps_final = resultat_api_trajets_finaux['rows'][indice_arrivee]['elements'][0]['duration']['value']
            liste_trajets_finaux[indice_arrivee] = Trajet()
            liste_trajets_finaux[indice_arrivee]._definir(origine_final,destination_final,transport_final,distance_final,temps_final)

        #Construction des trajets entiers
        for indice_depart in range(0,nombre_departs):
            for indice_arrivee in range (0,nombre_arrivees):
                liste_trajets.append(Trajet_Lib())
                liste_trajets[-1]._definir_trajets(liste_trajets_initiaux[indice_depart],matrice_trajets_lib[indice_depart][indice_arrivee],liste_trajets_finaux[indice_arrivee])
                liste_trajets[-1].calculer(self._origine,self._destination,self._transport)
        return liste_trajets

if __name__ == "__main__":

    origine_test = "6 Parvis Notre-Dame Paris"
    #origine_test = (48.9011922, 2.3399989)
    destination_test = "Rue de Rivoli Paris"
    #destination_test = (48.900092, 2.3398062)

    test = Generateur_Trajets_Lib()
    result = test.calculer(origine_test,destination_test,"velib")
    print(result)


    os.system('pause')

