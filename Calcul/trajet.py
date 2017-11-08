import os
import sys
import googlemaps
import datetime
from copy import copy, deepcopy
sys.path.insert(0, "../API")
import opendataparis
from CYA_meteo import Meteo


# Erreurs

class Connexion_API_Error(Exception):
    """Erreur soulevée lorsque la connexion une API (google, velib ou autolib) n'est pas possible, par exemple si l'utilisateur n'est pas connecté à internet ou encore si l'API rencontre un problème."""
    pass

class Format_API_Error(Exception):
    """Erreur renvoyé lorsque la réponse de l'API n'est pas au format attendu. Cela peut en particulier se produire si les données envoyées à celle-ci ne sont pas comprises, par exemple si une chaîne de caractère n'est pas reconnue comme une adresse."""
    pass

class Aucun_Transport_Trouve(Exception):
    """Erreur levé lorsque les conditions imposées par l'utilisateur ne permettent pas de trouver le moindre trajet possible."""
    pass



# Classes

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
        """Ce setter assure que :
            - la chaîne de caractères désignant l'adresse prend comme valeur l'adresse donnée par Google ;
            - les coordonnées soient mises à jour pour correspondre à cette adresse ;
            - un appel à la méthode calculé est effectué pour que les autres attributs qui peuvent être influencés par ce changement soient mis à jour (comme la distance ou le temps d'un trajet). Cet appel n'est effectué que si la destination et de transport sont également définis."""
        if not isinstance(origine,str):
            raise TypeError("origine attend le format str")
        try:
            result_api_origine = googlemaps.Client.geocode(_Origine_Et_Destination.client_google, origine)
            # Les trois lignes suivantes servent à lever une erreur si ces indexes ne sont pas définis
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
        """Si ce setter est appelé, il récupère auprès le l'API Google l'adresse correspondant aux coordonnées fournies, pour ensuite appeler le setter de l'adresse pour l'adresse trouvée."""
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
        """Ce setter fonctionne de la même manière que _set_origine"""
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
        """Ce setter fonctionne de la même manière que _set_coord_origine"""
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
        """Ce setter vérifie que le transport fourni corrspond bien à un transport reconnu par les objets définis plus loin. De plus, si l'origine et la destination sont définies, fait appel à la méthode calculer pour modifier les autres attributs pouvant dépendre de ce changement (comme la distance ou le temps du trajet)."""
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
        """Méthode pour effectuer les calculs propre à la classe. Ces calculs sont effectués dès modification du lieu d'origine, de destination ou du moyen de transport, afin que les autres attributs de la classe soient toujours à jour. Ici il n'y a pas d'autres attributs qui en dépendent, la méthode calculer ne fait donc rien."""
        pass

    def _definir(self,origine,coord_origine,destination,coord_destination,transport,distance=0,temps=0):
        """Méthode appelée lorsque l'on souhaite définir les attributs de l'objet sans vérification. On appelle cette méthode en particulier lorsque les attributs ont déjà été culculés ailleurs. En passant par cette méthode on évite ainsi d'appeler l'API google pour vérifier les adresses et coordonnées, et on évite également de lancer la méthode calculer pour obtenir la valeur des autres attributs."""
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
    """Caractérise une étape d'un trajet, c'est-à-dire une portion de trajet utilisant un seul type de transport : "driving", "walking", "bicycling", "transit", soit respectivement une portion de trajet en voiture, à pieds, en vélo ou en transports en commun."""

    def __init__(self):
        _Origine_Et_Destination.__init__(self)
        self._distance = 0
        self._temps = 0

    # Propriétés

    def _set_transport_etape(self,transport):
        # Modification du setter de transport pour restreindre les modes de transport possibles à ceux reconnus par l'API Google
        if transport not in ["driving","walking","bicycling","transit"]:
            raise ValueError("transport non valide")
        _Origine_Et_Destination._set_transport(self,transport)
    transport = property(_Origine_Et_Destination._get_transport,_set_transport_etape)

    def _get_distance(self):
        return self._distance
    def _set_distance(self,distance):
        """ Setter en lecture seule. """
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

        """Au lieu d'effectuer le calcul de distance et de temps, impose des valeurs (dans le cas où elles ont été calculées par un autre moyen). On suppose par ailleurs que origine et destination sont des adresses au bon format (c'est-à-dire qu'elles ont déjà été vérifiée précédemment) pour éviter de faire un appel inutile à l'API."""

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
        """Représentation utilisée pendant la phase de développement."""
        return self._transport+" - distance : "+self.afficher_distance()+" / temps : "+self.afficher_temps()



class Trajet(Etape):
    """Caractérise un trajet entier, comportant plusieurs étapes (généralement une étape à pieds au début et à la fin, et une étape utilisant le transport voulu entre les deux). Un trajet aura comme transport walking, transit, velib ou autolib. Remarquons que "transit" peut désigner une étape en transport en commun ou un trajet entier utilisant les transports en commun mais prenant également en compte les étapes à pieds. Cela est dû au fait que l'API Google utilise la même désignation "transit" dans les deux cas, nous gardons donc le format proposé par l'API."""

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
        if transport not in ["walking","transit", "velib", "autolib"]:
            raise ValueError("transport non valide")
        self._transport = transport
        self._choix_client()
        _Origine_Et_Destination._set_transport(self, transport)
    transport = property(_Origine_Et_Destination._get_transport, _set_transport_trajet)

    def _get_etapes(self):
        # Les tableaux étant traité par référence, on renvoit une copie du tableau pour éviter que le getter ne permette à l'utilisateur de modifier indirectement le contenu de ce tableau. De plus, puisque les éléments de ce tableau sont eux-même traités par références (il s'agit d'objets Etape), on effectue un deepcopy pour que ces éléments soient eux-même copiés.
        return deepcopy(self._etapes)
    def _set_etapes(self,etapes):
        pass
    etapes = property(_get_etapes,_set_etapes)

    # _client et _mode sont laissés théoriquement interdits

    #Méthodes

    def _choix_client(self):
        """ Effectue le choix du client utilisé, ainsi que du mode de transport utilisé durant les étapes qui ne sont pas à pieds (par exemple un trajet 'velib' sera associé au mode 'bicycling'). """
        if (self._transport == "walking") | (self._transport == "transit"):
            self._client = _Origine_Et_Destination.client_google
            self._mode = self._transport
        elif self._transport == "velib":
            self._client = Trajet._client_velib
            self._mode = "bicycling"
        elif self._transport == "autolib":
            self._client = Trajet._client_autolib
            self._mode = "driving"

    def _calculer_lib(self,rayon):
        """Méthode calculer utilisée dans le cas d'un trajet velib ou autolib. Construit les trois étapes du trajet (à pieds - en transport - à pieds) sauf si aucune station de départ ou d'arrivée n'est trouvée."""

        stations_depart = self._client.cherche_depart(self._coord_origine[0],self._coord_origine[1],rayon,1)
        stations_arrivee = self._client.cherche_arrivee(self._coord_destination[0],self._coord_destination[1],rayon,1)

        if (stations_depart == []) | (stations_arrivee == []):
            #Cas où aucune station n'est trouvée dans un rayon autour du départ ou de l'arrivée
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
        """ Méthode calculer utilisée lorsqu'il s'agit d'un trajet 'transit'. Récupère les différentes étapes ainsi que les calculs de distance et de temps directement dans la réponse de l'API Google."""
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

    def _calculer_walking(self):
        """ Méthode calculer utilisée pour un trajet à pieds : construit simplement une étape à pieds. """
        etape = Etape()
        etape._definir(self.origine,self.coord_origine,self.destination,self.coord_destination,'walking')
        etape.calculer()
        self._etapes = [etape]

    def calculer(self):
        """ Fait appel à la fonction calculer appropriée au type de trajet. Calcule ensuite la distance et le temps total. """
        self._choix_client()
        if self._transport == "walking":
            self._calculer_walking()
        elif self._transport == "transit":
            self._calculer_transit()
        elif (self._transport == "velib") | (self._transport == "autolib"):
            self._calculer_lib(2000)

        self._distance = 0
        self._temps = 0
        for etape in self._etapes:
            self._distance += etape.distance
            self._temps += etape.temps



class Choix_Trajet(_Origine_Et_Destination):

    """Effectue un choix de type de transport en fonction des trajets générés par les données choisies par l'utilisateur."""

    @staticmethod
    def _cout_trajet(trajet,niveau_pluie):
        """Fonction statique de score permettant d'associer à un trajet un coût (mesuré en temps) pour pouvoir les comparer entre eux. Cette fonction prend en particulier en compte le niveau de pluie et la durée du trajet exposé à la pluie. Nous utilisons ici une fonction relativement basique. Bien entendu, la précision de l'application reposerait en partie sur le choix d'une fonction plus précise, comportant plus de paramètres et utilisant un modèle plus complexe."""
        coefficient_surcout = {0: 0.2, 1: 0.5, 2: 1}
        valeur_du_trajet = trajet.temps
        for etape in trajet.etapes:
            if etape.transport in ['walking','bicycling']:
                valeur_du_trajet += coefficient_surcout[niveau_pluie] * etape.temps
        return valeur_du_trajet

    def __init__(self):
        _Origine_Et_Destination.__init__(self)
        self._considerer_meteo = False
        self._charge_utilisateur = 0
        self._transports_possibles = {"walking":False, "transit":False, "velib":False, "autolib":False}
        self._trajets_generes = {"walking":None, "transit":None, "velib":None, "autolib":None}

    # Propriétés

    def _get_transport(self):
        """L'attribut transport n'étant pas utile à cette classe, on rend une chaine vide"""
        return ""
    def _set_transport(self, transport):
        """L'attribut transport n'étant pas utile à cette classe, on ne le modifie pas"""
        pass
    transport = property(_get_transport,_set_transport)

    def _get_considerer_meteo(self):
        return self._considerer_meteo
    def _set_considerer_meteo(self,meteo):
        pass
    considerer_meteo = property(_get_considerer_meteo,_set_considerer_meteo)

    def _get_charge_utilisateur(self):
        return self._charge_utilisateur
    def _set_charge_utilisateur(self,charge):
        pass
    charge_utilisateur = property(_get_charge_utilisateur,_set_charge_utilisateur)

    def _get_transports_possibles(self):
        # De même que précédemment, on effectue une copie du tableau (traité par références) pour éviter une modification indirecte par l'utilisateur.
        return copy(self._transports_possibles)
    def _set_transports_possibles(self,transports_possibles):
        pass
    transports_possibles = property(_get_transports_possibles,_set_transports_possibles)

    def _get_trajets_generes(self):
        # De même que précédemment, on effectue une copie du tableau (traité par références) pour éviter une modification indirecte par l'utilisateur.
        return copy(self._trajets_generes)
    def _set_trajets_generes(self,trajets_generes):
        pass
    trajets_generes = property(_get_trajets_generes,_set_trajets_generes)

    # Méthodes

    def entrer_donnees_utilisateur(self,origine,destination,considerer_meteo,charge_utilisateur,walking,transit,velib,autolib):
        # Récupère les données choisies par l'utilisateur au travers de l'UI.
        if not isinstance(origine,str):
            raise TypeError("origine attend le format str")
        if not isinstance(destination,str):
            raise TypeError("destination attend le format str")
        if (not isinstance(walking,bool)) | (not isinstance(transit,bool)) | (not isinstance(velib,bool)) | (not isinstance(autolib,bool)):
            raise TypeError("les choix de transport attendent le format bool")
        if not isinstance(considerer_meteo,bool):
            raise TypeError("le choix de meteo attend le format bool")
        if not isinstance(charge_utilisateur,int):
            raise TypeError("la charge utilisateur attend le format int")
        self.origine = origine
        self.destination = destination
        self._considerer_meteo = considerer_meteo
        self._charge_utilisateur = charge_utilisateur
        self._transports_possibles["walking"] = walking
        self._transports_possibles["transit"] = transit
        self._transports_possibles["velib"] = velib
        self._transports_possibles["autolib"] = autolib

    def calculer(self):
        """Calcule les trajets possibles d'après les choix de l'utilisateur. Le niveau de charge ainsi que les transports choisis peuvent interdire certains trajets."""
        charge_maximale = {"walking": 1, "transit": 2, "velib": 1, "autolib": 3}
        for transport in ["walking","transit","velib","autolib"]:
            if self._transports_possibles[transport] & (self._charge_utilisateur <= charge_maximale[transport]):
                trajet = Trajet()
                trajet._definir(self.origine,self.coord_origine,self.destination,self.coord_destination,transport)
                trajet.calculer()
                if trajet.etapes != []:
                    self._trajets_generes[transport] = trajet

        if self._trajets_generes == {"walking":None, "transit":None, "velib":None, "autolib":None}:
            raise Aucun_Transport_Trouve

    def choix(self):
        """Fait le choix du meilleur trajet et retourne le résultat."""
        niveau_pluie = Meteo().seuil_pluie(datetime.datetime.now())
        meilleur_trajet = None
        meilleur_score = 0
        # Vérification parmi les différents trajets trouvés (non nuls) celui qui a le score le plus faible (en privilégiant les premiers transports de la liste)
        for transport in ["walking","transit","velib","autolib"]:
            if (self._transports_possibles[transport]) & (self._trajets_generes[transport]!=None):
                if meilleur_trajet==None:
                    meilleur_trajet = self._trajets_generes[transport]
                    if self._considerer_meteo:
                        meilleur_score = Choix_Trajet._cout_trajet(self._trajets_generes[transport], niveau_pluie)
                    else:
                        meilleur_score = self._trajets_generes[transport].temps
                else:
                    if self._considerer_meteo:
                        score = Choix_Trajet._cout_trajet(self._trajets_generes[transport], niveau_pluie)
                    else:
                        score = self._trajets_generes[transport].temps
                    if score<meilleur_score:
                        # En cas d'égalité des score, on privilégie walking, puis transit, puis velib, puis autolib
                        meilleur_trajet = self._trajets_generes[transport]
                        meilleur_score = score

        return meilleur_trajet

    def __repr__(self):
        """On représente les trajets trouvés."""
        repr_string = ""
        for transport in ["walking","transit","velib","autolib"]:
            if (not self._transports_possibles[transport]) | (self._trajets_generes[transport]==None):
                continue
            trajet = self._trajets_generes[transport]
            repr_string += transport + " : " + trajet.afficher_distance() + " / " + trajet.afficher_temps() + "\n"
        return repr_string



if __name__ == "__main__":

    origine_test = "CentraleSupelec"
    destination_test = "Dernier bar avant la fin du monde"

    test = Choix_Trajet()
    test.entrer_donnees_utilisateur(origine_test,destination_test,False,0,True,True,True,True)
    test.calculer()

    meilleur = test.choix()
    print(meilleur)
    print(meilleur.etapes)




    os.system('pause')
