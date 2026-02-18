""" Utilitaire de visualisation des solutions provenant d'un solveur quelconque. """

import random
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches


def visualise_solution(solveur, titre="Rectangle Packing"):
    fig, ax = plt.subplots(1, 1, figsize=(12, 10))

    # Bounding box réellement utilisé
    largeur_utilisee = solveur.largeur_max()
    hauteur_utilisee = solveur.hauteur_max()

    bbox = patches.Rectangle((0, 0), largeur_utilisee, hauteur_utilisee,
                              linewidth=2, edgecolor='red', facecolor='none', label='Conteneur')
    ax.add_patch(bbox)

    # Dessine les rectangles placés
    couleurs = [(random.random(), random.random(), random.random(), 0.7)
                for _ in solveur.rectangles_places]

    for rect, couleur in zip(solveur.rectangles_places, couleurs):
        if rect.est_place():
            patch = patches.Rectangle((rect.x, rect.y), rect.largeur, rect.hauteur,
                                       linewidth=1, edgecolor='black', facecolor=couleur)
            ax.add_patch(patch)

            cx = rect.x + rect.largeur / 2
            cy = rect.y + rect.hauteur / 2
            ax.text(cx, cy, str(rect.id), ha='center', va='center',
                    fontsize=10, fontweight='bold')

    # Axes
    ax.set_xlim(-1, max(solveur.largeur_conteneur, largeur_utilisee) + 1)
    ax.set_ylim(-1, max(solveur.hauteur_conteneur, hauteur_utilisee) + 1)
    ax.set_aspect('equal')
    ax.set_xlabel('X', fontsize=12)
    ax.set_ylabel('Y', fontsize=12)
    ax.set_title(titre, fontsize=14, fontweight='bold')
    ax.set_xticks(np.arange(0, max(solveur.largeur_conteneur, largeur_utilisee) + 1, 1))
    ax.set_yticks(np.arange(0, max(solveur.hauteur_conteneur, hauteur_utilisee) + 1, 1))
    ax.grid(True, alpha=0.3)
    ax.legend(loc='upper right')

    # Statistiques
    aire_utilisee = sum(r.aire() for r in solveur.rectangles_places)
    espace_perdu = solveur.largeur_conteneur * solveur.hauteur_conteneur - aire_utilisee

    stats_text = (f"Conteneur : {solveur.largeur_conteneur}×{solveur.hauteur_conteneur} "
                  f"(aire = {solveur.largeur_conteneur * solveur.hauteur_conteneur})\n"
                  f"Gaspillage conteneur : {espace_perdu}")

    ax.text(0.02, 0.98, stats_text, transform=ax.transAxes,
            fontsize=10, verticalalignment='top',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.9))

    plt.tight_layout()
    plt.show()
