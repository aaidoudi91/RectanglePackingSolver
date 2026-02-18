""" Implémentation de l'algorithme Bottom-Left. """

from models.rectangle import Rectangle
from solvers.base import SolveurBase


class BottomLeftPacker(SolveurBase):
    """ Prend un conteneur de dimensions fixes et tente d'y placer une liste de rectangles sans chevauchement.
    L'algorithme parcourt chaque rectangle et le positionne à la première position valide trouvée en balayant l'espace
    de bas en haut, puis de gauche à droite. """

    def peut_etre_place(self, rectangle, x, y):
        """ Vérifie si un rectangle peut être placé à la position (x, y) (= ne dépasse pas et ne chevauche pas). """
        if x < 0 or y < 0:
            return False
        if x + rectangle.largeur > self.largeur_conteneur:
            return False
        if y + rectangle.hauteur > self.hauteur_conteneur:
            return False

        # Crée un rectangle temporaire à cette position
        # Optimisable : instancie potentiellement beaucoup d'objets en mémoire
        rect_temp = Rectangle(rectangle.largeur, rectangle.hauteur, rectangle.id)
        rect_temp.x = x
        rect_temp.y = y
        for place in self.rectangles_places:
            if rect_temp.chevauche(place):
                return False

        return True

    def trouve_bottom_left(self, rect):
        """ Trouve la position Bottom-Left pour placer un rectangle.
        Retourne un tuple (x, y) de la position ou None si aucune position n'est trouvée. """
        for y in range(self.hauteur_conteneur):
            for x in range(self.largeur_conteneur):
                if self.peut_etre_place(rect, x, y):
                    return x, y
        return None

    def emballe(self, rectangles, ordre="decroissant"):
        """ Emballe les rectangles en utilisant l'algorithme Bottom-Left.
        Retourne True si tous les rectangles ont été placés, False sinon. """
        self.rectangles_places = []
        for rectangle in rectangles: rectangle.reset_position()

        rects_a_placer = rectangles.copy()

        if ordre == "decroissant":
            rects_a_placer.sort(key=lambda r: r.aire(), reverse=True)
        elif ordre == "croissant":
            rects_a_placer.sort(key=lambda r: r.aire())

        for rect in rects_a_placer:
            position = self.trouve_bottom_left(rect)
            if position is None:
                return False
            rect.x, rect.y = position
            self.rectangles_places.append(rect)

        return True
