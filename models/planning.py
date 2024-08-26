# models/planning.py
class Planning:
    def __init__(self, id_medecin, id_jour, heureDeAm, heureAAm, heureDePm, heureAPm):
        self.id_medecin = id_medecin
        self.id_jour = id_jour
        self.heureDeAm = heureDeAm
        self.heureAAm = heureAAm
        self.heureDePm = heureDePm
        self.heureAPm = heureAPm