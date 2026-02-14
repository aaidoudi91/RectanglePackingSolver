""" Implémentation de l'algorithme Bottom-Left pour le problème de Rectangle Packing.
Résout le benchmark de Korf en trouvant le conteneur optimal (pour cet algo) de surface minimale. """


import math
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import random
import numpy as np


class Rectangle:
    """ Représente un rectangle avec ses dimensions. """

    def __init__(self, largeur, hauteur, id = None):
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
            return f"Rectangle(id={self.id}, largeur={self.largeur}, hauteur={self.hauteur}, position=({self.x},{self.y}))"
        return f"Rectangle(id={self.id}, largeur={self.largeur}, hauteur={self.hauteur})"


class BenchmarkKorf:
    """ Générateur de benchmark de Korf pour le Rectangle Packing. """

    def __init__(self, n):
        self.n = n
        self.rectangles = self.genere_carres()
        self.aire_totale = self.calcule_aire_totale()

    def genere_carres(self):
        """ Génère la liste des carrés de 1×1 à n×n. """
        carres = []
        for i in range(1, self.n + 1):
            carres.append(Rectangle(largeur=i, hauteur=i, id=i))
        return carres

    def calcule_aire_totale(self):
        """ Calcule l'aire totale de tous les carrés. """
        return sum(rect.aire() for rect in self.rectangles)

    def obtenir_rectangles(self):
        """ Retourne la liste des rectangles à emballer. """
        return self.rectangles

    def affiche_info(self):
        """ Affiche les informations du benchmark. """
        print(f"Benchmark de Korf : N={self.n}, Aire totale des carrés: {self.aire_totale}")


class BottomLeftPacker:
    """ Implémentation de l'algo Bottom-Left pour le placement de rectangles. Prend un conteneur de dimensions fixes et
    tente d'y placer une liste de rectangles sans chevauchement. L'algorithme parcourt chaque rectangle et le positionne
    à la première position valide trouvée en balayant l'espace de bas en haut, puis de gauche à droite. """

    def __init__(self, largeur_conteneur, hauteur_conteneur):
        """ Initialise le packer avec les dimensions du conteneur. """
        self.largeur_conteneur = largeur_conteneur
        self.hauteur_conteneur = hauteur_conteneur
        self.rectangles_places = []

    def peut_etre_place(self, rect, x, y):
        """ Vérifie si un rectangle peut être placé à la position (x, y). """
        if x < 0 or y < 0:
            return False
        if x + rect.largeur > self.largeur_conteneur:
            return False
        if y + rect.hauteur > self.hauteur_conteneur:
            return False

        # Crée un rectangle temporaire à cette position
        # Optimisable : instancie potentiellement beaucoup d'objets en mémoire
        rec_temp = Rectangle(rect.largeur, rect.hauteur, rect.id)
        rec_temp.x = x
        rec_temp.y = y
        for place in self.rectangles_places:
            if rec_temp.chevauche(place):  # vérifie les chevauchements avec les rectangles déjà placés
                return False

        return True

    def trouve_bottom_left(self, rect):
        """ Trouve la position Bottom-Left pour placer un rectangle.
            Retourne un tuple (x, y) de la position ou None si aucune position n'est trouvée. """
        for y in range(self.hauteur_conteneur):  # Parcourt toutes les positions possibles
            for x in range(self.largeur_conteneur):
                if self.peut_etre_place(rect, x, y):
                    return x, y
        return None

    def emballe(self, rectangles, ordre="decroissant"):
        """ Emballe les rectangles en utilisant l'algorithme Bottom-Left.
            Retourne True si tous les rectangles ont été placés, False sinon. """
        self.rectangles_places = []

        for rect in rectangles:
            rect.reset_position()

        rects_a_place = rectangles.copy()  # pour ne pas modifier l'original

        if ordre == "decroissant":
            # Tri par aire décroissante (puis par largeur en cas d'égalité)
            rects_a_place.sort(key=lambda r: (r.aire(), r.largeur), reverse=True)
        elif ordre == "croissant":
            rects_a_place.sort(key=lambda r: (r.aire(), r.largeur))

        # Place chaque rectangle
        for rect in rects_a_place:
            position = self.trouve_bottom_left(rect)
            if position is None:
                #print(f"Impossible de placer le rectangle {rect.id} ({rect.largeur}×{rect.hauteur})")
                return False
            rect.x, rect.y = position  # Place le rectangle
            self.rectangles_places.append(rect)

        return True

    def hauteur_max(self):
        """ Retourne la hauteur maximale utilisée. """
        if not self.rectangles_places:
            return 0
        return max(rect.y + rect.hauteur for rect in self.rectangles_places)

    def largeur_max(self):
        """ Retourne la largeur maximale utilisée. """
        if not self.rectangles_places:
            return 0
        return max(rect.x + rect.largeur for rect in self.rectangles_places)

    def espace_perdu(self):
        """ Calcule l'espace perdu dans le conteneur. """
        aire_utilisee = sum(rect.aire() for rect in self.rectangles_places)
        aire_conteneur = self.largeur_conteneur * self.hauteur_conteneur
        return aire_conteneur - aire_utilisee

    def visualisation(self):
        """ Visualise le résultat du packing avec matplotlib. """
        fig, ax = plt.subplots(1, 1, figsize=(12, 10))

        # Dessine le bounding box réellement utilisé en trait plein (équivalent au conteneur ici)
        used_width = self.largeur_max()
        used_height = self.hauteur_max()
        bbox = patches.Rectangle((0, 0), used_width, used_height, linewidth=2, edgecolor='red', facecolor='none',
                                 label='Conteneur')
        ax.add_patch(bbox)

        # Dessine les rectangles
        colors = []
        for _ in self.rectangles_places:
            colors.append((random.random(), random.random(), random.random(), 0.7))

        for rect, color in zip(self.rectangles_places, colors):
            if rect.est_place():
                patch = patches.Rectangle((rect.x, rect.y), rect.largeur, rect.hauteur,
                                          linewidth=1, edgecolor='black', facecolor=color)
                ax.add_patch(patch)

                cx = rect.x + rect.largeur / 2
                cy = rect.y + rect.hauteur / 2
                ax.text(cx, cy, str(rect.id), ha='center', va='center',
                        fontsize=10, fontweight='bold')

        # Axes
        ax.set_xlim(-1, max(self.largeur_conteneur, used_width) + 1)
        ax.set_ylim(-1, max(self.hauteur_conteneur, used_height) + 1)
        ax.set_aspect('equal')
        ax.set_xlabel('X', fontsize=12)
        ax.set_ylabel('Y', fontsize=12)
        ax.set_title("Bottom-Left Packing", fontsize=14, fontweight='bold')
        ax.set_xticks(np.arange(0, max(self.largeur_conteneur, used_width) + 1, 1))
        ax.set_yticks(np.arange(0, max(self.hauteur_conteneur, used_height) + 1, 1))
        ax.grid(True, alpha=0.3)
        ax.legend(loc='upper right')

        # Statistiques avec bbox
        used_area = sum(rect.aire() for rect in self.rectangles_places)
        waste_initial = self.largeur_conteneur * self.hauteur_conteneur - used_area

        stats_text = f"Conteneur : {self.largeur_conteneur}×{self.hauteur_conteneur} (aire = {self.largeur_conteneur * self.hauteur_conteneur})\n"
        stats_text += f"Gaspillage conteneur : {waste_initial}"

        ax.text(0.02, 0.98, stats_text, transform=ax.transAxes,
                fontsize=10, verticalalignment='top',
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.9))

        plt.tight_layout()
        plt.show()


class ChercheurConteneurOptimal:
    """  Résout le problème de trouver le plus petit conteneur possible pour un ensemble de rectangles donné. Cette
    classe génère automatiquement une liste de conteneurs candidats de dimensions variées, triés par aire croissante. La
    génération part d'une borne inférieure calculée et teste systématiquement différentes combinaisons largeur-hauteur.
    Pour chaque candidat, elle instancie un BottomLeftPacker et tente le placement. Dès qu'un conteneur permet de placer
    tous les rectangles avec succès, la recherche s'arrête et retourne ce conteneur optimal. """

    def __init__(self, rectangles):
        self.rectangles = rectangles
        self.aire_totale = sum(r.aire() for r in rectangles)
        self.largeur_max = max(r.largeur for r in rectangles)
        self.hauteur_max = max(r.hauteur for r in rectangles)

    def genere_conteneurs_candidats(self, max_candidats=500):
        """ Génère une liste de conteneurs candidats triés par aire croissante. """
        candidats = []

        # Borne inférieure : racine carrée de l'aire totale
        borne_inf = math.ceil(math.sqrt(self.aire_totale))

        # Génère des candidats
        for width in range(max(borne_inf, self.largeur_max), borne_inf + 300):
            # Hauteur minimale pour contenir l'aire totale
            hauteur_min = math.ceil(self.aire_totale / width)

            # Teste plusieurs hauteurs possibles
            for height_offset in range(0, 10):
                height = max(hauteur_min + height_offset, self.hauteur_max)
                aire = width * height

                # Filtre les candidats trop grands
                if aire <= self.aire_totale * 2:  # Pas plus du double de l'aire totale
                    candidats.append((width, height, aire))

        # Tri par aire croissante
        candidats.sort(key=lambda x: x[2])

        # Retourne sans l'aire
        return [(w, h) for w, h, _ in candidats[:max_candidats]]

    def trouve_conteneur_optimal(self, sort_order="decroissant"):
        """ Trouve le plus petit conteneur possible avec Bottom-Left.
            Retourne un tuple (dimensions, packer) ou (None, None) si échec. """
        candidats = self.genere_conteneurs_candidats()

        for i, (width, height) in enumerate(candidats):
            packer = BottomLeftPacker(width, height)
            if packer.emballe(self.rectangles, ordre=sort_order):
                print(f"    Solution trouvée :")
                print(f"        Conteneur : {width}×{height} (aire = {width * height})")
                print(f"        Gaspillage dans le conteneur : {packer.espace_perdu()}")
                return (width, height), packer

        print("\nAucune solution trouvée dans les candidats générés.")
        return None, None



if __name__ == "__main__":
    for n in [13, 16]:
        benchmark = BenchmarkKorf(n)
        benchmark.affiche_info()

        chercheur = ChercheurConteneurOptimal(benchmark.obtenir_rectangles())
        (dimensions_conteneur, packer) = chercheur.trouve_conteneur_optimal()

        if packer:
            packer.visualisation()

        print()

