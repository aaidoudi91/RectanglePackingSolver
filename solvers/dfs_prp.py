""" DFS avec backtracking pour le Perfect Rectangle Packing. """

from solvers.base import SolveurBase
from utils.skyline import Skyline


class DFSSolverPRP(SolveurBase):
    """ Résout le Perfect Rectangle Packing par DFS avec backtracking et les règles de Hougardy:
            Règle 1 : Valley Area Check      — l'aire des rects compatibles doit couvrir la vallée
            Règle 2 : Brisure de symétrie    — le premier rect reste dans la moitié gauche
            Règle 3 : Propagation globale    — toutes les vallées doivent être couvrables
            Règle 4 : Dead space check       — l'espace résiduel de la vallée doit être couvert
        Notons aussi les optimisations mémoire : zéro copie et zéro alloc. """

    def __init__(self, largeur, hauteur):
        super().__init__(largeur, hauteur)
        self.skyline = Skyline(largeur, hauteur)
        self.noeuds_explores        = 0
        self.elagages_vallee_vide   = 0   # aucun rect compatible avec la vallée
        self.elagages_aire          = 0   # règle 1 : aire insuffisante
        self.elagages_propagation   = 0   # règle 3 : une autre vallée est insolvable
        self.elagages_dead_space    = 0   # règle 4 : espace résiduel non couvert


    def _placer(self, rect, x, y):
        rect.x = x
        rect.y = y
        self.rectangles_places.append(rect)
        self.skyline.mettre_a_jour(rect)

    def _enlever(self, rect):
        self.rectangles_places.pop()
        self.skyline.annuler()
        rect.reset_position()

    # Règles de pruning de Hougardy
    def _regle1_valley_area_check(self, vallee, rects, n):
        """ L'aire totale des rects non placés compatibles avec la vallée doit être >= aire minimale de la vallée
        (largeur × hauteur_jusqu'au_plafond). Si l'aire est insuffisante, la vallée ne pourra jamais être remplie. """
        h_plafond   = self.skyline.hauteur_plafond(vallee)
        aire_vallee = vallee.largeur * (h_plafond - vallee.hauteur)

        hauteur_dispo = self.hauteur_conteneur - vallee.hauteur
        aire_compatible = sum(
            rects[i].aire()
            for i in range(n)
            if rects[i].largeur <= vallee.largeur and rects[i].hauteur <= hauteur_dispo
        )
        return aire_compatible >= aire_vallee

    def _regle2_symetrie(self, rect, x_v, premier_placement):
        """ Pour le tout premier rectangle placé, on le contraint dans la moitié gauche du conteneur. """
        if not premier_placement:
            return True
        return x_v <= (self.largeur_conteneur - rect.largeur) // 2

    def _regle3_propagation_globale(self, rects, n):
        """ Après un placement, vérifie que toutes les vallées de la skyline peuvent être couvertes par au moins un
        rectangle restant. Coupe les branches où une vallée serait irrémédiablement vide. """
        for seg in self.skyline.segments:
            if seg.hauteur == self.hauteur_conteneur:
                continue  # segment plein, pas une vallée

            hauteur_dispo = self.hauteur_conteneur - seg.hauteur
            largeur_dispo = self.skyline.largeur_disponible(seg.x, seg.hauteur)

            peut_couvrir = any(rects[i].largeur <= largeur_dispo and rects[i].hauteur <= hauteur_dispo for i in range(n))
            if not peut_couvrir:
                return False  # cette vallée est insolvable => élagage
        return True

    def _regle4_dead_space(self, rects, n, indice_exclu, largeur_restante, hauteur_dispo):
        """ Après avoir placé un rect de largeur w < largeur_vallee, l'espace résiduel
        (largeur_restante = largeur_vallee - w) doit pouvoir être couvert par au moins un des rectangles restants. """
        if largeur_restante == 0:
            return True  # pas d'espace résiduel
        for i in range(n):
            if i == indice_exclu:
                continue
            if rects[i].largeur <= largeur_restante and rects[i].hauteur <= hauteur_dispo:
                return True
        return False


    def _dfs(self, rects, n, premier_placement):
        """ Fonction récursive du DFS PRP. rects[0:n] = rectangles non encore placés. """
        self.noeuds_explores += 1

        if self.skyline.est_remplie():
            return True

        # Choisit la vallée la plus étroite => branchement le plus contraint
        vallee = self.skyline.vallee_plus_etroite()
        x_v, h_v = vallee.x, vallee.hauteur

        # Règle 1
        if not self._regle1_valley_area_check(vallee, rects, n):
            self.elagages_aire += 1
            return False

        largeur_dispo = self.skyline.largeur_disponible(x_v, h_v)
        hauteur_dispo = self.hauteur_conteneur - h_v

        # Collecte des candidats valides
        candidats = [i for i in range(n) if rects[i].largeur <= largeur_dispo and rects[i].hauteur <= hauteur_dispo]

        if not candidats:
            self.elagages_vallee_vide += 1
            return False

        # Tri : exact-fit en premier (w == largeur_dispo), puis par aire décroissante
        # Un exact-fit remplit entièrement la vallée donc pas d'espace résiduel à gérer
        candidats.sort(key=lambda i: (rects[i].largeur != largeur_dispo, -rects[i].aire()))

        vus = set()
        candidats_dedupliques = []
        for idx in candidats:
            dims = (rects[idx].largeur, rects[idx].hauteur)
            if dims not in vus:
                vus.add(dims)
                candidats_dedupliques.append(idx)
        candidats = candidats_dedupliques

        for idx in candidats:
            rect = rects[idx]

            # Règle 2
            if not self._regle2_symetrie(rect, x_v, premier_placement):
                continue

            # Règle 4
            largeur_restante = largeur_dispo - rect.largeur
            if not self._regle4_dead_space(rects, n, idx, largeur_restante, hauteur_dispo):
                self.elagages_dead_space += 1
                continue

            # Placement + swap pour retirer idx des non-placés
            rects[idx], rects[n - 1] = rects[n - 1], rects[idx]
            self._placer(rect, x_v, h_v)

            # Règle 3
            if not self._regle3_propagation_globale(rects, n - 1):
                self.elagages_propagation += 1
                self._enlever(rect)
                rects[idx], rects[n - 1] = rects[n - 1], rects[idx]
                continue

            if self._dfs(rects, n - 1, False):
                return True

            # Backtracking
            self._enlever(rect)
            rects[idx], rects[n - 1] = rects[n - 1], rects[idx]

        return False


    def emballe(self, rectangles, ordre="decroissant"):
        """ Tente de résoudre l'instance PRP. """
        self.rectangles_places      = []
        self.noeuds_explores        = 0
        self.elagages_vallee_vide   = 0
        self.elagages_aire          = 0
        self.elagages_propagation   = 0
        self.elagages_dead_space    = 0
        self.skyline = Skyline(self.largeur_conteneur, self.hauteur_conteneur)

        for r in rectangles: r.reset_position()

        rects_a_placer = list(rectangles)

        if ordre == "decroissant":
            rects_a_placer.sort(key=lambda r: r.aire(), reverse=True)
        elif ordre == "croissant":
            rects_a_placer.sort(key=lambda r: r.aire())

        return self._dfs(rects_a_placer, len(rects_a_placer), True)

    def affiche_stats(self):
        total = (self.elagages_vallee_vide + self.elagages_aire +
                 self.elagages_propagation + self.elagages_dead_space)
        print(f"        Noeuds explorés         : {self.noeuds_explores}")
        print(f"        Élagages vallée vide     : {self.elagages_vallee_vide}")
        print(f"        Élagages aire (R1)       : {self.elagages_aire}")
        print(f"        Élagages propagation (R3): {self.elagages_propagation}")
        print(f"        Élagages dead space (R4) : {self.elagages_dead_space}")
        if self.noeuds_explores > 0:
            print(f"        Taux d'élagage total    : {100 * total / self.noeuds_explores:.1f}%")
