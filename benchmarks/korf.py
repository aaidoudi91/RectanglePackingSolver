""" Générateur du benchmark de Korf : carrés consécutifs de 1×1 à n×n. """

from models.rectangle import Rectangle


class BenchmarkKorf:
    def __init__(self, n):
        self.n = n
        self.rectangles = self.genere_carres()
        self.aire_totale = self.calcule_aire_totale()

    def genere_carres(self):
        """ Génère la liste des carrés de 1×1 à n×n. """
        carres = []
        for i in range(1, self.n + 1):
            carres.append(Rectangle(largeur=i, hauteur=i, id=i))
        return carres

    def calcule_aire_totale(self):
        """ Calcule l'aire totale de tous les carrés. """
        return sum(rectangle.aire() for rectangle in self.rectangles)

    def obtenir_rectangles(self):
        """ Retourne la liste des rectangles à emballer. """
        return self.rectangles

    def affiche_info(self):
        """ Affiche les informations du benchmark. """
        print(f"Aire totale des carrés : {self.aire_totale}")
