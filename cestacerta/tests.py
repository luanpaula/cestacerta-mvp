import pytest
from datetime import date, timedelta
from django.core.exceptions import ValidationError
from cestacerta.models import FamiliaBeneficiaria, LoteAlimento
from cestacerta.services import listar_lotes_peps, registrar_entrega_cesta

@pytest.mark.django_db
def test_bloqueio_retirada_duplicada_mesmo_ciclo():
    familia = FamiliaBeneficiaria.objects.create(
        nome_responsavel="Maria Aparecida Souza",
        cpf_responsavel="12348291099",
        membros=4
    )
    assert familia.cpf_mascarado == "***.482.910-**"
    registrar_entrega_cesta(familia.id, "2026-11-Q1")
    with pytest.raises(ValidationError):
        registrar_entrega_cesta(familia.id, "2026-11-Q1")

@pytest.mark.django_db
def test_ordenacao_peps_e_alerta_sete_dias():
    hoje = date(2026, 11, 16)
    LoteAlimento.objects.create(nome_item="Arroz Tipo 1", quantidade=30, peso_total_kg=150, data_validade=hoje + timedelta(days=90))
    LoteAlimento.objects.create(nome_item="Leite Integral", quantidade=12, peso_total_kg=12, data_validade=hoje + timedelta(days=2))
    fila = listar_lotes_peps(data_referencia=hoje)
    assert fila[0]["nome_item"] == "Leite Integral"
    assert fila[0]["alerta_critico"] is True
    assert fila[1]["alerta_critico"] is False
