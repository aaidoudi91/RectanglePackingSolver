""" Utilitaire de recherche du conteneur optimal pour un solveur donné. """

import math


class ChercheurConteneurOptimal:
    """ Génère automatiquement une liste de conteneurs candidats de dimensions variées, triés par aire croissante. La
    génération part d'une borne inférieure calculée et teste systématiquement différentes combinaisons largeur-hauteur.
    Pour chaque candidat, elle instancie le solveur fourni et tente le placement. Dès qu'un conteneur permet de placer
    tous les rectangles avec succès, la recherche s'arrête et retourne ce conteneur. """

    def __init__(self, rectangles, classe_solveur):
        """ Initialise le chercheur avec une liste de rectangles et une classe solveur (pas une instance). """
        self.rectangles = rectangles
        self.classe_solveur = classe_solveur
        self.aire_totale = sum(r.aire() for r in rectangles)
        self.largeur_max = max(r.largeur for r in rectangles)
        self.hauteur_max = max(r.hauteur for r in rectangles)

    def genere_conteneurs_candidats(self, max_candidats=500):
        candidats = set()  # pour éviter les doublons

        # Borne inférieure : plus grand rectangle
        largeur_min = self.largeur_max
        hauteur_min = self.hauteur_max

        # Borne supérieure : somme de toutes les largeurs
        largeur_max_test = sum(r.largeur for r in self.rectangles)

        for largeur in range(largeur_min, largeur_max_test + 1):
            # Hauteur minimale : soit la hauteur du plus grand rect, soit ce qui
            # est nécessaire pour contenir l'aire totale
            hauteur = max(math.ceil(self.aire_totale / largeur), hauteur_min)
            aire = largeur * hauteur

            if self.aire_totale * 1.008 < aire <= self.aire_totale * 1.15:
                # Normaliser pour éviter (x, y) et (y, x) (pour dfs, sinon mettre les deux)
                candidat = tuple(sorted([largeur, hauteur]))
                candidats.add(candidat)

        # Tri par aire croissante
        candidats = sorted(candidats, key=lambda x: (x[0] * x[1]))

        return candidats[:max_candidats]

    def trouve_conteneur_optimal(self, ordre="decroissant"):
        """ Trouve le plus petit conteneur possible avec le solveur fourni.
        Retourne un tuple (dimensions, solveur) ou (None, None) si échec. """
        candidats = self.genere_conteneurs_candidats()

        for largeur, hauteur in candidats:
            solveur = self.classe_solveur(largeur, hauteur)
            if solveur.emballe(self.rectangles, ordre=ordre):
                aire_conteneur = largeur * hauteur
                pourcentage_gaspillage = (solveur.espace_perdu() / aire_conteneur) * 100
                print(f"    Solution trouvée :")
                print(f"        Conteneur : {largeur}×{hauteur} (aire = {aire_conteneur})")
                print(f"        Gaspillage : {solveur.espace_perdu()} ({pourcentage_gaspillage:.2f}%)\n")
                return (largeur, hauteur), solveur

        print("Aucune solution trouvée dans les candidats générés.")
        return None, None
