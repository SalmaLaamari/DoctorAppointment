class Rendezvous:
    def __init__(self, id, medecin_id, patient_id, date_rdv, statut):
        self.id = id
        self.medecin_id = medecin_id
        self.patient_id = patient_id
        self.date_rdv = date_rdv
        self.statut = statut

    def to_dict(self):
        return {
            'id': self.id,
            'medecin_id': self.medecin_id,
            'patient_id': self.patient_id,
            'date_rdv': self.date_rdv.isoformat() if self.date_rdv else None,
            'statut': self.statut
        }