""" Point d'entrée principal du projet. Mode d'exécution sélectionnable via la variable MODE ci-dessous :
    "KORF_BL" : Benchmark Korf avec Bottom-Left.
    "KORF_DFS" : Benchmark Korf avec DFS.
    "PRP" : Instances PRP générées (comparaison optionnelle DFS Général / DFS Skyline).
    "PARTRIDGE" : Benchmark Partridge (comparaison optionnelle DFS Général / DFS Skyline). """

import time
from typing import List, Tuple

from benchmarks.korf import BenchmarkKorf
from benchmarks.prp_generator import GenerateurPRP
from benchmarks.partridge import BenchmarkPartridge

from solvers.base import SolveurBase
from solvers.bottom_left import BottomLeft
from solvers.dfs import DFS
from solvers.dfs_prp import DFS_PRP

from utils.conteneur_optimal import ChercheurConteneurOptimal
from utils.visualisation import visualise_solution


MODE = "PRP"  # Choix parmi les 4 modes listés ci-dessus

CONFIG_KORF_BL = {"valeurs_n" : [3, 4, 5, 6, 7, 8, 9, 10, 11, 13, 14, 15], "visualiser" : True}

CONFIG_KORF_DFS = {"valeurs_n" : [3, 4, 5, 6, 7, 8, 9, 10, 11, 13, 14, 15, 16], "visualiser" : True}

# (nom, largeur, hauteur, nb_cibles, seed, ratio_min, biais_alt)
CONFIG_PRP = [ ("15", 30, 20, 15, 42, 0.10, 1), ("20", 40, 30, 25, 42, 0.3, 0.9), ("30", 60, 40, 30, 42, 0.12, 0.9)]
PRP_VISUALISER, PRP_COMPARER_DFS = True, True

CONFIG_PARTRIDGE = {"valeurs_n" : [2, 3, 4, 5, 6, 7, 8, 9, 10, 11], "visualiser" : True}
PARTRIDGE_VISUALISER, PARTRIDGE_COMPARER_DFS = True, False


def _chrono(solveur, rectangles):
    """ Lance solveur.emballe(rectangles) et retourne (succes, duree). """
    debut = time.perf_counter()
    succes = solveur.emballe(rectangles)
    duree = time.perf_counter() - debut
    return succes, duree

def _affiche_resultat(succes, duree, solveur):
    """ Affiche le résultat et les stats d'un solveur. """
    statut = "Solution trouvée" if succes else "Aucune solution"
    print(f"    {statut} en {duree:.4f}s")
    if hasattr(solveur, 'affiche_stats'):
        solveur.affiche_stats()


def executer_korf(n, classe_solveur, nom_solveur, visualiser=True):
    """ Exécute le benchmark de Korf avec le solveur spécifié. """
    print(f"\nBenchmark Korf N={n} - {nom_solveur}")
    benchmark = BenchmarkKorf(n)
    benchmark.affiche_info()
    chercheur = ChercheurConteneurOptimal(benchmark.obtenir_rectangles(), classe_solveur)
    debut = time.perf_counter()
    (dims, solveur) = chercheur.trouve_conteneur_optimal()
    duree = time.perf_counter() - debut
    if solveur and visualiser:
        print(f"    Solution trouvée en {duree:.4f}s")
        if hasattr(solveur, 'affiche_stats'):
            solveur.affiche_stats()
        visualise_solution(solveur, titre=f"Benchmark Korf N={n} - {nom_solveur}")

def executer_prp(nom, largeur, hauteur, nb_cibles, seed, ratio_min, biais_alt, visualiser=True, comparer_dfs=True):
    """ Exécute une instance PRP générée pseudo-aléatoirement avec le solveur DFS Skyline (et DFS Général) """
    print(f"\nPRP N={nom} - Conteneur {largeur}×{hauteur}")
    generateur = GenerateurPRP(largeur, hauteur, nb_cibles, seed=seed, ratio_min=ratio_min, biais_alternance=biais_alt)
    generateur.affiche_info()

    solveurs_a_tester: List[Tuple[str, SolveurBase]] = [("DFS Skyline", DFS_PRP(largeur, hauteur))]
    if comparer_dfs: solveurs_a_tester.append(("DFS Général", DFS(largeur, hauteur)))

    premier_succes = None
    for nom_solveur, solveur in solveurs_a_tester:
        print(f"{nom_solveur} :")
        rectangles = generateur.obtenir_rectangles_melanges()
        succes, duree = _chrono(solveur, rectangles)
        _affiche_resultat(succes, duree, solveur)
        if succes and premier_succes is None:
            premier_succes = (solveur, nom_solveur)
        if visualiser and premier_succes:
            solveur_vis, nom_vis = premier_succes
            visualise_solution(solveur_vis, titre=f"PRP N={nom} - {nom_vis}")

def executer_partridge(n, comparer_dfs=True, visualiser=True):
    """ Exécute le benchmark Partridge avec DFS Skyline, et optionnellement DFS Général. """
    print(f"\nBenchmark Partridge N={n}")
    benchmark = BenchmarkPartridge(n, seed=42)
    benchmark.affiche_info()
    cote_conteneur = benchmark.cote_conteneur

    solveurs_a_tester: List[Tuple[str, SolveurBase]] = [("DFS Skyline", DFS_PRP(cote_conteneur, cote_conteneur))]
    if comparer_dfs: solveurs_a_tester.append(("DFS Général", DFS(cote_conteneur, cote_conteneur)))

    for nom_solveur, solveur in solveurs_a_tester:
        print(f"{nom_solveur} :")
        succes, duree = _chrono(solveur, benchmark.obtenir_rectangles_melanges())
        _affiche_resultat(succes, duree, solveur)
        if succes and visualiser:
            visualise_solution(solveur, titre=f"Partridge N={n} - {nom_solveur}")


if __name__ == "__main__":
    if MODE == "KORF_BL":
        for n in CONFIG_KORF_BL["valeurs_n"]:
            executer_korf(n, BottomLeft, "Bottom-Left", visualiser=CONFIG_KORF_BL["visualiser"])
    elif MODE == "KORF_DFS":
        for n in CONFIG_KORF_DFS["valeurs_n"]:
            executer_korf(n, DFS, "DFS Exact", visualiser=CONFIG_KORF_DFS["visualiser"])
    elif MODE == "PRP":
        for config in CONFIG_PRP:
            executer_prp(*config, visualiser=PRP_VISUALISER, comparer_dfs=PRP_COMPARER_DFS)
    elif MODE == "PARTRIDGE":
        for n in CONFIG_PARTRIDGE["valeurs_n"]:
            executer_partridge(n, comparer_dfs=PARTRIDGE_COMPARER_DFS, visualiser=PARTRIDGE_VISUALISER)
    else:
        print("Valeurs acceptées : KORF_BL, KORF_DFS, PRP, PARTRIDGE")