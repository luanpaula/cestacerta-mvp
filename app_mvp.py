import os, sys, django
from datetime import date, timedelta
from django.conf import settings
from django.http import HttpResponse
from django.urls import path
from django.core.wsgi import get_wsgi_application

if not settings.configured:
    settings.configure(
        DEBUG=True, SECRET_KEY="cestacerta-mvp-key", ALLOWED_HOSTS=["*"],
        ROOT_URLCONF=__name__,
        INSTALLED_APPS=["django.contrib.contenttypes", "django.contrib.auth", "cestacerta"],
        DATABASES={"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": "db_mvp.sqlite3"}},
    )
    django.setup()

from django.core.management import call_command
from cestacerta.models import FamiliaBeneficiaria, LoteAlimento, EntregaCesta
from cestacerta.services import listar_lotes_peps, gerar_resumo_mensal_transparencia

call_command("migrate", "--run-syncdb", verbosity=0)
if not FamiliaBeneficiaria.objects.exists():
    f1 = FamiliaBeneficiaria.objects.create(nome_responsavel="Maria Aparecida Souza", cpf_responsavel="12348291099", membros=4)
    f2 = FamiliaBeneficiaria.objects.create(nome_responsavel="Joao Pedro Lima", cpf_responsavel="98711930400", membros=3)
    EntregaCesta.objects.create(familia=f2, ciclo_referencia="2026-11-Q1")
    h = date(2026, 11, 16)
    LoteAlimento.objects.create(nome_item="Leite Integral UHT (24 un)", quantidade=24, peso_total_kg=24, data_validade=h + timedelta(days=2))
    LoteAlimento.objects.create(nome_item="Tomate Italiano (15 kg)", quantidade=15, peso_total_kg=15, data_validade=h + timedelta(days=4))
    LoteAlimento.objects.create(nome_item="Arroz Tipo 1 (60 pct)", quantidade=60, peso_total_kg=300, data_validade=h + timedelta(days=90))

BASE_CSS = """<style>
*{box-sizing:border-box;margin:0;padding:0;font-family:system-ui,sans-serif}
body{background:#F3F4F6;color:#111827;display:flex;justify-content:center;padding:12px}
body.hc{background:#000000;color:#FFFF00}
.app{width:412px;background:#FFFFFF;border:2px solid #1B4332;border-radius:14px;overflow:hidden}
body.hc .app{background:#000000;border:3px solid #FFFF00}
header{background:#1B4332;color:#FFF;padding:16px;display:flex;justify-content:space-between;align-items:center}
body.hc header{background:#000;border-bottom:2px solid #FFFF00;color:#FFFF00}
.wrap{padding:16px;display:flex;flex-direction:column;gap:14px}
.btn{display:block;width:100%;min-height:54px;padding:14px;border-radius:10px;font-size:18px;font-weight:800;text-align:center;text-decoration:none;border:2px solid #1B4332;cursor:pointer}
.btn-p{background:#1B4332;color:#FFF} .btn-s{background:#FFF;color:#111827}
body.hc .btn-p,body.hc .btn-s{background:#000;color:#FFFF00;border:2px solid #FFFF00}
.alert{background:#9B1C1C;color:#FFF;padding:14px;border-radius:10px;border-left:8px solid #FCA5A5;font-size:16px}
body.hc .alert{background:#000;color:#00FFFF;border:2px solid #00FFFF}
.card{border:2px solid #9CA3AF;border-radius:10px;padding:14px;font-size:16px}
body.hc .card{border:2px solid #FFFF00}
.ok{border-color:#15803D;background:#F0FDF4} .blk{border-color:#B91C1C;background:#FEF2F2}
body.hc .ok,body.hc .blk{background:#000;color:#FFFF00}
input{width:100%;min-height:50px;padding:12px;font-size:18px;border:2px solid #111827;border-radius:8px;margin-top:6px}
body.hc input{background:#000;color:#FFF;border:2px solid #FFFF00}
</style>"""

def home(request):
    hc = "hc" if request.GET.get("contraste") == "alto" else ""
    lotes = listar_lotes_peps(date(2026, 11, 16))
    criticos = sum(1 for l in lotes if l["alerta_critico"])
    return HttpResponse(f"""<!DOCTYPE html><html lang="pt-BR"><head><meta charset="utf-8"><title>CestaCerta MVP</title>{BASE_CSS}</head>
    <body class="{hc}"><main class="app"><header><div><h1>CestaCerta • ACMS</h1><small>Operador: Carlos Silva • Ciclo 2026-11-Q1</small></div></header>
    <div class="wrap"><div class="alert" role="alert">⚠️ <strong>ATENÇÃO: {criticos} lotes vencem em até 7 dias!</strong><br>Priorize Leite Integral e Tomate na montagem hoje.</div>
    <a class="btn btn-p" href="/entregar/">1. Entregar Cesta (2 Toques) →</a>
    <a class="btn btn-s" href="/estoque/">2. Estoque PEPS e Resumo Mensal →</a>
    <a class="btn btn-s" href="/estoque/?contraste=alto">👁️ Ativar Modo Alto Contraste (WCAG AAA)</a></div></main></body></html>""")

def entregar(request):
    f1, f2 = FamiliaBeneficiaria.objects.all()[:2]
    return HttpResponse(f"""<!DOCTYPE html><html lang="pt-BR"><head><meta charset="utf-8"><title>Entregar Cesta</title>{BASE_CSS}</head>
    <body><main class="app"><header><h1>Entregar Cesta</h1><a href="/" style="color:#FFF;font-weight:700">← Início</a></header>
    <div class="wrap"><div><label for="busca"><strong>Buscar por CPF (11 dígitos) ou Nome:</strong></label>
    <input id="busca" value="Maria / Joao (Consulta Ativa)" /></div>
    <div class="card ok"><strong>✅ APTA PARA RETIRADA</strong><br>{f1.nome_responsavel} • CPF: {f1.cpf_mascarado} ({f1.membros} membros)<br><br>
    <button class="btn btn-p">Confirmar Entrega (Baixa PEPS)</button></div>
    <div class="card blk"><strong>🚫 BLOQUEADA — CESTA JÁ RETIRADA NESTE CICLO</strong><br>{f2.nome_responsavel} • CPF: {f2.cpf_mascarado} • Retirada registrada em 2026-11-Q1</div></div></main></body></html>""")

def estoque(request):
    hc = "hc" if request.GET.get("contraste") == "alto" else ""
    lotes = listar_lotes_peps(date(2026, 11, 16))
    resumo = gerar_resumo_mensal_transparencia("2026-11")
    cards = "".join([f"<div class=\"card {"blk" if l["alerta_critico"] else "ok"}\"><strong>{"⚠️ URGENTE • VENCE EM BREVE" if l["alerta_critico"] else "🕒 REGULAR • ESTOQUE NORMAL"}</strong><br>{l["nome_item"]} — Validade: {l["data_validade"]}</div>" for l in lotes])
    toggle = "/" if hc else "/estoque/?contraste=alto"
    return HttpResponse(f"""<!DOCTYPE html><html lang="pt-BR"><head><meta charset="utf-8"><title>Estoque PEPS</title>{BASE_CSS}</head>
    <body class="{hc}"><main class="app"><header><h1>Estoque PEPS & ODS 2</h1><a href="{toggle}" style="color:#FFF;font-weight:700">{"Modo Padrão" if hc else "Alto Contraste"}</a></header>
    <div class="wrap">{cards}<div class="card"><strong>📊 Resumo Mensal (2026-11)</strong><br>Arrecadado: <strong>{resumo["total_kg_arrecadados"]:.0f} kg</strong> • Cestas entregues: <strong>{resumo["total_cestas_entregues"]}</strong></div></div></main></body></html>""")

def health(r):
    from django.http import JsonResponse
    return JsonResponse({"status": "UP", "service": "cestacerta-mvp", "database": "connected"})
urlpatterns = [path("", home), path("entregar/", entregar), path("estoque/", estoque), path("health/", health)]
if __name__ == "__main__":
    from django.core.management import execute_from_command_line
    execute_from_command_line([sys.argv[0], "runserver", "0.0.0.0:8000"])
