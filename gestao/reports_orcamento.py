from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, HRFlowable
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
from django.http import HttpResponse
from .models import Orcamento
from django.utils import timezone

def gerar_orcamento_pdf(request, orcamento_id):
    orc = Orcamento.objects.get(id=orcamento_id)
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="Orcamento_{orc.id}.pdf"'

    doc = SimpleDocTemplate(response, pagesize=A4, rightMargin=1.5*cm, leftMargin=1.5*cm, topMargin=1.5*cm, bottomMargin=1.5*cm)
    styles = getSampleStyleSheet()
    
    # Estilos Customizados SAP/TOTVS Style
    style_title = ParagraphStyle('Title', parent=styles['Normal'], fontSize=18, leading=22, alignment=TA_RIGHT, spaceAfter=10, textColor=colors.HexColor("#2C3E50"), fontName='Helvetica-Bold')
    style_header = ParagraphStyle('Header', parent=styles['Normal'], fontSize=10, leading=12, textColor=colors.grey)
    style_label = ParagraphStyle('Label', parent=styles['Normal'], fontSize=9, leading=11, fontName='Helvetica-Bold', textColor=colors.HexColor("#2C3E50"))
    style_value = ParagraphStyle('Value', parent=styles['Normal'], fontSize=10, leading=12)
    style_total = ParagraphStyle('Total', parent=styles['Normal'], fontSize=12, leading=14, fontName='Helvetica-Bold', alignment=TA_RIGHT)
    
    elements = []

    # --- CABEÇALHO (Logotipo e Título) ---
    header_data = [
        [Paragraph(f"<b>G IMIGRA</b><br/><font size='8'>Gestão de Imigração Profissional</font>", styles['Normal']), 
         Paragraph("PROPOSTA COMERCIAL", style_title)]
    ]
    header_table = Table(header_data, colWidths=[10*cm, 8*cm])
    header_table.setStyle(TableStyle([('VALIGN', (0,0), (-1,-1), 'TOP')]))
    elements.append(header_table)
    elements.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#2C3E50"), spaceBefore=5, spaceAfter=15))

    # --- INFORMAÇÕES DO CLIENTE E PROPOSTA ---
    data_info = [
        [Paragraph("CLIENTE", style_label), Paragraph("DETALHES DA PROPOSTA", style_label)],
        [Paragraph(f"{orc.cliente.nome}<br/>{orc.cliente.email}<br/>{orc.cliente.telefone}", style_value),
         Paragraph(f"Nº Proposta: {orc.id}<br/>Data: {orc.data_proposta.strftime('%d/%m/%Y')}<br/>Visto: {orc.tipo_visto.nome}", style_value)]
    ]
    info_table = Table(data_info, colWidths=[9*cm, 9*cm])
    info_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('BOTTOMPADDING', (0,0), (-1,0), 5),
    ]))
    elements.append(info_table)
    elements.append(Spacer(1, 1*cm))

    # --- TABELA DE VALORES (ESTILO GRID SAP) ---
    elements.append(Paragraph("RESUMO FANCEIRO", style_label))
    elements.append(Spacer(1, 0.2*cm))
    
    table_data = [
        [Paragraph("DESCRIÇÃO DO SERVIÇO", style_label), Paragraph("VALOR TOTAL (USD)", style_label)],
        [Paragraph(f"Assessoria Imigratória Completa - Visto {orc.tipo_visto.codigo}", style_value), 
         Paragraph(f"$ {orc.valor_total:,.2f}", style_value)],
        ["", ""], # Linha vazia para respiro
        [Paragraph("CONDIÇÕES DE PAGAMENTO", style_label), ""],
        [Paragraph(f"Entrada (Pagamento Inicial):", style_value), Paragraph(f"$ {orc.entrada:,.2f}", style_value)],
        [Paragraph(f"Saldo Parcelado ({orc.num_parcelas}x {orc.frequencia}):", style_value), 
         Paragraph(f"$ {(orc.valor_total - orc.entrada):,.2f}", style_value)],
    ]
    
    values_table = Table(table_data, colWidths=[14*cm, 4*cm])
    values_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#F2F4F4")),
        ('GRID', (0,0), (-1,1), 0.5, colors.grey),
        ('ALIGN', (1,0), (1,-1), 'RIGHT'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOTTOMPADDING', (0,1), (-1,-1), 10),
    ]))
    elements.append(values_table)
    
    # --- PLANO DE PARCELAS DETALHADO ---
    if orc.parcelas_preview.exists():
        elements.append(Spacer(1, 0.8*cm))
        elements.append(Paragraph("CRONOGRAMA DE PAGAMENTOS", style_label))
        elements.append(Spacer(1, 0.2*cm))
        
        plist_data = [[Paragraph("PARCELA", style_label), Paragraph("VENCIMENTO", style_label), Paragraph("VALOR", style_label)]]
        for p in orc.parcelas_preview.all().order_by('num_parcela'):
            label = "Entrada" if p.num_parcela == 0 else f"Parcela {p.num_parcela}"
            plist_data.append([label, p.data_vencimento.strftime('%d/%m/%Y'), f"$ {p.valor:,.2f}"])
            
        plist_table = Table(plist_data, colWidths=[6*cm, 6*cm, 6*cm])
        plist_table.setStyle(TableStyle([
            ('GRID', (0,0), (-1,-1), 0.2, colors.lightgrey),
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#F9EBEA") if orc.entrada > 0 else colors.HexColor("#F2F4F4")),
            ('ALIGN', (2,0), (2,-1), 'RIGHT'),
        ]))
        elements.append(plist_table)

    # --- RODAPÉ E NOTAS ---
    elements.append(Spacer(1, 2*cm))
    notes = "Notas: Esta proposta tem validade de 15 dias. Os valores não incluem taxas consulares estranhas à assessoria, salvo indicação em contrário. G IMIGRA - Excellence in Immigration Services."
    elements.append(Paragraph(notes, style_header))
    
    # Assinaturas
    elements.append(Spacer(1, 2*cm))
    sig_data = [
        [HRFlowable(width="6cm", thickness=1), HRFlowable(width="6cm", thickness=1)],
        [Paragraph("G IMIGRA - Consultoria", style_header), Paragraph("Aceite do Cliente", style_header)]
    ]
    sig_table = Table(sig_data, colWidths=[9*cm, 9*cm])
    sig_table.setStyle(TableStyle([('ALIGN', (0,0), (-1,-1), 'CENTER')]))
    elements.append(sig_table)

    doc.build(elements)
    return response
