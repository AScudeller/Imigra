from .models import LogNotificacao, Cliente
import logging

logger = logging.getLogger(__name__)

class NotificacaoService:
    @staticmethod
    def enviar_whatsapp(cliente, mensagem, parcela=None):
        """
        Simula o envio de WhatsApp e registra no log.
        Em produção, aqui entraria a integração com API (Twilio, Z-API, etc).
        """
        # Logica Mock de envio
        print(f"ENVIANDO WHATSAPP PARA {cliente.telefone}: {mensagem}")
        
        LogNotificacao.objects.create(
            cliente=cliente,
            parcela=parcela,
            tipo='WHATSAPP',
            mensagem=mensagem,
            status='SUCESSO' # Mockando sucesso
        )

    @staticmethod
    def enviar_email(cliente, assunto, mensagem, parcela=None):
        """
        Simula o envio de E-mail e registra no log.
        """
        print(f"ENVIANDO EMAIL PARA {cliente.email} [{assunto}]: {mensagem}")
        
        LogNotificacao.objects.create(
            cliente=cliente,
            parcela=parcela,
            tipo='EMAIL',
            mensagem=f"Assunto: {assunto} | Corpo: {mensagem}",
            status='SUCESSO'
        )

    @staticmethod
    def notificar_pagamento_recebido(pagamento):
        cliente = pagamento.cliente
        msg = f"Olá {cliente.nome}, recebemos seu pagamento de ${pagamento.valor_total} via {pagamento.metodo}. Obrigado!"
        NotificacaoService.enviar_whatsapp(cliente, msg)

    @staticmethod
    def notificar_fatura_criada(fatura):
        cliente = fatura.cliente
        msg = f"G IMIGRA: Uma nova fatura #{fatura.doc_entry} foi gerada no valor de ${fatura.total_fatura}. Acesse seu portal para detalhes."
        NotificacaoService.enviar_email(cliente, "Nova Fatura Gerada", msg)
