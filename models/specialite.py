class Specialite:
    def __init__(self, id, nom):
        self.id = id
        self.nom = nom

    def to_dict(self):
        return vars(self)