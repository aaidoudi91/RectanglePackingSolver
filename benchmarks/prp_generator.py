""" Générateur d'instances de Perfect Rectangle Packing par découpe guillotine. """

import random
from models.rectangle import Rectangle


class GenerateurPRP:
    """ Génère une instance PRP en découpant un conteneur par guillotine cut équilibré.
        On maintient une liste de pièces à découper. À chaque étape :
            1. On choisit la pièce à couper (la plus grande, pour équilibrer les tailles)
            2. On détermine la direction de coupe (dimension la plus longue en priorité)
            3. On coupe dans une plage restreinte [ratio_min, ratio_max] de la dimension
               pour éviter les tranches dégénérées
        On s'arrête quand on atteint nb_cibles pièces au total. """

    def __init__(self, largeur, hauteur, nb_cibles, seed=None, taille_min=2, ratio_min=0.25):
        self.largeur_conteneur = largeur  # largeur du conteneur
        self.hauteur_conteneur = hauteur  # hauteur du conteneur
        self.nb_cibles = nb_cibles  # nombre de rectangles souhaités
        self.taille_min = taille_min  # dimension minimale d'un côté (évite les rectangles dégénérés)
        self.ratio_min  = ratio_min  # fraction minimale de la coupe (ex: 0.25 → jamais < 25% de la dim)
        self.ratio_max  = 1.0 - ratio_min
        self.rng = random.Random(seed)  # graine aléatoire pour la reproductibilité

        self.rectangles = []
        self._compteur_id = 1
        self._generer()

    def _generer(self):
        """ Lance la génération. """
        self.rectangles  = []
        self._compteur_id = 1

        # Chaque pièce est un tuple (x, y, largeur, hauteur)
        pieces = [(0, 0, self.largeur_conteneur, self.hauteur_conteneur)]

        while len(pieces) + len(self.rectangles) < self.nb_cibles and pieces:
            # Trie les pièces par aire décroissante => coupe toujours la plus grande
            # Introduit un peu d'aléatoire parmi les 3 plus grandes pour éviter
            # un schéma trop systématique
            pieces.sort(key=lambda p: p[2] * p[3], reverse=True)
            k = min(3, len(pieces))
            idx = self.rng.randint(0, k - 1)
            x, y, w, h = pieces.pop(idx)

            # Essaie de découper cette pièce
            coupee = self._couper_piece(x, y, w, h, pieces)

            # Si la pièce est trop petite pour être coupée => feuille
            if not coupee:
                self._creer_feuille(x, y, w, h)

        # Toutes les pièces restantes non découpées deviennent des feuilles
        for x, y, w, h in pieces:
            self._creer_feuille(x, y, w, h)

    def _couper_piece(self, x, y, w, h, pieces):
        """ Tente de découper la pièce (x, y, w, h) et ajoute les deux moitiés à pieces.
        Retourne True si la coupe a eu lieu, False si la pièce est trop petite. """

        peut_vertical   = w >= 2 * self.taille_min
        peut_horizontal = h >= 2 * self.taille_min

        if not peut_vertical and not peut_horizontal:
            return False

        direction = self._choisir_direction(w, h, peut_vertical, peut_horizontal)

        if direction == 'vertical':
            c = self._position_coupe(w)
            # Sous-rect gauche + sous-rect droit
            pieces.append((x,     y, c,     h))
            pieces.append((x + c, y, w - c, h))
        else:
            c = self._position_coupe(h)
            # Sous-rect bas + sous-rect haut
            pieces.append((x, y,     w, c    ))
            pieces.append((x, y + c, w, h - c))

        return True

    def _choisir_direction(self, w, h, peut_vertical, peut_horizontal):
        """ Choisit la direction de coupe. On préfère couper dans la dimension la plus longue (produit des
        formes plus compactes). Si les deux sont égales, on choisit aléatoirement. """
        if peut_vertical and peut_horizontal:
            if w > h:   return 'vertical'
            elif h > w: return 'horizontal'
            else:       return self.rng.choice(['vertical', 'horizontal'])
        return 'vertical' if peut_vertical else 'horizontal'

    def _position_coupe(self, dimension):
        """ Retourne une position de coupe dans la plage [ratio_min, ratio_max] de la dimension.
        Cela évite les tranches dégénérées (ex: 1 pixel de large).
        Fallback sur [taille_min, dimension - taille_min] si la plage ratio est trop étroite. """
        borne_basse = max(self.taille_min, int(dimension * self.ratio_min))
        borne_haute = min(dimension - self.taille_min, int(dimension * self.ratio_max))

        # Fallback si le ratio force des bornes invalides (petites pièces)
        if borne_basse > borne_haute:
            borne_basse = self.taille_min
            borne_haute = dimension - self.taille_min

        return self.rng.randint(borne_basse, borne_haute)

    def _creer_feuille(self, x, y, largeur, hauteur):
        """ Enregistre la pièce finale comme Rectangle placé. """
        rect = Rectangle(largeur=largeur, hauteur=hauteur, id=self._compteur_id)
        rect.x = x
        rect.y = y
        self.rectangles.append(rect)
        self._compteur_id += 1


    # Interface publique
    def obtenir_rectangles(self):
        """ Retourne les rectangles avec leur position d'origine (solution de référence). """
        return self.rectangles

    def obtenir_rectangles_melanges(self):
        """ Retourne des copies des rectangles sans position, dans un ordre aléatoire.
        C'est cette liste qui doit être passée au solveur. """
        copies = [Rectangle(r.largeur, r.hauteur, r.id) for r in self.rectangles]
        self.rng.shuffle(copies)
        return copies

    def verifier_partition(self):
        """ Vérifie que les rectangles couvrent exactement le conteneur sans chevauchement. """
        aire_totale = sum(r.aire() for r in self.rectangles)
        aire_conteneur = self.largeur_conteneur * self.hauteur_conteneur
        if aire_totale != aire_conteneur:
            print(f"Erreur : aire totale {aire_totale} != aire conteneur {aire_conteneur}")
            return False
        for i, r1 in enumerate(self.rectangles):
            for r2 in self.rectangles[i + 1:]:
                if r1.chevauche(r2):
                    print(f"Erreur : chevauchement entre rect {r1.id} et {r2.id}")
                    return False
        return True

    def affiche_info(self):
        """ Affiche un résumé de l'instance générée. """
        aires = sorted([r.aire() for r in self.rectangles], reverse=True)
        print(f"Instance Perfect Rectangle Packing : Conteneur {self.largeur_conteneur}×{self.hauteur_conteneur} - "
              f"{len(self.rectangles)} Rectangles")
        print(f"    Aires : min={min(aires)}, max={max(aires)}, "
              f"moyenne={sum(aires)/len(aires):.1f}")
        print(f"    Dimensions : "
              + ", ".join(f"{r.largeur}×{r.hauteur}" for r in self.rectangles))
