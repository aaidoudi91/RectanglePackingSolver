""" Générateur d'instances de Perfect Rectangle Packing par découpe guillotine. """

import random
from models.rectangle import Rectangle


class GenerateurPRP:
    """ Génère une instance PRP en découpant un conteneur par guillotine cut équilibré.
        On maintient une liste de pièces à découper. À chaque étape, on choisit la pièce à couper, puis on détermine la
        direction de coupe, et on coupe dans une plage restreinte de la dimension pour éviter les tranches dégénérées.
        On s'arrête quand on atteint nb_cibles pièces au total. """

    def __init__(self, largeur, hauteur, nb_cibles, seed, taille_min=2, ratio_min=0.25):
        self.largeur_conteneur = largeur
        self.hauteur_conteneur = hauteur
        self.nb_cibles = nb_cibles  # nombre de rectangles souhaités
        self.taille_min = taille_min  # dimension minimale d'un côté
        self.ratio_min  = ratio_min  # fraction minimale de la coupe (ex.: 0.25 => jamais < 25% de la dim)
        self.ratio_max  = 1.0 - ratio_min
        self.rng = random.Random(seed)  # graine aléatoire pour la reproductibilité
        self.rectangles = []
        self._compteur_id = 1
        self._generer()

    def _choisir_direction(self, largeur, hauteur, peut_vertical, peut_horizontal):
        """ Choisit la direction de coupe. On préfère couper dans la dimension la plus longue (car produit des
        formes plus compactes). Si les deux sont égales, on choisit aléatoirement. """
        if peut_vertical and peut_horizontal:
            if largeur > hauteur: return 'vertical'
            elif hauteur > largeur: return 'horizontal'
            else: return self.rng.choice(['vertical', 'horizontal'])
        return 'vertical' if peut_vertical else 'horizontal'  # une seule coupe possible : limite taille_min atteinte

    def _position_coupe(self, dimension):
        """ Retourne une position de coupe dans la plage [ratio_min, ratio_max] de la dimension.
        Retombe sur [taille_min, dimension - taille_min] si la plage ratio est trop étroite. """
        borne_basse = max(self.taille_min, int(dimension * self.ratio_min))
        borne_haute = min(dimension - self.taille_min, int(dimension * self.ratio_max))

        if borne_basse > borne_haute:  # si le ratio force des bornes invalides (petites pièces)
            borne_basse = self.taille_min
            borne_haute = dimension - self.taille_min

        return self.rng.randint(borne_basse, borne_haute)

    def _couper_piece(self, x, y, largeur, hauteur, pieces):
        """ Tente de découper la pièce (x, y, largeur, hauteur) et ajoute les deux moitiés à pieces.
        Retourne True si la coupe a eu lieu, False si la pièce est trop petite. """
        peut_vertical = largeur >= 2 * self.taille_min
        peut_horizontal = hauteur >= 2 * self.taille_min
        if not peut_vertical and not peut_horizontal:  # trop petit
            return False

        direction = self._choisir_direction(largeur, hauteur, peut_vertical, peut_horizontal)
        if direction == 'vertical':
            c = self._position_coupe(largeur)
            pieces.append((x, y, c, hauteur))
            pieces.append((x+c, y, largeur-c, hauteur))
        else:
            c = self._position_coupe(hauteur)
            pieces.append((x, y, largeur, c))
            pieces.append((x, y+c, largeur, hauteur-c))
        return True

    def _creer_feuille(self, x, y, largeur, hauteur):
        """ Enregistre la pièce finale comme Rectangle placé. """
        rect = Rectangle(largeur=largeur, hauteur=hauteur, id=self._compteur_id)
        rect.x = x
        rect.y = y
        self.rectangles.append(rect)
        self._compteur_id += 1

    def _generer(self):
        """ Lance la génération. """
        self.rectangles  = []
        self._compteur_id = 1

        # Chaque pièce est un tuple (x, y, largeur, hauteur)
        pieces = [(0, 0, self.largeur_conteneur, self.hauteur_conteneur)]

        while len(pieces) + len(self.rectangles) < self.nb_cibles and pieces:
            # Trie les pièces par aire décroissante et coupe une des trois plus grande aléatoirement
            pieces.sort(key=lambda p: p[2] * p[3], reverse=True)
            k = min(3, len(pieces))
            idx = self.rng.randint(0, k - 1)
            x, y, largeur, hauteur = pieces.pop(idx)

            # Essaie de découper cette pièce
            coupee = self._couper_piece(x, y, largeur, hauteur, pieces)
            if not coupee:  # trop petite pour être coupée alors devient une feuille
                self._creer_feuille(x, y, largeur, hauteur)

        # Toutes les pièces restantes non découpées deviennent des feuilles
        for x, y, largeur, hauteur in pieces:
            self._creer_feuille(x, y, largeur, hauteur)

    def obtenir_rectangles_melanges(self):
        """ Retourne des copies des rectangles sans position, dans un ordre aléatoire (pour être passée au solveur). """
        copies = [Rectangle(r.largeur, r.hauteur, r.id) for r in self.rectangles]
        self.rng.shuffle(copies)
        return copies

    def affiche_info(self):
        """ Affiche un résumé de l'instance générée. """
        aires = sorted([r.aire() for r in self.rectangles], reverse=True)
        print(f"Instance Perfect Rectangle Packing : Conteneur {self.largeur_conteneur}×{self.hauteur_conteneur} - "
              f"{len(self.rectangles)} Rectangles")
        print(f"    Aires : min={min(aires)}, max={max(aires)}, " f"moyenne={sum(aires)/len(aires):.1f}")
        print(f"    Dimensions : " + ", ".join(f"{r.largeur}×{r.hauteur}" for r in self.rectangles))
