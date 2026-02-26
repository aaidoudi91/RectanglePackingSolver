""" Point d'entrée principal du projet Rectangle Packing.
Lance les benchmarks de Korf avec les différents solveurs disponibles. """

import time
from benchmarks.korf import BenchmarkKorf
from solvers.bottom_left import BottomLeft
from solvers.dfs import DFS
from utils.conteneur_optimal import ChercheurConteneurOptimal
from utils.visualisation import visualise_solution
from benchmarks.prp_generator import GenerateurPRP
from solvers.dfs_prp import DFSSolverPRP

def run_prp(largeur, hauteur, nb_rectangles, seed=42):
    gen = GenerateurPRP(largeur, hauteur, nb_rectangles, seed=seed, taille_min=2, ratio_min=0.2)
    gen.affiche_info()
    debut = time.time()

    solveur = DFSSolverPRP(largeur, hauteur)
    succes = solveur.emballe(gen.obtenir_rectangles_melanges())

    if succes:
        print("    Solution trouvée via DFS.")
        #solveur.affiche_stats()
        visualise_solution(solveur, titre=f"PRP — {largeur}×{hauteur}, {nb_rectangles} rects")

    fin = time.time()
    temps_execution = fin - debut
    print(f"Temps d'exécution : {temps_execution:.2f} secondes\n")

def executer_benchmark(n, classe_solveur, nom_solveur):
    print(f"Benchmark de Korf : N={n}, {nom_solveur}")

    debut = time.time()

    benchmark = BenchmarkKorf(n)
    benchmark.affiche_info()

    chercheur = ChercheurConteneurOptimal(benchmark.obtenir_rectangles(), classe_solveur)
    (dimensions, solveur) = chercheur.trouve_conteneur_optimal()

    if solveur:
        visualise_solution(solveur, titre=f"{nom_solveur} — Korf N={n}")

    fin = time.time()
    temps_execution = fin - debut
    print(f"Temps d'exécution : {temps_execution:.2f} secondes\n")


if __name__ == "__main__":
    """
    for n in [14, 15]:
        executer_benchmark(n, BottomLeft, "Bottom-Left")"""

    for n in [11]:
        executer_benchmark(n, DFS, "DFS")

    for nb in [20]:
        run_prp(20, 15, nb, seed=42)
