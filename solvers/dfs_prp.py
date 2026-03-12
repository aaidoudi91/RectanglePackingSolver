""" DFS avec backtracking pour le Perfect Rectangle Packing. """

from solvers.base import SolveurBase
from utils.skyline import Skyline


class DFS_PRP(SolveurBase):
    """ Résout le Perfect Rectangle Packing par DFS avec backtracking et les règles de Hougardy:
            Règle 1 : Valley Area Check - l'aire des rectangles compatibles doit couvrir la vallée.
            Règle 2 : Brisure de symétrie - le premier rect reste dans la moitié gauche.
            Règle 3 : Propagation globale - toutes les vallées doivent être couvrables.
            Règle 4 : Dead space check - l'espace résiduel de la vallée doit être couvert. """

    def __init__(self, largeur, hauteur):
        super().__init__(largeur, hauteur)
        self.skyline = Skyline(largeur, hauteur)
        self.noeuds_explores = 0
        self.elagages_vallee_vide = 0  # aucun rect compatible avec la vallée
        self.elagages_aire = 0  # règle 1 : aire insuffisante
        self.elagages_propagation = 0  # règle 3 : une autre vallée est insolvable
        self.elagages_espace_residuel = 0  # règle 4 : espace résiduel non couvert


    def _placer(self, rectangle, x, y):
        rectangle.x = x
        rectangle.y = y
        self.rectangles_places.append(rectangle)
        self.skyline.mettre_a_jour(rectangle)

    def _enlever(self, rectangle):
        self.rectangles_places.pop()
        self.skyline.annuler()
        rectangle.reset_position()


    def _regle1_vallee_verification_aire(self, vallee, rects, n):
        """ L'aire totale des rectangles non placés compatibles avec la vallée doit être >= aire minimale de la vallée
        (largeur × hauteur_jusqu'au_plafond). Si l'aire est insuffisante, la vallée ne pourra jamais être remplie. """
        hauteur_plafond = self.skyline.hauteur_plafond(vallee)
        aire_vallee = vallee.largeur * (hauteur_plafond - vallee.hauteur)

        hauteur_dispo = self.hauteur_conteneur - vallee.hauteur
        aire_compatible = sum(rects[i].aire() for i in range(n)
                              if rects[i].largeur <= vallee.largeur and rects[i].hauteur <= hauteur_dispo)
        return aire_compatible >= aire_vallee

    def _regle2_symetrie(self, rect, x_vallee, premier_placement):
        """ Pour le tout premier rectangle placé, on le contraint dans la moitié gauche du conteneur. """
        if not premier_placement:
            return True
        return x_vallee <= (self.largeur_conteneur - rect.largeur) // 2

    def _regle3_propagation_globale(self, rects, n):
        """ Après un placement, vérifie que toutes les vallées de la skyline peuvent être couvertes par au moins un
        rectangle restant. Coupe les branches où une vallée serait irrémédiablement vide. """
        for segment in self.skyline.segments:
            if segment.hauteur == self.hauteur_conteneur:  # segment plein, pas une vallée
                continue
            hauteur_dispo = self.hauteur_conteneur - segment.hauteur
            largeur_dispo = self.skyline.largeur_disponible(segment.x, segment.hauteur)
            peut_couvrir = any(rects[i].largeur <= largeur_dispo and rects[i].hauteur <= hauteur_dispo for i in range(n))
            if not peut_couvrir:  # si cette vallée est insolvable alors élagage
                return False
        return True

    @staticmethod
    def _regle4_dead_space(rectangles, n, indice_exclu, largeur_restante, hauteur_dispo):
        """ Après avoir placé un rectangle de largeur < largeur_vallee, l'espace résiduel
        (largeur_restante = largeur_vallee - largeur) doit pouvoir être couvert par au moins un des rectangles restants. """
        if largeur_restante == 0:  # pas d'espace résiduel
            return True
        for i in range(n):
            if i == indice_exclu:
                continue
            if rectangles[i].largeur <= largeur_restante and rectangles[i].hauteur <= hauteur_dispo:
                return True
        return False


    def _dfs(self, rectangles, n, premier_placement):
        """ Fonction récursive du DFS PRP. rects[0:n] = rectangles non encore placés. """
        self.noeuds_explores += 1

        if self.skyline.est_remplie():  # condition d'arrêt
            return True

        vallee = self.skyline.vallee_plus_etroite()  # prend la vallée la plus étroite (branchement le plus contraint)
        x_vallee, hauteur_v = vallee.x, vallee.hauteur

        if not self._regle1_vallee_verification_aire(vallee, rectangles, n):  # règle 1
            self.elagages_aire += 1
            return False

        largeur_dispo = self.skyline.largeur_disponible(x_vallee, hauteur_v)
        hauteur_dispo = self.hauteur_conteneur - hauteur_v
        # Collecte des candidats valides
        candidats = [i for i in range(n) if rectangles[i].largeur <= largeur_dispo and rectangles[i].hauteur <= hauteur_dispo]
        if not candidats:
            self.elagages_vallee_vide += 1
            return False

        # Tri avec exact-fit en premier (largeur == largeur_dispo), puis par aire décroissante
        candidats.sort(key=lambda i: (rectangles[i].largeur != largeur_dispo, -rectangles[i].aire()))

        # Élagage par symétrie des doublons
        vus = set()  # dimensions que l'on a déjà prévu de tester
        candidats_dedupliques = []
        for idx in candidats:
            dims = (rectangles[idx].largeur, rectangles[idx].hauteur)
            if dims not in vus:
                vus.add(dims)
                candidats_dedupliques.append(idx)
        candidats = candidats_dedupliques

        for idx in candidats:
            rect = rectangles[idx]

            if not self._regle2_symetrie(rect, x_vallee, premier_placement):  # règle 2
                continue

            largeur_restante = largeur_dispo - rect.largeur
            if not self._regle4_dead_space(rectangles, n, idx, largeur_restante, hauteur_dispo):  # règle 4
                self.elagages_espace_residuel += 1
                continue

            # Placement et swap pour retirer idx des non-placés
            rectangles[idx], rectangles[n-1] = rectangles[n-1], rectangles[idx]
            self._placer(rect, x_vallee, hauteur_v)

            if not self._regle3_propagation_globale(rectangles, n-1):  # règle 3
                self.elagages_propagation += 1
                self._enlever(rect)
                rectangles[idx], rectangles[n-1] = rectangles[n-1], rectangles[idx]
                continue

            if self._dfs(rectangles, n-1, False):
                return True

            # Backtracking
            self._enlever(rect)
            rectangles[idx], rectangles[n-1] = rectangles[n-1], rectangles[idx]

        return False


    def emballe(self, rectangles, ordre="croissant"):
        """ Tente de résoudre l'instance PRP. """
        self.rectangles_places = []
        self.noeuds_explores = 0
        self.elagages_vallee_vide = 0
        self.elagages_aire = 0
        self.elagages_propagation = 0
        self.elagages_espace_residuel = 0
        self.skyline = Skyline(self.largeur_conteneur, self.hauteur_conteneur)

        for rectangle in rectangles: rectangle.reset_position()
        rectangles_a_placer = list(rectangles)
        if ordre == "decroissant":
            rectangles_a_placer.sort(key=lambda r: r.aire(), reverse=True)
        elif ordre == "croissant":
            rectangles_a_placer.sort(key=lambda r: r.aire())
        return self._dfs(rectangles_a_placer, len(rectangles_a_placer), True)

    def affiche_stats(self):
        total = (self.elagages_vallee_vide + self.elagages_aire +
                 self.elagages_propagation + self.elagages_espace_residuel)
        print(f"        Noeuds explorés         : {self.noeuds_explores}")
        print(f"        Élagages vallée vide     : {self.elagages_vallee_vide}")
        print(f"        Élagages aire (R1)       : {self.elagages_aire}")
        print(f"        Élagages propagation (R3): {self.elagages_propagation}")
        print(f"        Élagages dead space (R4) : {self.elagages_espace_residuel}")
        if self.noeuds_explores > 0:
            print(f"        Taux d'élagage total    : {100 * total / self.noeuds_explores:.1f}%")
