# CestaCerta — Gestão de Banco de Alimentos Comunitário (MVP)

Aplicação web responsiva (*mobile-first*) desenvolvida em **Python 3.12 + Django 5.1** para apoiar a **Associação Comunitária Mãos Solidárias (ACMS)** no controle de doações perecíveis e na distribuição equitativa de cestas básicas (alinhado ao **ODS 2 — Fome Zero e Agricultura Sustentável**).

## Funcionalidades do MVP
- **Cadastro e Consulta de Famílias:** Busca instantânea por nome ou CPF mascarado (`***.456.789-**`).
- **Trava Quinzenal de Entrega:** Bloqueio automático (`UNIQUE(familia_id, ciclo_referencia)`) que impede retiradas duplicadas no mesmo ciclo de 15 dias.
- **Controle de Estoque PEPS:** Ordenação automática por data de validade (*Primeiro que Entra, Primeiro que Sai*) com alertas visuais para lotes que vencem em até 7 dias.
- **Resumo de Transparência:** Consolidação mensal de quilos arrecadados e cestas entregues para prestação de contas aos doadores.

## Arquitetura e Tecnologias
- **Padrão Arquitetural:** Monolítico Modular em Camadas (MVT — *Model-View-Template*).
- **Linguagem e Framework:** Python 3.12, Django 5.1, Bootstrap 5.3.
- **Banco de Dados:** PostgreSQL 16 (produção) / SQLite3 (desenvolvimento e testes).
- **Qualidade e CI:** `pytest` + `pytest-django` e GitHub Actions.

## Como Executar Localmente
1. Clone o repositório:
   `git clone https://github.com/seu-usuario/cestacerta-mvp.git`
2. Crie e ative o ambiente virtual:
   `python -m venv .venv && source .venv/bin/activate`
3. Instale as dependências e execute as migrações:
   `pip install -r requirements.txt && python manage.py migrate`
4. Execute os testes automatizados:
   `pytest`# cestacerta-mvp
