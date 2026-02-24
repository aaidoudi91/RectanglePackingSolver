""" Implémentation du DFS avec backtracking optimisé. """

from solvers.base import SolveurBase

class DFS(SolveurBase):
    """ Résout le Rectangle Packing par une recherche en profondeur avec backtracking.
    Garantit une solution si elle existe, au prix d'une complexité exponentielle dans le pire cas.
    Améliorations implémentées :
        1. Brisure de symétrie    : force le premier rectangle dans le quadrant supérieur gauche.
        2. Élagage par aire       : coupe si l'aire restante dépasse l'espace libre.
        3. Bounding functions     : relaxation 1D de Korf (horizontale + verticale) via algo Martello & Toth.
        4. Incrémentalisme        : mise à jour de l'état du conteneur (évitent de re-calculer l'état global). """

    def __init__(self, largeur, hauteur):
        super().__init__(largeur, hauteur)
        self.noeuds_explores = 0
        self.noeuds_elagages_aire = 0
        self.noeuds_elagages_sym = 0
        self.noeuds_elagages_bf = 0

        self.aire_libre_courante = largeur * hauteur
        self.capacites_h = [largeur] * hauteur
        self.capacites_v = [hauteur] * largeur


    # 1. Vérification / Génération de positions
    def _meilleur_bloquant(self, x, y, w, h):
        """ Retourne la coordonnée x de fin du meilleur bloqueur, ou None. Au lieu de s'arrêter au premier rectangle qui
        chevauche, on cherche celui qui s'étend le plus loin vers la droite pour maximiser notre saut. """
        meilleur_saut = -1
        for place in self.rectangles_places:
            # Condition de chevauchement sur X : les intervalles [x, x+w[ et [place.x, place.x+largeur[ se croisent
            if (x < place.x + place.largeur and x + w > place.x and
            # Condition de chevauchement sur Y : les intervalles [y, y+h[ et [place.y, place.y+hauteur[ se croisent
                y < place.y + place.hauteur and y + h > place.y):
                if place.x + place.largeur > meilleur_saut:
                    meilleur_saut = place.x + place.largeur
        return meilleur_saut if meilleur_saut != -1 else None

    def _positions_candidates_generateur(self, rect):
        """ Génère les positions candidates à la volée (yield) pour économiser la mémoire. """
        limite_x = self.largeur_conteneur - rect.largeur
        limite_y = self.hauteur_conteneur - rect.hauteur

        # Élagage par brisure de symétrie
        if not self.rectangles_places:  # uniquement pour le 1er rectangle
            limite_x_sym = limite_x // 2  # moitié gauche seulement
            limite_y_sym = limite_y // 2  # moitié basse seulement

            # Calcul du nombre de positions ignorées par la symétrie (pour stats)
            coupes_x = (limite_x - limite_x_sym) * (limite_y + 1)
            coupes_y = (limite_y - limite_y_sym) * (limite_x_sym + 1)
            self.noeuds_elagages_sym += (coupes_x + coupes_y)

            limite_x = limite_x_sym
            limite_y = limite_y_sym

        for y in range(limite_y + 1):
            x = 0
            while x <= limite_x:
                saut = self._meilleur_bloquant(x, y, rect.largeur, rect.hauteur)
                if saut is None:
                    yield x, y  # position libre proposée
                    x += 1
                else:
                    # Saut maximal : on avance x directement à la fin du plus grand bloqueur
                    x = saut


    # 2. Gestion de l'état incrémental
    def _placer(self, rect, x, y):
        """ Place le rectangle et met à jour les états incrémentaux du conteneur. États lus par les bounding functions
        sans re-calcul. """
        rect.x = x
        rect.y = y
        self.rectangles_places.append(rect)
        self.aire_libre_courante -= rect.aire()  # soustrait l'aire du rectangle de l'espace libre global

        # Pour chaque rangée y (puis x) que le rectangle occupe (de y à y+hauteur/de x à x+largeur),
        # on réduit la capacité horizontale/verticale disponible de sa largeur/hauteur.
        for cy in range(y, y + rect.hauteur):
            self.capacites_h[cy] -= rect.largeur
        for cx in range(x, x + rect.largeur):
            self.capacites_v[cx] -= rect.hauteur

    def _enlever(self, rect):
        """ Retire le rectangle et restaure les états incrémentaux. Appelée lors du backtracking. """
        self.rectangles_places.pop()
        self.aire_libre_courante += rect.aire()  # restitue l'aire à l'espace libre global

        # Restaure la capacité horizontale/verticale de chaque rangée occupée
        for cy in range(rect.y, rect.y + rect.hauteur):
            self.capacites_h[cy] += rect.largeur
        for cx in range(rect.x, rect.x + rect.largeur):
            self.capacites_v[cx] += rect.hauteur

        rect.reset_position()


    #  3. Bounding Functions de Korf (Martello & Toth)
    @staticmethod
    def _calcule_items(rects, index, orientation):
        """ Construit le vecteur des items en utilisant l'index pour éviter la copie de liste. """
        items = {}
        # On parcourt uniquement de l'index courant jusqu'à la fin (rectangles non placés)
        for i in range(index, len(rects)):
            r = rects[i]
            if orientation == 'horizontale':
                # Un rect de largeur L et hauteur H génère H tranches de largeur L
                taille, nb = r.largeur, r.hauteur
            else:
                # Un rect de largeur L et hauteur H génère L tranches de hauteur H
                taille, nb = r.hauteur, r.largeur
            items[taille] = items.get(taille, 0) + taille * nb
        return items

    @staticmethod
    def _borne_martello_toth(capacites, items, taille_max):
        """ Calcule une borne inférieure sur le gaspillage. """
        bins = {}
        for cap in capacites:
            if cap > 0:
                # bins[c] = aire totale disponible dans toutes les rangées de capacité libre c
                bins[cap] = bins.get(cap, 0) + cap

        gaspillage = 0
        carryover = 0

        for taille in range(1, taille_max + 1):
            bin_area = bins.get(taille, 0)  # espace dans les bins de capacité exacte = taille
            item_area = items.get(taille, 0)  # aire des items de taille exacte = taille
            total_items = carryover + item_area

            if bin_area > total_items:  # surplus de capacité
                gaspillage += bin_area - total_items
                carryover = 0
            else:  # surplus d'items
                carryover = total_items - bin_area

        return gaspillage

    def _bounding_function(self, rects, index, aire_restante):
        """ Applique les bounding functions de Korf sans cloner de listes. 
        Se lit tel que : m'espace disponible dans le conteneur (aire_libre_courante) doit pouvoir accueillir à la fois 
        l'aire des rectangles restants (aire_restante) et l'espace qui sera forcément gaspillé (waste). Si ce n'est pas 
        le cas, la solution est impossible."""
        # Direction horizontale : les bins sont les rangées, les items sont des tranches de largeur
        items_h = self._calcule_items(rects, index, 'horizontale')
        waste_h = self._borne_martello_toth(self.capacites_h, items_h, self.largeur_conteneur)
        if aire_restante + waste_h > self.aire_libre_courante:
            return True  # élagage

        # Direction verticale : les bins sont les colonnes, les items sont des tranches de hauteur
        items_v = self._calcule_items(rects, index, 'verticale')
        waste_v = self._borne_martello_toth(self.capacites_v, items_v, self.hauteur_conteneur)
        if aire_restante + waste_v > self.aire_libre_courante:
            return True  # élagage

        return False

    # 4. DFS
    def _dfs(self, rects, index, aire_restante):
        """ Fonction récursive du DFS avec backtracking pilotée purement par index. """
        self.noeuds_explores += 1

        # Cas de base
        if index == len(rects):
            return True

        # Élagage par aire
        if aire_restante > self.aire_libre_courante:
            self.noeuds_elagages_aire += 1
            return False

        # Élagage par bounding function de Korf (on passe la liste complète et l'index actuel)
        if self._bounding_function(rects, index, aire_restante):
            self.noeuds_elagages_bf += 1
            return False

        rect_courant = rects[index]
        nouvelle_aire_restante = aire_restante - rect_courant.aire()

        # Exploration via le générateur
        for x, y in self._positions_candidates_generateur(rect_courant):

            self._placer(rect_courant, x, y)

            if self._dfs(rects, index + 1, nouvelle_aire_restante):
                return True

            self._enlever(rect_courant)

        return False

    #  5. Interface publique
    def emballe(self, rectangles, ordre="decroissant"):
        """ Emballe les rectangles en utilisant le DFS. """
        self.rectangles_places = []
        self.noeuds_explores = 0
        self.noeuds_elagages_aire = 0
        self.noeuds_elagages_sym = 0
        self.noeuds_elagages_bf = 0

        self.aire_libre_courante = self.largeur_conteneur * self.hauteur_conteneur
        self.capacites_h = [self.largeur_conteneur] * self.hauteur_conteneur
        self.capacites_v = [self.hauteur_conteneur] * self.largeur_conteneur

        for rectangle in rectangles:
            rectangle.reset_position()

        rects_a_placer = rectangles.copy()

        if ordre == "decroissant":
            rects_a_placer.sort(key=lambda r: r.aire(), reverse=True)
        elif ordre == "croissant":
            rects_a_placer.sort(key=lambda r: r.aire())

        aire_totale = sum(r.aire() for r in rects_a_placer)

        return self._dfs(rects_a_placer, 0, aire_totale)

    def affiche_stats(self):
        """ Affiche les statistiques de la recherche. """
        total_elagages = self.noeuds_elagages_aire + self.noeuds_elagages_sym + self.noeuds_elagages_bf
        print(f"        Noeuds explorés      : {self.noeuds_explores}")
        print(f"        Élagages aire        : {self.noeuds_elagages_aire}")
        print(f"        Élagages symétrie    : {self.noeuds_elagages_sym}")
        print(f"        Élagages bounding f. : {self.noeuds_elagages_bf}")
        if self.noeuds_explores > 0:
            print(f"        Taux d'élagage      : {100 * total_elagages / self.noeuds_explores:.1f}%")
