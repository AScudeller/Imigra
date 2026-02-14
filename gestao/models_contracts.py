from django.db import models
from django.utils.translation import gettext_lazy as _

class ModeloContrato(models.Model):
    """
    Armazena o texto base do contrato padrão único.
    Usa placeholders como {{cliente_nome}}, {{passaporte}}, {{tipo_visto}}, {{valor_total}}.
    """
    nome = models.CharField(_("Nome do Modelo"), max_length=100, default="Contrato Padrão G IMIGRA")
    conteudo = models.TextField(_("Conteúdo do Contrato (HTML)"), 
                                 help_text=_("Use variáveis como {{cliente_nome}}, {{tipo_visto}}, {{valor_total}}, etc."))
    ativo = models.BooleanField(default=True, verbose_name=_("Ativo"))
    
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.nome} ({'Ativo' if self.ativo else 'Inativo'})"

    class Meta:
        verbose_name = _("Modelo de Contrato")
        verbose_name_plural = _("Modelos de Contratos")
