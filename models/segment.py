""" Modèle des segments de la skyline. """

class Segment:
    """ Représente un segment horizontal de la skyline.
    Un segment (x, largeur, hauteur) signifie que la zone [x, x+largeur[ est remplie jusqu'à 'hauteur'. """

    # Empêche la création d'un dictionnaire par instance pour économiser la RAM lors du DFS.
    __slots__ = ('x', 'largeur', 'hauteur')

    def __init__(self, x, largeur, hauteur):
        self.x = x
        self.largeur = largeur
        self.hauteur = hauteur

    def x_fin(self):
        return self.x + self.largeur
