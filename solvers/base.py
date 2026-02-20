""" Classe abstraite commune à tous les solveurs de Rectangle Packing. """

from abc import ABC, abstractmethod


class SolveurBase(ABC):
    def __init__(self, largeur, hauteur):
        self.largeur_conteneur = largeur
        self.hauteur_conteneur = hauteur
        self.rectangles_places = []

    @abstractmethod
    def emballe(self, rectangles):
        """ Tente de placer tous les rectangles dans le conteneur. Retourne True si tous les rectangles sont placés. """
        pass

    def peut_etre_place(self, rectangle, x, y):
        """ Vérifie si un rectangle peut être placé à la position (x, y) (=> ne dépasse pas et ne chevauche pas). """
        if x < 0 or y < 0:
            return False
        if x + rectangle.largeur > self.largeur_conteneur:
            return False
        if y + rectangle.hauteur > self.hauteur_conteneur:
            return False

        for place in self.rectangles_places:
            if (x + rectangle.largeur <= place.x or place.x + place.largeur <= x or y + rectangle.hauteur <= place.y or
                    place.y + place.hauteur <= y) : continue
            else : return False

        return True

    def hauteur_max(self):
        """ Retourne la hauteur maximale utilisée. """
        if not self.rectangles_places:
            return 0
        return max(r.y + r.hauteur for r in self.rectangles_places)

    def largeur_max(self):
        """ Retourne la largeur maximale utilisée. """
        if not self.rectangles_places:
            return 0
        return max(r.x + r.largeur for r in self.rectangles_places)

    def espace_perdu(self):
        """ Calcule l'espace perdu dans le conteneur. """
        aire_utilisee = sum(r.aire() for r in self.rectangles_places)
        aire_conteneur = self.largeur_conteneur * self.hauteur_conteneur
        return aire_conteneur - aire_utilisee
