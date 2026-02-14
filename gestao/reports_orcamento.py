from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, HRFlowable, Image
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
from django.http import HttpResponse
from .models import Orcamento, OrcamentoParcela
from django.utils import timezone
from decimal import Decimal
from datetime import timedelta

def gerar_orcamento_pdf(request, orcamento_id):
    orc = Orcamento.objects.get(id=orcamento_id)
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="Proposta_Comercial_{orc.id}.pdf"'

    doc = SimpleDocTemplate(response, pagesize=A4, rightMargin=1.5*cm, leftMargin=1.5*cm, topMargin=1.5*cm, bottomMargin=1.5*cm)
    styles = getSampleStyleSheet()
    
    # Cores Corporativas G IMIGRA (Deep Navy & Gold Accent)
    color_main = colors.HexColor("#002347")
    color_accent = colors.HexColor("#D4AF37")
    color_bg = colors.HexColor("#F9F9F9")
    
    # Estilos Customizados Premium
    style_title = ParagraphStyle('Title', parent=styles['Normal'], fontSize=22, leading=26, alignment=TA_RIGHT, textColor=color_main, fontName='Helvetica-Bold')
    style_subtitle = ParagraphStyle('SubTitle', parent=styles['Normal'], fontSize=10, leading=12, alignment=TA_RIGHT, textColor=colors.grey, spaceAfter=20)
    
    style_section = ParagraphStyle('Section', parent=styles['Normal'], fontSize=12, leading=14, fontName='Helvetica-Bold', textColor=color_main, borderPadding=5, spaceBefore=15, spaceAfter=10)
    style_label = ParagraphStyle('Label', parent=styles['Normal'], fontSize=8, leading=10, fontName='Helvetica-Bold', textColor=colors.grey)
    style_value = ParagraphStyle('Value', parent=styles['Normal'], fontSize=10, leading=12, textColor=colors.black)
    style_footer = ParagraphStyle('Footer', parent=styles['Normal'], fontSize=7, leading=9, alignment=TA_CENTER, textColor=colors.grey)
    
    elements = []

    # --- HEADER DESIGN (Stylized Logo) ---
    logo_part = [
        [Paragraph(f"<font size='28' color='#002347'><b>G</b></font><font size='28' color='#D4AF37'><b>IMIGRA</b></font>", styles['Normal'])],
        [Paragraph(f"<font size='8' color='grey'>IMMIGRATION EXCELLENCE</font>", styles['Normal'])]
    ]
    logo_table_styled = Table(logo_part, colWidths=[10*cm])
    logo_table_styled.setStyle(TableStyle([('LEFTPADDING', (0,0), (-1,-1), 0), ('BOTTOMPADDING', (0,0), (-1,-1), 0)]))

    header_data = [
        [
            logo_table_styled,
            [Paragraph("PROPOSTA COMERCIAL", style_title), Paragraph(f"REF: #ORC-{orc.id:04d} | DOC: {orc.id} | DATA: {orc.data_proposta.strftime('%d/%m/%Y')}", style_subtitle)]
        ]
    ]
    header_table = Table(header_data, colWidths=[10*cm, 8*cm])
    header_table.setStyle(TableStyle([('VALIGN', (0,0), (-1,-1), 'TOP'), ('ALIGN', (1,0), (1,0), 'RIGHT')]))
    elements.append(header_table)
    elements.append(HRFlowable(width="100%", thickness=2, color=color_main, spaceBefore=0, spaceAfter=20))

    # --- CLIENT INFORMATION BOX ---
    client_data = [
        [Paragraph("CONTATANTE / CLIENTE", style_label), Paragraph("SERVIÇO SOLICITADO", style_label)],
        [
            Paragraph(f"<b>{orc.cliente.nome.upper()}</b><br/>{orc.cliente.email}<br/>{orc.cliente.telefone}", style_value), 
            Paragraph(f"Visto: <b>{orc.tipo_visto.nome}</b><br/>Categoria: {orc.tipo_visto.codigo}", style_value)
        ],
    ]
    client_table = Table(client_data, colWidths=[9*cm, 9*cm])
    client_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), color_bg),
        ('LINEBELOW', (0,0), (-1,0), 1, color_main),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
    ]))
    elements.append(client_table)
    elements.append(Spacer(1, 0.5*cm))

    # --- SCOPE OF SERVICES ---
    elements.append(Paragraph("DETALHAMENTO DO ESCOPO", style_section))
    
    # Tratamento da descrição vinda do TipoVisto (convertendo quebras de linha para PDF)
    desc_raw = orc.tipo_visto.descricao if orc.tipo_visto.descricao else "Assessoria Especializada G IMIGRA - Consultoria documental completa e acompanhamento de etapas."
    desc_servico = desc_raw.replace('\n', '<br/>')
    
    scope_data = [
        [Paragraph("DESCRIÇÃO DOS SERVIÇOS DE ASSESSORIA", style_label), Paragraph("TOTAL (USD)", style_label)],
        [
            Paragraph(f"<b>Projeto:</b> {orc.tipo_visto.nome}<br/><br/>{desc_servico}", style_value),
            Paragraph(f"<b>USD {orc.valor_total:,.2f}</b>", ParagraphStyle('Right', parent=style_value, alignment=TA_RIGHT))
        ]
    ]
    scope_table = Table(scope_data, colWidths=[14*cm, 4*cm])
    scope_table.setStyle(TableStyle([
        ('GRID', (0,0), (-1,1), 0.5, colors.lightgrey),
        ('BACKGROUND', (0,0), (-1,0), color_main),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('TOPPADDING', (0,1), (-1,1), 10),
        ('BOTTOMPADDING', (0,1), (-1,1), 20),
    ]))
    elements.append(scope_table)
    elements.append(Spacer(1, 0.5*cm))

    # --- FINANCIAL SCHEDULE (AUTO-CALCULATED LOGIC) ---
    elements.append(Paragraph("CONDIÇÕES FINANCEIRAS & CRONOGRAMA", style_section))
    
    pay_data = [[
        Paragraph("ORDEM", style_label), 
        Paragraph("DESCRIÇÃO", style_label), 
        Paragraph("DATA PREVISTA", style_label), 
        Paragraph("VALOR (USD)", style_label)
    ]]
    
    # Check if DB has preview (Use stored parcels FIRST as they might contain manual edits)
    parcelas = orc.parcelas_preview.all().order_by('num_parcela')
    
    if parcelas.exists():
        for p in parcelas:
            desc_p = "Entrada / Sinal" if p.num_parcela == 1 and orc.num_parcelas > 1 else f"Pagamento {p.num_parcela:02d}"
            pay_data.append([
                Paragraph(f"{p.num_parcela:02d}", ParagraphStyle('Center', parent=style_value, alignment=TA_CENTER)),
                Paragraph(desc_p, style_value),
                Paragraph(p.data_vencimento.strftime('%d/%m/%Y'), ParagraphStyle('Center', parent=style_value, alignment=TA_CENTER)),
                Paragraph(f"US$ {p.valor:,.2f}", ParagraphStyle('Right', parent=style_value, alignment=TA_RIGHT))
            ])
            
    else:
        # DYNAMIC CALCULATION (Fallback only if no parcels generated)
        temp_parcelas = []
        data_atual = orc.data_proposta or timezone.now().date()
        saldo = orc.valor_total - orc.entrada
        
        # 1. Primeira Parcela (Entrada ou Total à Vista)
        if orc.num_parcelas >= 1:
            valor_prim = orc.entrada if orc.num_parcelas > 1 else orc.valor_total
            desc_prim = "Entrada / Pagamento 01" if orc.num_parcelas > 1 else "Pagamento à Vista"
            temp_parcelas.append({'num': 1, 'desc': desc_prim, 'venc': data_atual, 'valor': valor_prim})
        
        # 2. Parcelas Subsequentes (Total - 1)
        num_restantes = orc.num_parcelas - 1
        if num_restantes > 0 and saldo > 0:
            valor_parcela = (saldo / num_restantes).quantize(Decimal('0.01'))
            for i in range(1, num_restantes + 1):
                if orc.frequencia == 'SEMANAL':
                    data_venc = data_atual + timedelta(weeks=i)
                elif orc.frequencia == 'QUINZENAL':
                    data_venc = data_atual + timedelta(days=15 * i)
                else: # MENSAL
                    data_venc = data_atual + timedelta(days=30 * i)
                
                temp_parcelas.append({'num': i + 1, 'desc': f"Parcela {orc.frequencia.capitalize()} {i:02d}", 'venc': data_venc, 'valor': valor_parcela})
        
        # Add dynamic rows to table
        for p in temp_parcelas:
            pay_data.append([
                Paragraph(f"{p['num']:02d}", style_value),
                Paragraph(p['desc'], style_value),
                Paragraph(p['venc'].strftime('%d/%m/%Y'), style_value),
                Paragraph(f"<b>US$ {p['valor']:,.2f}</b>", ParagraphStyle('Right', parent=style_value, alignment=TA_RIGHT))
            ])

    # If both failed (shouldn't happen)
    if len(pay_data) == 1:
        pay_data.append([Paragraph("01", style_value), Paragraph("Pagamento Único", style_value), Paragraph("À Vista", style_value), Paragraph(f"<b>US$ {orc.valor_total:,.2f}</b>", style_value)])

    pay_table = Table(pay_data, colWidths=[2*cm, 7*cm, 5*cm, 4*cm])
    pay_table.setStyle(TableStyle([
        ('LINEBELOW', (0,0), (-1,0), 1.5, color_main),
        ('LINEBELOW', (0,1), (-1,-1), 0.5, colors.lightgrey),
        ('ALIGN', (3,0), (3,-1), 'RIGHT'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, color_bg]),
    ]))
    elements.append(pay_table)

    # --- TOTAL SUMMARY BOX ---
    elements.append(Spacer(1, 0.5*cm))
    summary_data = [
        ["", Paragraph("VALOR TOTAL DA PROPOSTA", ParagraphStyle('RightBold', parent=style_label, alignment=TA_RIGHT)), 
         Paragraph(f"USD {orc.valor_total:,.2f}", ParagraphStyle('RightTotal', parent=style_value, fontSize=14, fontName='Helvetica-Bold', alignment=TA_RIGHT, textColor=color_main))]
    ]
    summary_table = Table(summary_data, colWidths=[9*cm, 5*cm, 4*cm])
    summary_table.setStyle(TableStyle([('ALIGN', (1,0), (-1,-1), 'RIGHT'), ('VALIGN', (0,0), (-1,-1), 'MIDDLE')]))
    elements.append(summary_table)

    # --- TERMS & SIGNATURES ---
    elements.append(Spacer(1, 2*cm))
    elements.append(Paragraph("TERMOS DE ACEITE", style_section))
    terms = """Esta proposta contempla exclusivamente os honorários de assessoria imigratória. Taxas governamentais (USCIS), traduções juramentadas, exames médicos e taxas consulares não estão inclusas e deverão ser pagas pelo contratante conforme a demanda de cada etapa. A validade desta proposta é de 15 dias corridos a partir de sua emissão."""
    elements.append(Paragraph(terms, ParagraphStyle('Terms', parent=styles['Normal'], fontSize=8, leading=10, textColor=colors.grey)))
    
    elements.append(Spacer(1, 2.5*cm))
    
    # Signature Lines
    sig_data = [
        [HRFlowable(width=6*cm, thickness=1, color=color_main), Spacer(1, 2*cm), HRFlowable(width=6*cm, thickness=1, color=color_main)],
        [Paragraph(f"G IMIGRA SOLUTIONS", ParagraphStyle('Sig', parent=style_label, alignment=TA_CENTER)), "", 
         Paragraph(orc.cliente.nome.upper(), ParagraphStyle('Sig', parent=style_label, alignment=TA_CENTER))]
    ]
    sig_table = Table(sig_data, colWidths=[7*cm, 4*cm, 7*cm])
    elements.append(sig_table)

    # --- FOOTER ---
    elements.append(Spacer(1, 1*cm))
    footer_text = "G IMIGRA - Consultoria Assessoria Imigratória Internacional | www.gimigra.com | contact@gimigra.com"
    elements.append(Paragraph(footer_text, style_footer))

    doc.build(elements)
    return response
