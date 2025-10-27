from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.core.mail import EmailMessage
from .forms import EstimationForm
from reportlab.pdfgen import canvas
from io import BytesIO


def home(request):
    return render(request, 'pages/home.html')


def estimation(request):
    resultats = None

    if request.method == "POST":
        form = EstimationForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data

            # Variables de base
            heures_prevues = data['heures_prevues']
            heures_reelles = data['heures_reelles']
            cout_horaire = data['cout_horaire']
            charges = data['charges']
            conso_prev = data['conso_prev']
            conso_reelle = data['conso_reelle']
            prix_carburant = data['prix_carburant']
            cout_lubrifiants = data['cout_lubrifiants']
            cout_entretien = data['cout_entretien']
            cout_amortissement = data['cout_amortissement']
            quote_part = data['quote_part']
            cout_materiaux = data['cout_materiaux']
            prix_facture = data['prix_facture']

            # Calculs
            cout_horaire_total = cout_horaire * (1 + charges / 100)
            cout_total_estime = (
                heures_prevues * cout_horaire_total
                + conso_prev * prix_carburant
                + cout_lubrifiants
                + cout_entretien
                + cout_amortissement
                + quote_part
                + cout_materiaux
            )
            cout_total_reel = (
                heures_reelles * cout_horaire_total
                + conso_reelle * prix_carburant
                + cout_lubrifiants
                + cout_entretien
                + cout_amortissement
                + quote_part
                + cout_materiaux
            )
            ecart_estime_vs_reel = cout_total_estime - cout_total_reel
            marge_brute = prix_facture - cout_total_reel
            marge_nette = marge_brute - (cout_total_reel * 0.1)
            taux_rentabilite = (marge_brute / prix_facture) * 100 if prix_facture else 0
            taux_horaire_reel = cout_total_reel / heures_reelles if heures_reelles else 0
            taux_horaire_facture = prix_facture / heures_reelles if heures_reelles else 0
            marge_prevue = (marge_brute / prix_facture) * 100 if prix_facture else 0
            ecart_marge_reelle_vs_prevue = taux_rentabilite - marge_prevue
            seuil_rentabilite_estime = cout_total_reel / 0.9
            seuil_rentabilite_reel = cout_total_reel / 0.85
            recommandation_ajustement_tarif = (
                ((seuil_rentabilite_reel - prix_facture) / prix_facture) * 100 if prix_facture else 0
            )

            # Résultats envoyés au template
            resultats = {
                "Coût horaire total employé (€)": round(cout_horaire_total, 2),
                "Coût total chantier estimé (€)": round(cout_total_estime, 2),
                "Coût total chantier réel (€)": round(cout_total_reel, 2),
                "Écart coût estimé vs réel (€)": round(ecart_estime_vs_reel, 2),
                "Marge brute (€)": round(marge_brute, 2),
                "Marge nette (€)": round(marge_nette, 2),
                "Taux de rentabilité (%)": round(taux_rentabilite, 2),
                "Taux horaire réel (€)": round(taux_horaire_reel, 2),
                "Taux horaire facturé (€)": round(taux_horaire_facture, 2),
                "Écart marge réelle vs prévue (%)": round(ecart_marge_reelle_vs_prevue, 2),
                "Seuil rentabilité réel (€)": round(seuil_rentabilite_reel, 2),
                "Recommandation ajustement tarif (%)": round(recommandation_ajustement_tarif, 2),
            }

            # 🔹 Sauvegarde dans la session pour PDF / email
            request.session['resultats'] = resultats
        else:
            resultats = None
    else:
        form = EstimationForm()

    return render(request, 'pages/estimation.html', {'form': form, 'resultats': resultats})


# ---------- PDF ----------
def export_pdf(request):
    """Génère un PDF téléchargeable à partir des résultats stockés"""
    resultats = request.session.get('resultats')
    if not resultats:
        return HttpResponse("Aucune donnée disponible pour le PDF.")

    # Création du PDF
    buffer = BytesIO()
    p = canvas.Canvas(buffer)
    p.setTitle("Estimation du chantier")

    p.drawString(100, 800, "Estimation du chantier")
    y = 770
    for key, value in resultats.items():
        p.drawString(100, y, f"{key}: {value}")
        y -= 20

    p.showPage()
    p.save()
    buffer.seek(0)

    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="estimation.pdf"'
    return response


# ---------- Email ----------
def send_email(request):
    """Envoie le PDF par email"""
    if request.method == "POST":
        email = request.POST.get("email")
        resultats = request.session.get('resultats')

        if not email or not resultats:
            return JsonResponse({"success": False, "message": "Données manquantes."})

        # Création du PDF en mémoire
        buffer = BytesIO()
        p = canvas.Canvas(buffer)
        p.setTitle("Estimation du chantier")
        y = 800
        p.drawString(100, y, "Estimation du chantier")
        y -= 20
        for key, value in resultats.items():
            p.drawString(100, y, f"{key}: {value}")
            y -= 20
        p.showPage()
        p.save()
        buffer.seek(0)

        # Envoi de l'email
        mail = EmailMessage(
            subject="Résultats de votre estimation de chantier",
            body="Veuillez trouver ci-joint le rapport PDF de votre estimation.",
            from_email="arthus@exemple.com",
            to=[email],
        )
        mail.attach("estimation.pdf", buffer.getvalue(), "application/pdf")
        mail.send(fail_silently=True)

        return JsonResponse({"success": True, "message": "Email envoyé avec succès."})

    return JsonResponse({"success": False, "message": "Méthode non autorisée."})
