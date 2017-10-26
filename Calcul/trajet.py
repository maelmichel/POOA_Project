import os
import sys
import copy
import googlemaps
sys.path.insert(0,"../API")
import opendataparis



class _Origine_Et_Destination:

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
        if not isinstance(origine,str):
            raise TypeError("Le lieu d'origine doit être une chaîne de caractères.")
        try:
            result_api_origine = googlemaps.Client.geocode(_Origine_Et_Destination.client_google, origine)
            result_api_origine[0]['formatted_address']
            result_api_origine[0]['geometry']['location']['lat']
            result_api_origine[0]['geometry']['location']['lng']
        except googlemaps.exceptions.TransportError:
            raise googlemaps.exceptions.TransportError("Connexion avec l'API Google impossible. Vérifiez votre connexion internet.")
        except IndexError:
            raise IndexError("Erreur du traitement par l'API Google. Vérifiez les adresses rentrées.")
        else:
            self._origine = result_api_origine[0]['formatted_address']
            self._coord_origine = (result_api_origine[0]['geometry']['location']['lat'],result_api_origine[0]['geometry']['location']['lng'])
        if (self._destination!="") & (self._transport!=""):
            self.calculer()
    origine = property(_get_origine, _set_origine)

    def _get_coord_origine(self):
        return self._coord_origine
    def _set_coord_origine(self, coord):
        if (not isinstance(coord,tuple)) | (len(coord)!=2) | (not isinstance(coord[0],float)) | (not isinstance(coord[0],float)):
            raise TypeError("Les coordonnées d'origine doivent être une paire de nombres flottants.")
        try:
            result_api = googlemaps.Client.reverse_geocode(_Origine_Et_Destination.client_google, coord)
            self._set_origine(result_api[0]['formatted_address'])
        except googlemaps.exceptions.TransportError:
            raise googlemaps.exceptions.TransportError("Connexion avec l'API Google impossible. Vérifiez votre connexion internet.")
        except IndexError:
            raise IndexError("Coordonnées non trouvées.")
    coord_origine = property(_get_coord_origine, _set_coord_origine)

    def _get_destination(self):
        return self._destination
    def _set_destination(self, destination):
        if not isinstance(destination,str):
            raise TypeError("Le lieu de destination doit être une chaîne de caractères.")
        try:
            result_api_destination = googlemaps.Client.geocode(_Origine_Et_Destination.client_google, destination)
            result_api_destination[0]['formatted_address']
            result_api_destination[0]['geometry']['location']['lat']
            result_api_destination[0]['geometry']['location']['lng']
        except googlemaps.exceptions.TransportError:
            raise googlemaps.exceptions.TransportError("Connexion avec l'API Google impossible. Vérifiez votre connexion internet.")
        except IndexError:
            raise IndexError("Erreur du traitement par l'API Google. Vérifiez les adresses rentrées.")
        else:
            self._destination = result_api_destination[0]['formatted_address']
            self._coord_destination = (result_api_destination[0]['geometry']['location']['lat'],result_api_destination[0]['geometry']['location']['lng'])
        if (self._origine != "") & (self._transport != ""):
            self.calculer()
    destination = property(_get_destination, _set_destination)

    def _get_coord_destination(self):
        return self._coord_destination
    def _set_coord_destination(self, coord):
        if (not isinstance(coord,tuple)) | (len(coord)!=2) | (not isinstance(coord[0],float)) | (not isinstance(coord[0],float)):
            raise TypeError("Les coordonnées de destination doivent être une paire de nombres flottants.")
        try:
            result_api = googlemaps.Client.reverse_geocode(_Origine_Et_Destination.client_google, coord)
            self._set_destination(result_api[0]['formatted_address'])
        except googlemaps.exceptions.TransportError:
            raise googlemaps.exceptions.TransportError("Connexion avec l'API Google impossible. Vérifiez votre connexion internet.")
        except IndexError:
            raise IndexError("Coordonnées non trouvées.")
    coord_destination = property(_get_coord_destination, _set_coord_destination)

    def _get_transport(self):
        return self._transport
    def _set_transport(self, transport):
        if not isinstance(transport,str):
            raise TypeError("Le mode de transport doit être une chaîne de caractères.")
        if transport not in ["driving","walking","bicycling","transit","velib","autolib"]:
            raise ValueError("Le mode de transport '" + transport + "' n'est reconnu ni par l'API Google, ni comme un transport velib ou autolib.")
        self._transport = transport
        if (self._origine != "") & (self._destination != ""):
            self.calculer()
    transport = property(_get_transport, _set_transport)

    # Méthodes

    def calculer(self):
        """Fonction pour effectuer les calculs propre à la classe. Ces calculs sont effectués dès modification du lieu d'origine, de destination ou du moyen de transport, afin que les autres attributs de la classe soient toujours à jour."""
        pass



class Trajet(_Origine_Et_Destination):
    """Caractérise un trajet classique entre un lieu d'origine et un lieu de destination."""

    def __init__(self):
        _Origine_Et_Destination.__init__(self)
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

    def calculer(self):

        """Effectue un appel à l'API google pour calculer la distance et la durée du trajet."""

        if self.transport not in ["driving", "walking", "bicycling", "transit"]:
            raise ValueError("Le mode de transport '" + self.transport + "' n'est pas reconnu par l'API Google.")

        try:
            trajet = googlemaps.Client.directions(_Origine_Et_Destination.client_google, origin=self._origine, destination=self._destination, mode=self._transport)
        except googlemaps.exceptions.TransportError:
            raise googlemaps.exceptions.TransportError("Connexion avec l'API Google impossible. Vérifiez votre connexion internet.")
        try:
            trajet[0]['legs'][0]['distance']['value']
            trajet[0]['legs'][0]['duration']['value']
        except IndexError:
            raise IndexError("Erreur du traitement par l'API Google (pas de route trouvée). Vérifiez les adresses rentrées ainsi que votre connexion à internet.")
        else:
            self._distance = trajet[0]['legs'][0]['distance']['value']
            self._temps = trajet[0]['legs'][0]['duration']['value']


    def _definir(self,origine,destination,transport,distance,temps):

        """Au lieu d'effectuer le calcul de distance et de temps, impose des valeurs (dans le cas où elles ont été calculées par un autre moyen)."""

        if not isinstance(transport, str):
            raise TypeError("Le mode de transport doit être une chaîne de caractères.")
        if transport not in ["driving", "walking", "bicycling", "transit", "velib", "autolib"]:
            raise ValueError("Le mode de transport '" + transport + "' n'est reconnu ni par l'API Google, ni comme un transport velib ou autolib.")
        if not isinstance(distance,int):
            raise TypeError("La distance doit être un entier.")
        if not isinstance(temps,int):
            raise TypeError("Le temps doit être un entier.")

        #Pour éviter qu'un appel à l'API soit effecuté, on met temporairement l'attribut transport à ""
        self._transport = ""
        self.origine = origine
        self.destination = destination
        self._transport = transport
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

    def calculer(self):
        """Établit la durée et la distance du trajet, en supposant que les sous-trajets sont déjà calculés."""
        if self.transport not in ["velib","autolib"]:
            raise ValueError("Le mode de transport '" + self.transport + "' n'est pas reconnu comme un transport velib ou autolib.")
        self._distance = self._trajet_initial._distance + self._trajet_lib._distance + self._trajet_final._distance
        self._temps = self._trajet_initial._temps + self._trajet_lib._temps + self._trajet_final._temps

    def _definir_trajets(self,trajet_initial,trajet_lib,trajet_final):
        """Établit les trois sous-trajets qui définissent ce trajet. On évite de récupérer ces objets par référence car ils peuvent être utilisés pour d'autres trajets."""
        if not isinstance(trajet_initial,Trajet):
            raise ValueError("Les sous-trajets d'un trajet en velib ou autolib doivent être de la classe Trajet.")
        if not isinstance(trajet_lib,Trajet):
            raise ValueError("Les sous-trajets d'un trajet en velib ou autolib doivent être de la classe Trajet.")
        if not isinstance(trajet_final,Trajet):
            raise ValueError("Les sous-trajets d'un trajet en velib ou autolib doivent être de la classe Trajet.")
        self._tajet_initial = copy.copy(trajet_initial)
        self._trajet_lib = copy.copy(trajet_lib)
        self._trajet_final = copy.copy(trajet_final)



#Pour ne pas faire trop d'appels à l'API google, utiliser le calcul des distances en matrice pour les différentes stations. Par conséquent il faut pouvoir créer les différents trajets lib en même temps.
class Generateur_Trajets_Lib(_Origine_Et_Destination):
    """Classe pour générer et travailler sur un ensemble de Trajet_Lib entre deux points, en fonction des stations à proximité. Cette fonction utilise en particulier une fonction de l'API google maps permettant de calculer en même temps des trajets pour un ensemble de points de départs et d'arrivées, ce qui évite d'effectuer un appel à l'API pour chaque paire de stations possibles."""

    def __init__(self):
        _Origine_Et_Destination.__init__(self)
        self._client = None
        self._mode = ""
        self._stations_departs = []
        self._stations_arrivees = []

    # Propriétés

    # Le client est volontairement laissé en attribut invisible.

    def _get_mode(self):
        return self._mode
    def _set_mode(self,mode):
        pass
    mode = property(_get_mode,_set_mode)

    def _get_stations_departs(self):
        return self._stations_departs
    def _set_stations_departs(self,stations_departs):
        pass
    stations_departs = property(_get_stations_departs,_set_stations_departs)

    def _get_stations_arrivees(self):
        return self._stations_arrivees
    def _set_stations_arrivees(self,stations_arrivees):
        pass
    stations_arrivees = property(_get_stations_arrivees,_set_stations_arrivees)

    # Méthodes

    def _choix_client(self):
        """Sélectionne le client et le mode de transport adéquat suivant qu'il s'agisse d'un trajet en velib ou en autolib."""
        if self._transport == "velib":
            self._client = opendataparis.Client_Velib()
            self.mode = "bicycling"
        elif self._transport == "autolib":
            self.client = opendataparis.Client_Autolib()
            self.mode = "driving"
        else:
            raise ValueError("Le mode de transport '" + self.transport + "' n'est pas reconnu comme un transport velib ou autolib.")

    def _stations(self,distance_depart,distance_arrivee):
        """Méthode pour obtenir la liste des stations à proximité des points de départ et d'arrivée. Remarquons qu'actuellement le nombre de stations sélectionnées par défaut est définie dans les objets Client_Velib/Client_Autolib. Il faudra alors utiliser le paramètre limite des méthodes cherche_depart et cherche_arrivee si on souhaite pouvoir modifier ce paramètre à l'avenir."""
        if not isinstance(distance_depart,int):
            raise TypeError("Le rayon de recherche pour les stations de départ doit être un entier.")
        if not isinstance(distance_arrivee,int):
            raise TypeError("Le rayon de recherche pour les stations d'arrivée doit être un entier.")
        self._stations_departs = self._client.cherche_depart(self._coord_origine[0],self._coord_origine[1],distance_depart)
        self._stations_arrivees = self._client.cherche_arrivee(self._coord_destination[0],self._coord_destination[1],distance_arrivee)

    def calculer(self):
        """Méthode pour construire une liste de trajets lib, c'est-à-dire des trajets décomposés en trois sous trajets : origine-station / station-sttion (velib ou autolib) / station-destination."""
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
        resultat_api_trajets_lib = googlemaps.Client.distance_matrix(_Origine_Et_Destination.client_google,self._stations_departs,self._stations_arrivees,mode=self.mode)
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
        resultat_api_trajets_initiaux = googlemaps.Client.distance_matrix(_Origine_Et_Destination.client_google,[self._origine],self._stations_departs,mode='walking')
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
        resultat_api_trajets_finaux = googlemaps.Client.distance_matrix(_Origine_Et_Destination.client_google,self._stations_arrivees,[self._destination],mode='walking')
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

    test = Trajet_Lib()
    test.origine = origine_test
    test.destination = destination_test
    test.transport = "velib"
    test._definir_trajets(Trajet(),Trajet(),Trajet())
    print(test)

    """ À faire : 
    - travailler sur la méthode 'calculer' de Generateur_Trajets_Lib pour gérer les erreurs de communication avec l'API, et pour gérer son format de renvoit de réponse (peut-être créer un attribut pour y stocker la réponse ?)
    - faire le travail de gestion des erreurs et de protection des classes sur opendataparis.py
    - faire des commentaires plus propres et bien gérer la clareté du code
    - faire la classe / les méthodes pour la calcul final (choix du trajet)
    - mettre en commun avec les codes des autres"""


    os.system('pause')
