from django.db import models
from django.utils.translation import gettext_lazy as _

class ModeloContrato(models.Model):
    """
    Armazena o texto base para diferentes tipos de contratos.
    Usa placeholders como {{cliente_nome}}, {{passaporte}}, {{tipo_visto}}.
    """
    nome = models.CharField(_("Nome do Modelo"), max_length=100)
    tipo_visto = models.ForeignKey('TipoVisto', on_delete=models.SET_NULL, null=True, blank=True, verbose_name=_("Tipo de Visto Aplicável"))
    conteudo = models.TextField(_("Conteúdo do Contrato (Markdown/Texto)"))
    ativo = models.BooleanField(default=True)
    
    criado_em = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.nome} ({self.get_tipo_visto_display()})"

    class Meta:
        verbose_name = _("Modelo de Contrato")
        verbose_name_plural = _("Modelos de Contratos")
