from datetime import date

class Medecin:
    def __init__(self, id, id_specialite, id_ville, nom, prenom, password, duree_rdv, prix, cliniquename, longitude, latitude, active, adresse, telephone, fax, statut):
        self.id = id
        self.id_specialite = id_specialite
        self.id_ville = id_ville
        self.nom = nom
        self.prenom = prenom
        self.password = password
        self.duree_rdv = duree_rdv
        self.prix = prix
        self.cliniquename = cliniquename
        self.longitude = longitude
        self.latitude = latitude
        self.active = active
        self.adresse = adresse
        self.telephone = telephone
        self.fax = fax
        self.statut = statut

    def to_dict(self):
        return vars(self)