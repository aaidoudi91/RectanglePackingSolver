""" Point d'entrée principal du projet Rectangle Packing.
Lance les benchmarks de Korf avec les différents solveurs disponibles. """

from benchmarks.korf import BenchmarkKorf
from solvers.bottom_left import BottomLeftPacker
from solvers.dfs import DFSSolver
from utils.conteneur_optimal import ChercheurConteneurOptimal
from utils.visualisation import visualise_solution


def executer_benchmark(n, classe_solveur, nom_solveur):
    print(f"Benchmark de Korf : N={n}, {nom_solveur}")

    benchmark = BenchmarkKorf(n)
    benchmark.affiche_info()

    chercheur = ChercheurConteneurOptimal(benchmark.obtenir_rectangles(), classe_solveur)
    (dimensions, solveur) = chercheur.trouve_conteneur_optimal()

    if solveur:
        visualise_solution(solveur, titre=f"{nom_solveur} — Korf N={n}")


if __name__ == "__main__":
    """Bottom-Left sur des instances moyennes
    for n in [10, 15]:
        executer_benchmark(n, BottomLeftPacker, "Bottom-Left")"""

    # DFS uniquement sur des petites instances
    for n in [6, 7, 8]:
        executer_benchmark(n, DFSSolver, "DFS")
