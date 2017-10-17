import os

class Utilisateur:
    """Classe utilisateur créée à la va-vite pour les tests, en attendant que quelqu'un se penche réellement sur la création d'une telle classe."""

    def __init__(self):
        """Pour l'instant utilisateur défini par son trajet souhaité et sa charge"""
        self.origine = ""
        self.destination = ""
        self.charge = False

    def definir_utilisateur(self):
        self.origine = input("Point de départ : ")
        self.destination = input("Point d'arrivée : ")
        self.charge = input("Charge (laisser vide si aucune charge) : ")

if __name__ == "__main__":

    test = Utilisateur()
    test.definir_utilisateur()