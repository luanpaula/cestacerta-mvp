from django.db import models
from django.core.exceptions import ValidationError

class FamiliaBeneficiaria(models.Model):
    nome_responsavel = models.CharField(max_length=150)
    cpf_responsavel = models.CharField(max_length=11, unique=True)
    membros = models.PositiveIntegerField(default=1)
    ativa = models.BooleanField(default=True)

    @property
    def cpf_mascarado(self):
        return f"***.{self.cpf_responsavel[3:6]}.{self.cpf_responsavel[6:9]}-**"

class LoteAlimento(models.Model):
    nome_item = models.CharField(max_length=120)
    quantidade = models.PositiveIntegerField()
    peso_total_kg = models.DecimalField(max_digits=6, decimal_places=2)
    data_validade = models.DateField()

class EntregaCesta(models.Model):
    familia = models.ForeignKey(FamiliaBeneficiaria, on_delete=models.RESTRICT)
    ciclo_referencia = models.CharField(max_length=12)
    data_hora_entrega = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("familia", "ciclo_referencia")
