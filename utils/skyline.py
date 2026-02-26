""" Structure de données Skyline pour le Rectangle Packing. Maintient le profil supérieur des rectangles placés sous
forme de segments horizontaux. Conçue pour être utilisée de manière incrémentale avec backtracking (DFSSolverPRP). """


class Segment:
    """ Représente un segment horizontal de la skyline.
    Un segment (x, largeur, hauteur) signifie que la zone [x, x+largeur[ est remplie jusqu'à 'hauteur'. """

    __slots__ = ('x', 'largeur', 'hauteur')
    def __init__(self, x, largeur, hauteur):
        self.x = x
        self.largeur = largeur
        self.hauteur = hauteur

    def x_fin(self):
        return self.x + self.largeur

    def __repr__(self):
        return f"[{self.x}→{self.x_fin()} | h={self.hauteur}]"


class Skyline:
    """ Profil supérieur des rectangles placés dans le conteneur. """

    def __init__(self, largeur, hauteur):
        self.largeur = largeur
        self.hauteur = hauteur
        self.segments = [Segment(0, largeur, 0)]
        self._historique = []

    def vallee(self):
        """ Retourne le segment le plus bas et plus à gauche (Bitner-Reingold), ou None si la skyline est complète. """
        h_min = min(s.hauteur for s in self.segments)
        if h_min == self.hauteur:
            return None
        for seg in self.segments:
            if seg.hauteur == h_min:
                return seg
        return None

    def vallee_plus_etroite(self):
        """ Retourne la vallée (segment plus bas que ses deux voisins) de largeur minimale parmi toutes les vallées
        (Hougardy), ou en cas d'égalité de largeur, retourne la plus basse, puis la plus à gauche. Retourne None si la
        skyline est complète. """
        if self.est_remplie():
            return None

        vallees = self._detecter_vallees()
        if not vallees:
            # Pas de creux local strict => on retombe sur la plus basse à gauche
            return self.vallee()

        # Tri : largeur croissante, puis hauteur croissante, puis x croissant
        vallees.sort(key=lambda s: (s.largeur, s.hauteur, s.x))
        return vallees[0]

    def _detecter_vallees(self):
        """ Retourne tous les segments qui sont des vallées locales (plus bas que leurs voisins).
        Un segment de bord (premier ou dernier) est considéré vallée si son unique voisin est plus haut. """
        vallees = []
        n = len(self.segments)
        for i, seg in enumerate(self.segments):
            if seg.hauteur == self.hauteur:
                continue  # segment plein => pas une vallée
            h_gauche = self.segments[i - 1].hauteur if i > 0     else self.hauteur
            h_droite = self.segments[i + 1].hauteur if i < n - 1 else self.hauteur
            if seg.hauteur < h_gauche and seg.hauteur < h_droite:
                vallees.append(seg)
        return vallees

    def hauteur_plafond(self, vallee):
        """ Retourne la hauteur du plafond de la vallée = min(h_voisin_gauche, h_voisin_droit).
        C'est la hauteur jusqu'à laquelle la vallée doit être remplie au minimum.
        Utilisée pour la Règle 1 de Hougardy (valley area check). """
        n = len(self.segments)
        for i, seg in enumerate(self.segments):
            if seg is vallee:
                h_gauche = self.segments[i - 1].hauteur if i > 0     else self.hauteur
                h_droite = self.segments[i + 1].hauteur if i < n - 1 else self.hauteur
                return min(h_gauche, h_droite)
        return self.hauteur

    def largeur_disponible(self, x_v, h_v):
        """ Retourne la largeur totale disponible à partir de (x_v, h_v).
        S'étend vers la droite tant que les segments adjacents sont à la même hauteur h_v. """
        total = 0
        for seg in self.segments:
            if seg.x >= x_v and seg.hauteur == h_v:
                total += seg.largeur
            elif seg.x >= x_v:
                break
        return total

    def est_remplie(self):
        """ Retourne True si le conteneur est entièrement rempli. """
        return len(self.segments) == 1 and self.segments[0].hauteur == self.hauteur


    def mettre_a_jour(self, rect):
        """ Met à jour la skyline après le placement de rect. """
        self._historique.append([Segment(s.x, s.largeur, s.hauteur) for s in self.segments])

        x_debut = rect.x
        x_fin   = rect.x + rect.largeur
        h_new   = rect.y + rect.hauteur

        nouveaux = []
        for seg in self.segments:
            if seg.x_fin() <= x_debut or seg.x >= x_fin:
                nouveaux.append(Segment(seg.x, seg.largeur, seg.hauteur))
            else:
                if seg.x < x_debut:
                    nouveaux.append(Segment(seg.x, x_debut - seg.x, seg.hauteur))
                overlap_x   = max(seg.x, x_debut)
                overlap_fin = min(seg.x_fin(), x_fin)
                nouveaux.append(Segment(overlap_x, overlap_fin - overlap_x, h_new))
                if seg.x_fin() > x_fin:
                    nouveaux.append(Segment(x_fin, seg.x_fin() - x_fin, seg.hauteur))

        self.segments = self._fusionner(nouveaux)

    def annuler(self):
        """ Restaure la skyline à l'état avant le dernier mettre_a_jour (UNDO). """
        self.segments = self._historique.pop()


    @staticmethod
    def _fusionner(segments):
        """ Fusionne les segments adjacents de même hauteur. """
        if not segments:
            return segments
        fusionne = [Segment(segments[0].x, segments[0].largeur, segments[0].hauteur)]
        for seg in segments[1:]:
            if seg.hauteur == fusionne[-1].hauteur:
                fusionne[-1].largeur += seg.largeur
            else:
                fusionne.append(Segment(seg.x, seg.largeur, seg.hauteur))
        return fusionne

    def affiche(self):
        print(f"Skyline ({len(self.segments)} segments) : {self.segments}")
