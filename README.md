# Rectangle Packing Solver

Implémentation robuste et optimisée pour la résolution du **2D Rectangle Packing Problem**, 
un problème d'optimisation combinatoire NP-difficile. L'objectif est de placer un ensemble de rectangles de dimensions 
hétérogènes dans un conteneur englobant minimal, sans aucun chevauchement. 

Lorsque l'espace perdu est nul, l'algorithme atteint un **Perfect Rectangle Packing (PRP)**. Ce solveur propose à la 
fois des approches heuristiques rapides et des méthodes exactes capables de prouver l'optimalité sur des instances 
complexes, ainsi qu'un solveur dédié au PRP.

**Domaines d'application :**
* **Découpe industrielle** (verre, métal, bois, tissu) pour minimiser les chutes.
* **Conception VLSI** (Very Large Scale Integration) pour l'agencement de circuits imprimés.
* **Logistique et fret** (Bin/Strip packing pour le chargement de conteneurs).
* **Ordonnancement** (Allocation de ressources sous contraintes de temps).

## Architecture

```text
rectangle_packing/
├── models/
│   └── rectangle.py           # Représentation géométrique d'un rectangle
├── benchmarks/
│   ├── korf.py                # Benchmark de Korf
│   └── prp_generator.py       # Générateur d'instances PRP par guillotine cut
│ 
├── solvers/
│   ├── base.py                # Interface abstraite
│   ├── bottom_left.py         # Solveur Heuristique via Bottom-Left
│   ├── dfs.py                 # Solveur exact via DFS avec backtracking optimisé
│   └── dfs_prp.py             # Solveur exact via DFS avec backtracking optimisé pour le Perfect Rectangle Packing
├── utils/
│   ├── visualisation.py       # Rendu graphique via Matplotlib
│   ├── skyline.py             # Structure de données Skyline incrémentale
│   └── conteneur_optimal.py   # Moteur de recherche générique du conteneur minimal
│ 
├── main.py                    # Point d'entrée et exécution des benchmarks
│ 
├── requirements.txt   
├── README.md                  
└── Rapport.pdf    
```

## Algorithmes implémentés

### 1. Heuristique Bottom-Left

Une approche gloutonne rapide permettant de trouver des solutions initiales ou de traiter de très grandes instances 
où la preuve d'optimalité n'est pas requise. Trie les rectangles généralement par aire décroissante et place chacun 
d'eux à la position valide la plus basse, puis la plus à gauche possible.


### 2. DFS Branch-and-Bound - RP général

Une recherche exhaustive en profondeur pour le Rectangle Packing général. Ce solveur garantit de trouver le conteneur optimal absolu (ou de prouver qu'un 
conteneur donné est irréalisable). Pour contrer l'explosion combinatoire inhérente au problème NP-difficile, 
ce moteur intègre des techniques d'élagage tirées de la littérature scientifique :

* **Brisure de symétrie** — force le 1er rectangle dans le quadrant inférieur gauche.
* **Élagage par aire** — coupe si l'aire restante > espace libre.
* **Bounding functions de Korf** — relaxation 1D (Martello & Toth) horizontale + verticale.
* **États incrémentaux** —  mise à jour de l'état du conteneur, évitant de re-calculer l'état global.
* **Zéro copie** — parcours par index, aucune sous-liste allouée.
* **Sauts maximaux** — saut direct au bord droit du rectangle bloquant le plus loin.

### 3. DFS Skyline - PRP
Un solveur dédié aux instances de Perfect Rectangle Packing (gaspillage nul imposé), exploitant la règle de branchement de
Bitner-Reingold via une structure Skyline incrémentale. La position du prochain
rectangle est imposée par la vallée la plus étroite de la skyline — si aucun rectangle ne peut
la remplir, on backtrack immédiatement. Les règles de pruning de Hougardy (2012) complètent le dispositif :

* **Règle 1** — l'aire des rectangles compatibles doit couvrir la vallée.
* **Règle 2** — brisure de symétrie sur le premier placement.
* **Règle 3** — toutes les vallées de la skyline doivent être couvrables simultanément.
* **Règle 4** — l'espace résiduel après placement doit pouvoir être couvert.
* **Brisure des doublons** — k rectangles identiques → 1 seule tentative au lieu de k! (Simonis & O'Sullivan, 2008).


## Installation & Démarrage

Prérequis : Python 3.8+. Pour la visualisation : Matplotlib & Numpy.

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
