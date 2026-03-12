""" Benchmark de Partridge pour le PRP (Hougardy, 2012). Pour un entier n >= 1, on dispose de i copies du carré i×i
    pour chaque i dans {1, ..., n}. L'objectif est de placer tous ces carrés dans un carré de côté minimal n(n+1)/2. """

import random
from models.rectangle import Rectangle

class BenchmarkPartridge:
    """ Générateur d'instances du benchmark de Partridge. """

    def __init__(self, n, seed=None):
        self.n = n  # i copies du carré i×i pour i=1..n
        self.cote_conteneur = n * (n+1)//2   # côté du conteneur carré
        self.seed = seed
        self.rectangles = self._generer_carres()
        self.aire_totale = self.cote_conteneur ** 2
        self.rng = random.Random(seed)

    def _generer_carres(self):
        """ Génère la liste des carrés : i copies de i×i pour i = 1, ..., n. """
        carres = []
        id_courant = 1
        for i in range(self.n, 0, -1):  # du plus grand (n×n) au plus petit (1×1)
            for _ in range(i):
                carres.append(Rectangle(largeur=i, hauteur=i, id=id_courant))
                id_courant += 1
        return carres

    def obtenir_rectangles_melanges(self):
        """ Retourne des copies des carrés dans un ordre aléatoire (entrée du solveur).
        La seed fournie à la construction garantit la reproductibilité. """
        copies = [Rectangle(rectangle.largeur, rectangle.hauteur, rectangle.id) for rectangle in self.rectangles]
        self.rng.shuffle(copies)
        return copies

    def nombre_rectangles(self):
        """ Retourne le nombre total de carrés : n(n+1)/2. """
        return self.n * (self.n + 1) // 2

    def affiche_info(self):
        """ Affiche les informations de l'instance. """
        print(f"Benchmark Partridge (Hougardy) : n={self.n}")
        print(f"    Conteneur          : {self.cote_conteneur}×{self.cote_conteneur} "
              f"(aire = {self.aire_totale})")
        print(f"    Nombre de carrés   : {self.nombre_rectangles()}")
        print(f"    Composition        : "
              + ", ".join(f"{i}×({i}×{i})" for i in range(1, self.n + 1)))
