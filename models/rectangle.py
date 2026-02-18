""" Modèle de base représentant un rectangle avec ses dimensions et sa position. """

class Rectangle:
    def __init__(self, largeur, hauteur, id=None):
        self.largeur = largeur
        self.hauteur = hauteur
        self.id = id
        self.x = None
        self.y = None

    def aire(self):
        """ Retourne l'aire du rectangle. """
        return self.largeur * self.hauteur

    def est_place(self):
        """ Vérifie si le rectangle a été placé. """
        return self.x is not None and self.y is not None

    def chevauche(self, autre):
        """ Vérifie si ce rectangle chevauche un autre rectangle. """
        if not self.est_place() or not autre.est_place():
            return False
        if self.x + self.largeur <= autre.x or autre.x + autre.largeur <= self.x:
            return False
        if self.y + self.hauteur <= autre.y or autre.y + autre.hauteur <= self.y:
            return False
        return True

    def reset_position(self):
        """ Réinitialise la position du rectangle. """
        self.x = None
        self.y = None

    def __repr__(self):
        if self.est_place():
            return f"Rectangle(id={self.id}, {self.largeur}×{self.hauteur}, pos=({self.x},{self.y}))"
        return f"Rectangle(id={self.id}, {self.largeur}×{self.hauteur})"
