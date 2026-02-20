# Rectangle Packing Solver

Implémentation robuste et optimisée pour la résolution du **2D Rectangle Packing Problem**, 
un problème d'optimisation combinatoire NP-difficile. L'objectif est de placer un ensemble de rectangles de dimensions 
hétérogènes dans un conteneur englobant minimal, sans aucun chevauchement. 

Lorsque l'espace perdu est nul, l'algorithme atteint un **Perfect Rectangle Packing (PRP)**. Ce solveur propose à la 
fois des approches heuristiques rapides et des méthodes exactes capables de prouver l'optimalité sur des instances 
complexes (comme le benchmark de Korf).

**Domaines d'application :**
* **Découpe industrielle** (verre, métal, bois, tissu) pour minimiser les chutes.
* **Conception VLSI** (Very Large Scale Integration) pour l'agencement de circuits imprimés.
* **Logistique et fret** (Bin/Strip packing pour le chargement de conteneurs).
* **Ordonnancement** (Allocation de ressources sous contraintes de temps).

## Architecture

```text
rectangle_packing/
├── models/
│   └── rectangle.py           # Représentation géométrique
├── benchmarks/
│   └── korf.py                # Benchmark de Korf
├── solvers/
│   ├── base.py                # Interface abstraite
│   ├── bottom_left.py         # Solveur Heuristique via Bottom-Left
│   └── dfs.py                 # Solveur Exact via DFS avec backtracking optimisé
├── utils/
│   ├── visualisation.py       # Rendu graphique via Matplotlib
│   └── conteneur_optimal.py   # Moteur de recherche générique du conteneur minimal
│ 
├── main.py                    # Point d'entrée et exécution des benchmarks
│ 
├── README.md                  
└── Rapport.pdf    
```

## Algorithmes implémentés

### 1. Heuristique Bottom-Left

Une approche gloutonne rapide permettant de trouver des solutions initiales ou de traiter de très grandes instances 
où la preuve d'optimalité n'est pas requise. Trie les rectangles généralement par aire décroissante et place chacun 
d'eux à la position valide la plus basse, puis la plus à gauche possible.


### 2. DFS avec backtracking optimisé

Une recherche exhaustive en profondeur. Ce solveur garantit de trouver le conteneur optimal absolu (ou de prouver qu'un 
conteneur donné est irréalisable). Pour contrer l'explosion combinatoire inhérente au problème NP-difficile, 
ce moteur intègre des techniques avancées d'élagage (pruning) tirées de la littérature scientifique :

* **Brisure de symétrie** — force le 1er rectangle dans le quadrant supérieur gauche.
* **Élagage par aire** — coupe si l'aire restante > espace libre.
* **Bounding functions de Korf** — relaxation 1D (Martello & Toth) horizontale + verticale.
* **États incrémentaux** —  mise à jour de l'état du conteneur, évitant de re-calculer l'état global.
* **Zéro copie** — parcours par index, aucune sous-liste allouée.
* **Sauts maximaux** — saut direct au bord droit du rectangle bloquant le plus loin.


## Installation & Démarrage

Prérequis : Python 3.14+

```bash
# Installer les dépendances
pip install -r requirements.txt

# Lancer le solveur sur les benchmarks par défaut
python main.py
```

## Références et Bibliographie
Les optimisations implémentées dans ce solveur s'appuient sur les travaux de recherche suivants :

* Korf, R. E. (2003). Optimal Rectangle Packing: Initial Results. Actes de la conférence ICAPS.
* Korf, R. E. (2004). Optimal Rectangle Packing: New Results. Actes de la conférence ICAPS.
* Simonis, H., & O'Sullivan, B. (2008). Search Strategies for Rectangle Packing. Actes de la conférence CP.
* Hougardy, S. (2012). A Scale Invariant Exact Algorithm for Dense Rectangle Packing.
* Martello, S., Monaci, M., & Vigo, D. (2003). An Exact Approach to the Strip-Packing Problem. INFORMS Journal on Computing.
* Hopper, E., & Turton, B. C. H. (2001). An Empirical Investigation of Meta-heuristic and Heuristic Algorithms for a 2D Packing Problem. European Journal of Operational Research.

## Auteur
Aidoudi Aaron

Projet TER - Master 1 Intelligence Artificielle Distribuée à l'Université Paris Cité

Année Universitaire 2025-2026
