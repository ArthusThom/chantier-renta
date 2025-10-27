from django import forms

class EstimationForm(forms.Form):
    periode = forms.CharField(label="Période du chantier", max_length=100)
    nom_chantier = forms.CharField(label="Nom du chantier", max_length=100)
    type_prestation = forms.CharField(label="Type de prestation", max_length=100)
    heures_prevues = forms.FloatField(label="Heures travaillées prévues")
    heures_reelles = forms.FloatField(label="Heures travaillées réelles")
    cout_horaire = forms.FloatField(label="Coût horaire moyen employé (€)")
    charges = forms.FloatField(label="Charges sociales (%)")
    conso_prev = forms.FloatField(label="Consommation carburant prévue (L)")
    conso_reelle = forms.FloatField(label="Consommation carburant réelle (L)")
    prix_carburant = forms.FloatField(label="Coût carburant moyen (€/L)")
    cout_lubrifiants = forms.FloatField(label="Coût lubrifiants et fluides (€)")
    cout_entretien = forms.FloatField(label="Coût entretien matériel (€)")
    cout_amortissement = forms.FloatField(label="Coût amortissement matériel (€)")
    quote_part = forms.FloatField(label="Quote-part assurance & stockage (€)")
    cout_materiaux = forms.FloatField(label="Coût total matériaux & sous-traitants (€)")
    prix_facture = forms.FloatField(label="Prix facturé au client (€)")
    
def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    for field in self.fields.values():
        field.widget.attrs.update({
            'class': 'form-control',
            'placeholder': field.label
        })
