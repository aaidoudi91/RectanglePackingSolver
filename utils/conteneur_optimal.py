""" Utilitaire de recherche du conteneur optimal pour un solveur donné. """

import math


class ChercheurConteneurOptimal:
    """ Génère automatiquement une liste de conteneurs candidats de dimensions variées, triés par aire croissante. La
    génération part d'une borne inférieure calculée et teste systématiquement différentes combinaisons largeur-hauteur.
    Pour chaque candidat, elle instancie le solveur fourni et tente le placement. Dès qu'un conteneur permet de placer
    tous les rectangles avec succès, la recherche s'arrête et retourne ce conteneur. """

    def __init__(self, rectangles, classe_solveur):
        """ Initialise le chercheur avec une liste de rectangles et une classe solveur (pas une instance).
        Exemple : ChercheurConteneurOptimal(rectangles, DFSSolver) """
        self.rectangles = rectangles
        self.classe_solveur = classe_solveur
        self.aire_totale = sum(r.aire() for r in rectangles)
        self.largeur_max = max(r.largeur for r in rectangles)
        self.hauteur_max = max(r.hauteur for r in rectangles)

    def genere_conteneurs_candidats(self, max_candidats=500):
        """ Génère une liste de conteneurs candidats triés par aire croissante. """
        candidats = []

        borne_inf = math.ceil(math.sqrt(self.aire_totale))

        for largeur in range(max(borne_inf, self.largeur_max), borne_inf + 300):
            hauteur_min = math.ceil(self.aire_totale / largeur)

            for height_offset in range(0, 10):
                hauteur = max(hauteur_min + height_offset, self.hauteur_max)
                aire = largeur * hauteur

                if aire <= self.aire_totale * 1.2:
                    candidats.append((hauteur, largeur, aire))
                    candidats.append((largeur, hauteur, aire))

        candidats.sort(key=lambda x: x[2])
        return [(largeur, hauteur) for largeur, hauteur, _ in candidats[:max_candidats]]

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
