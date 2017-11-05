import os
import sys
import copy
import googlemaps
sys.path.insert(0,"../API")
import opendataparis



# Erreurs

class Connexion_API_Error(Exception):
    pass

class Format_API_Error(Exception):
    pass



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
            raise TypeError("origine attend le format str")
        try:
            result_api_origine = googlemaps.Client.geocode(_Origine_Et_Destination.client_google, origine)
            result_api_origine[0]['formatted_address']
            result_api_origine[0]['geometry']['location']['lat']
            result_api_origine[0]['geometry']['location']['lng']
        except googlemaps.exceptions.TransportError:
            raise Connexion_API_Error
        except IndexError:
            raise Format_API_Error
        else:
            self._origine = result_api_origine[0]['formatted_address']
            self._coord_origine = (result_api_origine[0]['geometry']['location']['lat'],result_api_origine[0]['geometry']['location']['lng'])
        if (self._destination!="") & (self._transport!=""):
            self.calculer()
    origine = property(_get_origine, _set_origine)

    def _get_coord_origine(self):
        return self._coord_origine
    def _set_coord_origine(self, coord):
        if (not isinstance(coord,tuple)) | (len(coord)!=2) | (not isinstance(coord[0],float)) | (not isinstance(coord[1],float)):
            raise TypeError("coord_origine attend un tuple de float")
        try:
            result_api = googlemaps.Client.reverse_geocode(_Origine_Et_Destination.client_google, coord)
            self._set_origine(result_api[0]['formatted_address'])
        except googlemaps.exceptions.TransportError:
            raise Connexion_API_Error
        except IndexError:
            raise Format_API_Error
    coord_origine = property(_get_coord_origine, _set_coord_origine)

    def _get_destination(self):
        return self._destination
    def _set_destination(self, destination):
        if not isinstance(destination,str):
            raise TypeError("destination attend le format str")
        try:
            result_api_destination = googlemaps.Client.geocode(_Origine_Et_Destination.client_google, destination)
            result_api_destination[0]['formatted_address']
            result_api_destination[0]['geometry']['location']['lat']
            result_api_destination[0]['geometry']['location']['lng']
        except googlemaps.exceptions.TransportError:
            raise Connexion_API_Error
        except IndexError:
            raise Format_API_Error
        else:
            self._destination = result_api_destination[0]['formatted_address']
            self._coord_destination = (result_api_destination[0]['geometry']['location']['lat'],result_api_destination[0]['geometry']['location']['lng'])
        if (self._origine != "") & (self._transport != ""):
            self.calculer()
    destination = property(_get_destination, _set_destination)

    def _get_coord_destination(self):
        return self._coord_destination
    def _set_coord_destination(self, coord):
        if (not isinstance(coord,tuple)) | (len(coord)!=2) | (not isinstance(coord[0],float)) | (not isinstance(coord[1],float)):
            raise TypeError("coord_destination attend un tuple de float")
        try:
            result_api = googlemaps.Client.reverse_geocode(_Origine_Et_Destination.client_google, coord)
            self._set_destination(result_api[0]['formatted_address'])
        except googlemaps.exceptions.TransportError:
            raise Connexion_API_Error
        except IndexError:
            raise Format_API_Error
    coord_destination = property(_get_coord_destination, _set_coord_destination)

    def _get_transport(self):
        return self._transport
    def _set_transport(self, transport):
        if not isinstance(transport,str):
            raise TypeError("transport attend le format str")
        if transport not in ["driving","walking","bicycling","transit","velib","autolib"]:
            raise ValueError("transport non valide")
        self._transport = transport
        if (self._origine != "") & (self._destination != ""):
            self.calculer()
    transport = property(_get_transport, _set_transport)

    # Méthodes

    def calculer(self):
        """Méthode pour effectuer les calculs propre à la classe. Ces calculs sont effectués dès modification du lieu d'origine, de destination ou du moyen de transport, afin que les autres attributs de la classe soient toujours à jour."""
        pass

    def _definir(self,origine,coord_origine,destination,coord_destination,transport,distance=0,temps=0):
        """Méthode appelée lorsque l'on souhaite définir les attributs de l'objet sans vérification. On appelle cette méthode en particulier lorsque les attributs ont déjà été définis ailleurs. En passant par cette méthode on évite ainsi d'appeler l'API google pour vérifier les adresses et coordonnées, et on évite également de lancer la méthode calculer pour obtenir la valeur des autres attributs."""
        if not isinstance(origine,str):
            raise TypeError("origine attend le format str")
        if (not isinstance(coord_origine,tuple)) | (len(coord_origine)!=2) | (not isinstance(coord_origine[0],float)) | (not isinstance(coord_origine[1],float)):
            raise TypeError("coord_origine attend un tuple de float")
        if not isinstance(destination,str):
            raise TypeError("destination attend le format str")
        if (not isinstance(coord_destination,tuple)) | (len(coord_destination)!=2) | (not isinstance(coord_destination[0],float)) | (not isinstance(coord_destination[1],float)):
            raise TypeError("coord_destination attend un tuple de float")
        if not isinstance(transport,str):
            raise TypeError("transport attend le format str")
        if transport not in ["driving","walking","bicycling","transit","velib","autolib"]:
            raise ValueError("transport non valide")
        self._origine = origine
        self._coord_origine = coord_origine
        self._destination = destination
        self._coord_destination = coord_destination
        self._transport = transport



class Etape(_Origine_Et_Destination):
    """Caractérise une étape d'un trajet, c'est-à-dire une portion de trajet utilisant un seul type de transport : driving, walking, bicycling, transit"""

    def __init__(self):
        _Origine_Et_Destination.__init__(self)
        self._distance = 0
        self._temps = 0

    # Propriétés
    def _set_transport_etape(self,transport):
        #Restriction des modes de transport possibles à ceux reconnus par l'API Google
        if transport not in ["driving","walking","bicycling","transit"]:
            raise ValueError("transport non valide")
        _Origine_Et_Destination._set_transport(self,transport)
    transport = property(_Origine_Et_Destination._get_transport,_set_transport_etape)

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
            raise ValueError("transport non valide")

        try:
            trajet = googlemaps.Client.directions(_Origine_Et_Destination.client_google, origin=self._origine, destination=self._destination, mode=self._transport)
            self._distance = trajet[0]['legs'][0]['distance']['value']
            self._temps = trajet[0]['legs'][0]['duration']['value']
        except googlemaps.exceptions.TransportError:
            raise Connexion_API_Error
        except IndexError:
            raise Format_API_Error

    def _definir(self,origine,coord_origine,destination,coord_destination,transport,distance=0,temps=0):

        """Au lieu d'effectuer le calcul de distance et de temps, impose des valeurs (dans le cas où elles ont été calculées par un autre moyen). On suppose par ailleurs que origine et destination sont des adresses au bon format pour éviter de faire un appel inutile à l'API."""

        _Origine_Et_Destination._definir(self,origine,coord_origine,destination,coord_destination,transport)

        if not isinstance(distance,int):
            raise TypeError("distance attend le format int")
        if not isinstance(temps,int):
            raise TypeError("temps attend le format int")

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



class Trajet(Etape):
    """Caractérise un trajet entier, comportant plusieurs étapes (généralement une étape à pieds au début et à la fin, et une étape utilisant le transport voulu entre les deux). Un trajet aura comme transport transit, velib ou autolib. Remarquons que "transit" peut désigner une étape en transport en commun ou un trajet entier utilisant les transports en commun mais prenant également en compte les étapes à pieds. Cela est dû au fait que l'API Google utilise la même désignation "transit" dans les deux cas, nous gardons donc le format proposé par l'API."""

    _client_velib = opendataparis.Client_Velib()
    _client_autolib = opendataparis.Client_Autolib()

    def __init__(self):
        Etape.__init__(self)
        self._client = None
        self._mode = ""
        self._etapes = []

    #Propriétés
    def _set_transport_trajet(self,transport):
        #Restriction de modes de transport possible à ceux correspondant à un type de trajet.
        if transport not in ["transit", "velib", "autolib"]:
            raise ValueError("transport non valide")
        self._transport = transport
        self._choix_client()
        _Origine_Et_Destination._set_transport(self, transport)
    transport = property(_Origine_Et_Destination._get_transport, _set_transport_trajet)

    def _get_etapes(self):
        return self._etapes
    def _set_etapes(self,etapes):
        pass
    etapes = property(_get_etapes,_set_etapes)

    #Méthodes
    def _choix_client(self):
        if self._transport == "transit":
            self._client = _Origine_Et_Destination.client_google
            self._mode = "transit"
        elif self._transport == "velib":
            self._client = Trajet._client_velib
            self._mode = "bicycling"
        elif self._transport == "autolib":
            self._client = Trajet._client_autolib
            self._mode = "driving"

    def _calculer_lib(self,rayon):

        stations_depart = self._client.cherche_depart(self._coord_origine[0],self._coord_origine[1],rayon,1)
        stations_arrivee = self._client.cherche_arrivee(self._coord_destination[0],self._coord_destination[1],rayon,1)

        if (stations_depart == []) | (stations_arrivee == []):
            #Cas où aucune station n'est trouvé dans un rayon autour du départ ou de l'arrivée
            self._etapes = []

        else:

            etape_initiale = Etape()
            etape_lib = Etape()
            etape_finale = Etape()

            try:
                # Étape intermédiaire en velib ou autolib
                etape_lib.coord_origine = (stations_depart[0][0],stations_depart[0][1])
                etape_lib.coord_destination = (stations_arrivee[0][0],stations_arrivee[0][1])
                etape_lib.transport = self._mode

                # Étape initiale à pieds
                etape_initiale._definir(self.origine,self.coord_origine,etape_lib.origine,etape_lib.coord_origine,"walking")
                etape_initiale.calculer()

                # Étape finale à pieds
                etape_finale._definir(etape_lib.destination,etape_lib.coord_destination,self.destination,self.coord_destination,"walking")
                etape_finale.calculer()

                self._etapes = [etape_initiale,etape_lib,etape_finale]
            except IndexError:
                raise Format_API_Error

    def _calculer_transit(self):
        api_result = googlemaps.Client.directions(_Origine_Et_Destination.client_google, origin=self._origine,destination=self._destination, mode="transit")
        origine_etape = self.origine
        coord_origine_etape = self.coord_origine
        try:
            for etape_api in api_result[0]['legs'][0]['steps']:
                # Récupération dans le résultat de l'API des informations de l'étape
                distance = etape_api['distance']['value']
                temps = etape_api['duration']['value']
                transport = etape_api['travel_mode'].lower()
                if transport == "walking":
                    coord_destination_etape = (etape_api['steps'][-1]['end_location']['lat'],etape_api['steps'][-1]['end_location']['lng'])
                else:
                    coord_destination_etape = (etape_api['transit_details']['arrival_stop']['location']['lat'],etape_api['transit_details']['arrival_stop']['location']['lng'])
                # Création de l'objet Etape correspondant
                etape = Etape()
                etape.coord_destination = coord_destination_etape
                etape._definir(origine_etape,coord_origine_etape,etape.destination,etape.coord_destination,transport,distance,temps)
                self._etapes.append(etape)
                # Préparation pour l'étape suivante
                origine_etape = etape.destination
                coord_origine_etape = etape.coord_destination
        except IndexError:
            raise Format_API_Error

    def calculer(self):
        """"""
        #Contrairement à ce qui était fait dans une précédente version du code, nous ne récupérerons ici qu'une seule statiton de départ et une seule station d'arrivée pour de la part des clients velib et autolib, ce afin de limiter le nombre d'appel à l'API Google et ainsi réduire le temps de traitement. On suppose donc que les clients velib et autolib fournissent déjà les stations les plus appropriées pour le trajet.
        self._choix_client()
        if self._transport == "transit":
            self._calculer_transit()
        elif (self._transport == "velib") | (self._transport == "autolib"):
            self._calculer_lib(2000)

        self._distance = 0
        self._temps = 0
        for etape in self._etapes:
            self._distance += etape.distance
            self._temps += etape.temps


'''

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

# Ceci est une classe utilisée dans une ancienne version du code, elle n'est plus valable à présent mais est conservée au cas où. (lorsque cette classe était active, la classe Trajet à laquelle elle fait référence correspondait à l'actuel classe Etape (à quelques modifications près). Cette classe est maintenant remplacée par l'actuelle classe Trajet.

#Pour ne pas faire trop d'appels à l'API google, utiliser le calcul des distances en matrice pour les différentes stations. Par conséquent il faut pouvoir créer les différents trajets lib en même temps.
class Generateur_Trajets_Lib(_Origine_Et_Destination):
    """Classe pour générer et travailler sur un ensemble de Trajet_Lib entre deux points, en fonction des stations à proximité. Cette fonction utilise en particulier une fonction de l'API google maps permettant de calculer en même temps des trajets pour un ensemble de points de départs et d'arrivées, ce qui évite d'effectuer un appel à l'API pour chaque paire de stations possibles."""

    def __init__(self):
        _Origine_Et_Destination.__init__(self)
        self._client = None
        self._mode = ""
        self._stations_departs = []
        self._stations_arrivees = []
        self._liste_trajets = []

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

    def _get_liste_trajets(self):
        return self._liste_trajets
    def _set_liste_trajets(self,liste_trajets):
        pass
    liste_trajets = property(_get_liste_trajets,_set_liste_trajets)

    # Méthodes

    def _choix_client(self):
        """Sélectionne le client et le mode de transport adéquat suivant qu'il s'agisse d'un trajet en velib ou en autolib."""
        if self._transport == "velib":
            self._client = opendataparis.Client_Velib()
            self._mode = "bicycling"
        elif self._transport == "autolib":
            self._client = opendataparis.Client_Autolib()
            self._mode = "driving"
        else:
            raise ValueError("Le mode de transport '" + self.transport + "' n'est pas reconnu comme un transport velib ou autolib.")

    def _stations(self,distance_depart,distance_arrivee):
        """Méthode pour obtenir la liste des stations à proximité des points de départ et d'arrivée. Remarquons qu'actuellement le nombre de stations sélectionnées par défaut est définie dans les objets Client_Velib/Client_Autolib. Il faudra alors utiliser le paramètre limite des méthodes cherche_depart et cherche_arrivee si on souhaite pouvoir modifier ce paramètre à l'avenir."""
        if not isinstance(distance_depart,int):
            raise TypeError("Le rayon de recherche pour les stations de départ doit être un entier.")
        if not isinstance(distance_arrivee,int):
            raise TypeError("Le rayon de recherche pour les stations d'arrivée doit être un entier.")
        self._stations_departs = self._client.cherche_depart(self._coord_origine[0],self._coord_origine[1],distance_depart,1)
        self._stations_arrivees = self._client.cherche_arrivee(self._coord_destination[0],self._coord_destination[1],distance_arrivee,1)

    def calculer(self):
        """Méthode pour construire une liste de trajets lib, c'est-à-dire des trajets décomposés en trois sous trajets : origine-station / station-sttion (velib ou autolib) / station-destination."""
        self._choix_client()
        self._stations(1000,1000)
        liste_trajets = []
        nombre_departs = len(self._stations_departs)
        nombre_arrivees = len(self._stations_arrivees)
        # Dans le cas où une des listes de stations est vide (s'il n'y a pas de stations à proximité, ou bien si la méthode stations n'a pas été appelée), on renvoit directement un résultat vide.
        if (nombre_departs==0) | (nombre_arrivees==0):
            self._liste_trajets = []
        else:

            #Trajets lib
            matrice_trajets_lib = []
            try:
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
            except googlemaps.exceptions.TransportError:
                raise googlemaps.exceptions.TransportError("Connexion avec l'API Google impossible. Vérifiez votre connexion internet.")
            except IndexError:
                raise IndexError("Erreur du traitement par l'API Google (pas de route trouvée). Vérifiez les adresses rentrées.")

            #Trajets initiaux
            try:
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
            except googlemaps.exceptions.TransportError:
                raise googlemaps.exceptions.TransportError("Connexion avec l'API Google impossible. Vérifiez votre connexion internet.")
            except IndexError:
                raise IndexError("Erreur du traitement par l'API Google (pas de route trouvée). Vérifiez les adresses rentrées.")

            #Trajets finaux
            try:
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
            except googlemaps.exceptions.TransportError:
                raise googlemaps.exceptions.TransportError("Connexion avec l'API Google impossible. Vérifiez votre connexion internet.")
            except IndexError:
                raise IndexError("Erreur du traitement par l'API Google (pas de route trouvée). Vérifiez les adresses rentrées.")

            #Construction des trajets entiers
            for indice_depart in range(0,nombre_departs):
                for indice_arrivee in range (0,nombre_arrivees):
                    liste_trajets.append(Trajet_Lib())
                    liste_trajets[-1]._definir_trajets(liste_trajets_initiaux[indice_depart],matrice_trajets_lib[indice_depart][indice_arrivee],liste_trajets_finaux[indice_arrivee])
                    liste_trajets[-1].origine = self.origine
                    liste_trajets[-1].destination = self.destination
                    liste_trajets[-1].transport = self.transport
            self._liste_trajets = liste_trajets



class Choix_Trajet:

    """Effectue un choix de type de transport en fonction des trajets générés par les données choisies par l'utilisateur."""

    # En attendant que l'on définisse la/les fonction(s) de comparaison des trajets (et les paramètres nécessaires à ces fonctions, comme la météo ou la charge de l'utilisateur), on se contente pour l'instant d'un comparatif au plus rapide (pas très pertinent, mais permet d'avoir une première structure pour le code dans l'attente de mieux).

    def __init__(self):
        self._origine = ""
        self._destination = ""
        self._transports_possibles = {"driving":False, "walking":False, "bicycling":False, "transit":False, "velib":False, "autolib":False}
        self._trajets_generes = {"driving":[], "walking":[], "bicycling":[], "transit":[], "velib":[], "autolib":[]}

    def _get_origine(self):
        return self._origine
    def _set_origine(self,origine):
        pass
    origine = property(_get_origine,_set_origine)

    def _get_destination(self):
        return self._destination
    def _set_destination(self,destination):
        pass
    destination = property(_get_destination,_set_destination)

    def _get_transports_possibles(self):
        return self._transports_possibles
    def _set_transports_possibles(self,transports_possibles):
        pass
    transports_possibles = property(_get_transports_possibles,_set_transports_possibles)

    def _get_trajets_generes(self):
        return self._trajets_generes
    def _set_trajets_generes(self,trajets_generes):
        pass
    trajets_generes = property(_get_trajets_generes,_set_trajets_generes)

    def entrer_donnees_utilisateur(self,origine,destination,driving,walking,bicycling,transit,velib,autolib):
        # En attendant de voir l'interaction avec le front, on considère pour l'instant que ces données sont des paramètres de cette méthode
        if not isinstance(origine,str):
            raise TypeError("Le point d'origine doit être une chaîne de caractères indiquant une adresse.")
        if not isinstance(destination,str):
            raise TypeError("Le point de destination doit être une chaîne de caractères indiquant une adresse.")
        if (not isinstance(driving,bool)) | (not isinstance(walking,bool)) | (not isinstance(bicycling,bool)) | (not isinstance(transit,bool)) | (not isinstance(velib,bool)) | (not isinstance(autolib,bool)):
            raise TypeError("Le choix de chaque transport doit être un booléen.")
        self._origine = origine
        self._destination = destination
        self._transports_possibles["driving"] = driving
        self._transports_possibles["walking"] = walking
        self._transports_possibles["bicycling"] = bicycling
        self._transports_possibles["transit"] = transit
        self._transports_possibles["velib"] = velib
        self._transports_possibles["autolib"] = autolib

    def calculer_trajets(self):
        """Calcule les trajets possibles d'après les choix de l'utilisateur."""
        for transport in ["driving","walking","bicycling","transit"]:
            if self._transports_possibles[transport]:
                trajet = Trajet()
                trajet.origine = self.origine
                trajet.destination = self.destination
                trajet.transport = transport
                self._trajets_generes[transport] = [trajet]
        for transport_lib in ["velib","autolib"]:
            if self._transports_possibles[transport_lib]:
                generateur_trajets = Generateur_Trajets_Lib()
                generateur_trajets.origine = self.origine
                generateur_trajets.destination = self.destination
                generateur_trajets.transport = transport_lib
                self._trajets_generes[transport_lib] = generateur_trajets.liste_trajets

    def choix(self):
        """Fait le choix du meilleur trajet et retourne le résultat."""
        pass

    def __repr__(self):
        """On représente les meilleurs trajets trouvés."""
        repr_string = ""
        for transport in ["driving","walking","bicycling","transit","velib","autolib"]:
            if not self._transports_possibles[transport]:
                continue
            repr_string += transport + " : "
            for trajet in self._trajets_generes[transport]:
                repr_string += trajet.afficher_distance()+" / "+trajet.afficher_temps() + " ; "
            repr_string += "\n"
        return repr_string

'''


if __name__ == "__main__":

    origine_test = "6 Parvis Notre-Dame Paris"
    coord_origine_test = (48.9011922, 2.3399989)
    destination_test = "Rue de Rivoli Paris"
    coord_destination_test = (48.900092, 2.3398062)

    test = Trajet()
    test.origine = origine_test
    test.destination = destination_test
    test.transport = "transit"
    print(test.etapes)
    print(test)

    """ À faire : 
    - faire des commentaires plus propres et bien gérer la clareté du code
    - voir ce que l'on peut extraire d'un trajet en transport en commun
    - faire la classe / les méthodes pour la calcul final (choix du trajet)
    - mieux gérer les erreurs afin de les utiliser plus facilement lors du traitement
    - mettre en commun avec les codes des autres"""


    os.system('pause')

