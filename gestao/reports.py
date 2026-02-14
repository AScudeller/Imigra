import io
import re
from django.utils import timezone
from django.http import FileResponse, HttpResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.units import inch
from .models import Fatura, Parcela

def gerar_invoice_pdf(request, doc_entry):
    from django.shortcuts import render, get_object_or_404
    fatura = get_object_or_404(Fatura, doc_entry=doc_entry)
    return render(request, 'gestao/admin/invoice_print.html', {'fatura': fatura})

def gerar_contrato_pdf(request, processo_id):
    from .models import Processo
    from .models_contracts import ModeloContrato
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable, Table, TableStyle, PageBreak
    from reportlab.lib.units import cm
    from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER, TA_RIGHT
    
    processo = Processo.objects.get(id=processo_id)
    
    # VALIDAÇÃO: Verificar se existe orçamento vinculado e aprovado
    if not processo.orcamento:
        return HttpResponse(
            "<h1>Erro: Contrato não pode ser gerado</h1>"
            "<p>Este processo não possui um orçamento vinculado. Por favor, vincule um orçamento aprovado antes de gerar o contrato.</p>"
            "<p><a href='/admin/gestao/processo/{}/change/'>Voltar ao Processo</a></p>".format(processo_id),
            status=400
        )
    
    if processo.orcamento.status != 'ACEITO':
        return HttpResponse(
            "<h1>Erro: Orçamento não aprovado</h1>"
            "<p>O orçamento vinculado a este processo ainda não foi aceito pelo cliente. Status atual: <strong>{}</strong></p>"
            "<p>Por favor, aguarde a aprovação do orçamento antes de gerar o contrato.</p>"
            "<p><a href='/admin/gestao/orcamento/{}/change/'>Ver Orçamento</a></p>".format(
                processo.orcamento.get_status_display(), processo.orcamento.id
            ),
            status=400
        )
    
    # Busca o contrato padrão ativo (único para todos os vistos)
    modelo = ModeloContrato.objects.filter(ativo=True).first()
    
    if not modelo:
        return HttpResponse(
            "<h1>Erro: Nenhum modelo de contrato configurado</h1>"
            "<p>Por favor, configure o modelo de contrato padrão em: "
            "<a href='/admin/gestao/modelocontrato/'>Admin > Modelos de Contratos</a></p>",
            status=404
        )

    # Lógica de Substituição de Variáveis
    # Lógica de Substituição de Variáveis com REGEX (mais flexível)
    texto_final = modelo.conteudo
    
    # Suporta {{ cliente_nome }}, {{cliente_nome}}, e até tags HTML internas {{<b>cliente_nome</b>}}
    def replace_var(pattern, replacement, text):
        # Regex que aceita espaços e tags HTML opcionais entre as chaves e o nome da variável
        regex = r'\{\{\s*(?:<[^>]*>)*\s*' + pattern + r'\s*(?:<[^>]*>)*\s*\}\}'
        return re.sub(regex, replacement, text, flags=re.IGNORECASE)

    # 1. Nome (Completo)
    texto_final = replace_var('cliente_nome', f"<b>{processo.cliente.nome.upper()}</b>", texto_final)
    
    # 2. Tipo de Processo
    visto_nome = processo.tipo_visto.nome if processo.tipo_visto else 'N/A'
    texto_final = replace_var('tipo_visto', f"<b>{visto_nome}</b>", texto_final)
    
    # 3. Valor Total (do contrato)
    orcamento = processo.orcamento
    texto_final = replace_var('valor_total', f"<b>$ {orcamento.valor_total:,.2f}</b>", texto_final)
    
    # 4. Data
    data_formatada = timezone.now().strftime('%d/%m/%Y')
    texto_final = replace_var('data_hoje', f"<b>{data_formatada}</b>", texto_final)
    
    # 5. Forma de Pagamento (Complexa)
    pagamento_html = f"<br><b>Valor Total do Contrato:</b> $ {orcamento.valor_total:,.2f}<br>"
    if orcamento.entrada > 0:
        pagamento_html += f"<b>Valor de Entrada:</b> $ {orcamento.entrada:,.2f}<br>"
    
    parcelas = orcamento.parcelas_preview.all().order_by('num_parcela')
    if parcelas.exists():
        pagamento_html += f"<b>Plano de Parcelamento ({orcamento.num_parcelas} parcelas):</b><br>"
        pagamento_html += "<table border='1' width='100%' cellpadding='5' style='border-collapse:collapse;'>"
        pagamento_html += "<tr style='background-color:#f2f2f2;'><th>Parcela</th><th>Vencimento</th><th>Valor (USD)</th></tr>"
        for p in parcelas:
            pagamento_html += f"<tr><td>{p.num_parcela}ª Parcela</td><td>{p.data_vencimento.strftime('%d/%m/%Y')}</td><td>$ {p.valor:,.2f}</td></tr>"
        pagamento_html += "</table>"
    else:
        pagamento_html += "<b>Pagamento à vista.</b>"
        
    texto_final = replace_var('forma_pagamento', pagamento_html, texto_final)

    # Configuração do Documento
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="Contrato_{processo.id}.pdf"'
    
    doc = SimpleDocTemplate(response, pagesize=A4, rightMargin=2*cm, leftMargin=2*cm, topMargin=2*cm, bottomMargin=2*cm)
    styles = getSampleStyleSheet()
    
    # Estilos Customizados
    style_tit = ParagraphStyle('ContractTitle', parent=styles['Normal'], fontSize=14, leading=18, alignment=TA_CENTER, fontName='Helvetica-Bold', spaceAfter=20)
    style_body = ParagraphStyle('ContractBody', parent=styles['Normal'], fontSize=10, leading=14, alignment=TA_JUSTIFY, spaceAfter=10)
    style_label = ParagraphStyle('SigLabel', parent=styles['Normal'], fontSize=9, alignment=TA_CENTER)
    style_value_right = ParagraphStyle('ValRight', parent=styles['Normal'], fontSize=9, alignment=TA_RIGHT)
    style_value_center = ParagraphStyle('ValCenter', parent=styles['Normal'], fontSize=9, alignment=TA_CENTER)
    
    elements = []
    
    # Conteúdo vindo diretamente do editor
    
    # Processamento do texto do editor

    # Sanitização de HTML para o ReportLab
    # O Paragraph do ReportLab não suporta <img> e é sensível a tags mal formadas
    texto_final = re.sub(r'<img[^>]*>', '', texto_final)
    
    # Garantir quebras de linha entre parágrafos HTML para o split
    texto_final = texto_final.replace('</p>', '</p>\n')
    texto_final = texto_final.replace('</div>', '</div>\n')
    texto_final = texto_final.replace('</h1>', '</h1>\n')
    texto_final = texto_final.replace('</h2>', '</h2>\n')
    texto_final = texto_final.replace('</h3>', '</h3>\n')

    linhas = texto_final.split('\n')
    for linha in linhas:
        linha_limpa = linha.strip()
        if linha_limpa:
            # Suporte para quebra de página via variável
            if '{{quebra_pagina}}' in linha_limpa.lower():
                elements.append(PageBreak())
                continue
                
            try:
                # Tenta gerar o parágrafo
                elements.append(Paragraph(linha_limpa, style_body))
            except:
                # Fallback: Se der erro de sintaxe, remove todas as tags e tenta texto puro
                texto_puro = re.sub(r'<[^>]*>', '', linha_limpa)
                if texto_puro.strip():
                    elements.append(Paragraph(texto_puro, style_body))
        else:
            elements.append(Spacer(1, 0.3*cm))
    
    # --- QUADRO FINANCEIRO NO CONTRATO (Se houver Orçamento Aceito vinculado) ---
    orcamento = processo.orcamento # Usamos o orçamento já validado acima
    
    if orcamento:
        elements.append(Spacer(1, 0.5*cm))
        elements.append(Paragraph("ANEXO I - CONDIÇÕES FINANCEIRAS", style_tit))
        
        pay_data = [[Paragraph("PARCELA", style_label), Paragraph("VENCIMENTO", style_label), Paragraph("VALOR (USD)", style_label)]]
        
        parcelas = orcamento.parcelas_preview.all().order_by('num_parcela')
        
        if parcelas.exists():
            for p in parcelas:
                desc_p = "Entrada" if p.num_parcela == 1 and orcamento.num_parcelas > 1 else f"Parcela {p.num_parcela}"
                pay_data.append([
                    Paragraph(desc_p, style_value_center),
                    Paragraph(p.data_vencimento.strftime('%d/%m/%Y'), style_value_center),
                    Paragraph(f"$ {p.valor:,.2f}", style_value_right)
                ])
        else:
             pay_data.append([Paragraph("Total", style_value_center), Paragraph("À Vista", style_value_center), Paragraph(f"$ {orcamento.valor_total:,.2f}", style_value_right)])

        pay_table = Table(pay_data, colWidths=[5*cm, 5*cm, 4*cm])
        pay_table.setStyle(TableStyle([
            ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#e0e0e0")),
            ('ALIGN', (2,0), (2,-1), 'RIGHT'),
        ]))
        elements.append(pay_table)
        elements.append(Spacer(1, 1*cm))
    
    doc.build(elements)
    return response
