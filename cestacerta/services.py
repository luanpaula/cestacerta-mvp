from datetime import date, timedelta
from django.db import transaction
from django.core.exceptions import ValidationError
from .models import FamiliaBeneficiaria, LoteAlimento, EntregaCesta

def listar_lotes_peps(data_referencia=None):
    hoje = data_referencia or date.today()
    limite_alerta = hoje + timedelta(days=7)
    lotes = LoteAlimento.objects.filter(quantidade__gt=0).order_by("data_validade")
    return [
        {
            "id": l.id,
            "nome_item": l.nome_item,
            "quantidade": l.quantidade,
            "data_validade": l.data_validade,
            "alerta_critico": l.data_validade <= limite_alerta,
        }
        for l in lotes
    ]

@transaction.atomic
def registrar_entrega_cesta(familia_id: int, ciclo_referencia: str) -> EntregaCesta:
    if EntregaCesta.objects.filter(familia_id=familia_id, ciclo_referencia=ciclo_referencia).exists():
        raise ValidationError("Cesta já retirada por esta família no ciclo quinzenal atual.")
    return EntregaCesta.objects.create(familia_id=familia_id, ciclo_referencia=ciclo_referencia)

import re
from django.db.models import Sum
from django.utils.html import escape

def gerar_resumo_mensal_transparencia(mes_referencia: str) -> dict:
    if not re.match(r"^\d{4}-(0[1-9]|1[0-2])$", mes_referencia):
        raise ValueError("Formato de período inválido. Utilize AAAA-MM.")
    ano, mes = map(int, mes_referencia.split("-"))
    total_kg = LoteAlimento.objects.filter(
        data_validade__year=ano, data_validade__month=mes
    ).aggregate(total=Sum("peso_total_kg"))["total"] or 0
    entregas = EntregaCesta.objects.filter(ciclo_referencia__startswith=mes_referencia)
    return {
        "periodo": escape(mes_referencia),
        "total_kg_arrecadados": float(total_kg),
        "total_cestas_entregues": entregas.count(),
        "familias_unicas_atendidas": entregas.values("familia_id").distinct().count(),
    }
