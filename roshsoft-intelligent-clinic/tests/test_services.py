from types import SimpleNamespace

from app.services import clinical_support


def test_clinical_support_flags_configured_red_flag():
    patient = SimpleNamespace(allergies=None, current_medications=None)
    text = clinical_support(patient, "Chest pain since morning", "pulse 90")
    assert "URGENT" in text
    assert "doctor" in text.lower()


def test_clinical_support_includes_allergy_warning():
    patient = SimpleNamespace(allergies="Penicillin", current_medications="Medicine A")
    text = clinical_support(patient, "mild cough", "temperature 37")
    assert "Penicillin" in text
    assert "interactions" in text

