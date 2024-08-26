from datetime import date

class Patient:
    def __init__(self, id, nom, prenom, email, password, cin, date_naissance, sexe, telephone, statut='I', date_inscription=None):
        self.id = id
        self.nom = nom
        self.prenom = prenom
        self.email = email
        self.password = password
        self.cin = cin
        self.date_naissance = date_naissance
        self.sexe = sexe
        self.telephone = telephone
        self.statut = statut
        self.date_inscription = date_inscription if date_inscription else date.today()

    def to_dict(self):
        return {
            "id": self.id,
            "nom": self.nom,
            "prenom": self.prenom,
            "email": self.email,
            "cin": self.cin,
            "date_naissance": str(self.date_naissance),
            "sexe": self.sexe,
            "telephone": self.telephone,
            "statut": self.statut,
            "date_inscription": str(self.date_inscription)
        }