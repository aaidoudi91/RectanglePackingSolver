""" Structure de données Skyline pour le PRP. """

from models.segment import Segment

class Skyline:
    """ Profil supérieur des rectangles placés sous forme de segments horizontaux dans le conteneur. """

    def __init__(self, largeur, hauteur):
        self.largeur = largeur
        self.hauteur = hauteur
        self.segments = [Segment(0, largeur, 0)]
        self._historique = []

    def vallee(self):
        """ Retourne le segment le plus bas et plus à gauche (Bitner-Reingold), ou None si la skyline est complète. """
        hauteur_min = min(s.hauteur for s in self.segments)
        if hauteur_min == self.hauteur:
            return None
        for segment in self.segments:
            if segment.hauteur == hauteur_min:
                return segment
        return None

    def _detecter_vallees(self):
        """ Retourne tous les segments qui sont des vallées locales (plus bas que leurs voisins).
        Un segment de bord (premier ou dernier) est considéré vallée si son unique voisin est plus haut. """
        vallees = []
        n = len(self.segments)
        for i, segment in enumerate(self.segments):
            if segment.hauteur == self.hauteur:  # si segment plein alors pas une vallée
                continue
            hauteur_gauche = self.segments[i-1].hauteur if i > 0 else self.hauteur  # else satisfait si segment de bord
            hauteur_droite = self.segments[i+1].hauteur if i < n-1 else self.hauteur
            if segment.hauteur < hauteur_gauche and segment.hauteur < hauteur_droite:
                vallees.append(segment)
        return vallees

    def est_remplie(self):
        """ Retourne True si le conteneur est entièrement rempli. """
        return len(self.segments) == 1 and self.segments[0].hauteur == self.hauteur

    def vallee_plus_etroite(self):
        """ Retourne la vallée de largeur minimale parmi toutes les vallées (Hougardy), ou en cas d'égalité de largeur,
        retourne la plus basse, puis la plus à gauche. Retourne None si la skyline est complète. """
        if self.est_remplie():
            return None
        vallees = self._detecter_vallees()
        if not vallees:  # si pas de creux local strict alors retombe sur la plus basse à gauche
            return self.vallee()
        vallees.sort(key=lambda s: (s.largeur, s.hauteur, s.x))  # tri par largeur croissante, puis hauteur, puis x
        return vallees[0]

    def hauteur_plafond(self, vallee):
        """ Retourne la hauteur du plafond de la vallée (jusqu'à laquelle la vallée doit être remplie au minimum).
        Utilisée pour la Règle 1 de Hougardy (valley area check). """
        n = len(self.segments)
        for i, segment in enumerate(self.segments):
            if segment is vallee:
                hauteur_gauche = self.segments[i-1].hauteur if i > 0 else self.hauteur
                hauteur_droite = self.segments[i+1].hauteur if i < n-1 else self.hauteur
                return min(hauteur_gauche, hauteur_droite)
        return self.hauteur  # si pas de plafond, alors retourne la hauteur du conteneur

    def largeur_disponible(self, x_vallee, hauteur_vallee):
        """ Retourne la largeur totale disponible à partir de la coordonnée x de la vallée et sa hauteur.
        S'étend vers la droite tant que les segments adjacents sont à la même hauteur hauteur_vallee. """
        total = 0
        for segment in self.segments:
            if segment.x >= x_vallee and segment.hauteur == hauteur_vallee:
                total += segment.largeur
            elif segment.x >= x_vallee:
                break
        return total

    @staticmethod
    def _fusionner(segments):
        """ Fusionne les segments adjacents de même hauteur. """
        if not segments:
            return segments
        fusionne = [Segment(segments[0].x, segments[0].largeur, segments[0].hauteur)]
        for segment in segments[1:]:
            if segment.hauteur == fusionne[-1].hauteur:
                fusionne[-1].largeur += segment.largeur
            else:
                fusionne.append(Segment(segment.x, segment.largeur, segment.hauteur))
        return fusionne

    def mettre_a_jour(self, rectangle):
        """ Met à jour la skyline après le placement de rectangle. Sauvegarde l'état précédent pour le backtracking. """
        self._historique.append([Segment(segment.x, segment.largeur, segment.hauteur) for segment in self.segments])

        x_debut = rectangle.x
        x_fin = rectangle.x + rectangle.largeur
        h_new = rectangle.y + rectangle.hauteur
        nouveaux = []

        # Reconstruction de la skyline en vérifiant l'impact du rectangle sur les segments existant
        for segment in self.segments:
            if segment.x_fin() <= x_debut or segment.x >= x_fin:  # à gauche/droite du rectangle donc reste intact
                nouveaux.append(Segment(segment.x, segment.largeur, segment.hauteur))
            else:  # chevauchement du segment donc on le découpe en 1, 2 ou 3 sous-segments.
                if segment.x < x_debut:
                    nouveaux.append(Segment(segment.x, x_debut - segment.x, segment.hauteur))
                overlap_x = max(segment.x, x_debut)
                overlap_fin = min(segment.x_fin(), x_fin)
                nouveaux.append(Segment(overlap_x, overlap_fin - overlap_x, h_new))
                if segment.x_fin() > x_fin:
                    nouveaux.append(Segment(x_fin, segment.x_fin() - x_fin, segment.hauteur))

        self.segments = self._fusionner(nouveaux)  # regroupe les segments adjacents se retrouvant à la même hauteur

    def annuler(self):
        """ Restaure la skyline à l'état avant le dernier mettre_a_jour (pour le backtracking). """
        self.segments = self._historique.pop()

    def affiche(self):
        print(f"Skyline ({len(self.segments)} segments) : {self.segments}")
