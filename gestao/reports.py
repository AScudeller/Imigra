import io
from django.utils import timezone
from django.http import FileResponse, HttpResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.units import inch
from .models import Fatura, Parcela

def gerar_invoice_pdf(request, doc_entry):
    fatura = Fatura.objects.get(doc_entry=doc_entry)
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    # Cabeçalho
    p.setFont("Helvetica-Bold", 16)
    p.drawString(1 * inch, height - 1 * inch, "INVOICE - G IMIGRA")
    
    p.setFont("Helvetica", 10)
    p.drawString(1 * inch, height - 1.25 * inch, f"Data: {fatura.data_fatura.strftime('%m/%d/%Y')}")
    p.drawString(1 * inch, height - 1.4 * inch, f"Fatura #: {fatura.doc_entry}")
    
    # Dados do Cliente
    p.setFont("Helvetica-Bold", 12)
    p.drawString(1 * inch, height - 2 * inch, "DADOS DO CLIENTE:")
    p.setFont("Helvetica", 10)
    p.drawString(1 * inch, height - 2.2 * inch, f"Nome: {fatura.cliente.nome}")
    p.drawString(1 * inch, height - 2.35 * inch, f"Email: {fatura.cliente.email}")
    p.drawString(1 * inch, height - 2.5 * inch, f"Passaporte: {fatura.cliente.passaporte}")

    # Tabela de Valores
    p.setStrokeColorRGB(0.8, 0.8, 0.8)
    p.line(1 * inch, height - 3 * inch, width - 1 * inch, height - 3 * inch)
    
    p.setFont("Helvetica-Bold", 11)
    p.drawString(1 * inch, height - 3.2 * inch, "Descrição do Serviço")
    p.drawRightString(width - 1 * inch, height - 3.2 * inch, "Total (USD)")
    
    p.line(1 * inch, height - 3.3 * inch, width - 1 * inch, height - 3.3 * inch)
    
    p.setFont("Helvetica", 10)
    descricao = f"Honorários Profissionais - {fatura.processo.get_tipo_visto_display() if fatura.processo else 'Serviços Diversos'}"
    p.drawString(1 * inch, height - 3.5 * inch, descricao)
    p.drawRightString(width - 1 * inch, height - 3.5 * inch, f"$ {fatura.total_fatura:.2f}")

    # Parcelamento
    p.setFont("Helvetica-Bold", 11)
    p.drawString(1 * inch, height - 4.5 * inch, "CRONOGRAMA DE PAGAMENTO:")
    y = height - 4.8 * inch
    p.setFont("Helvetica", 9)
    for parcela in fatura.parcelas.all():
        status = "PAGO" if parcela.valor_pago >= parcela.valor_parcela else "PENDENTE"
        p.drawString(1.2 * inch, y, f"Parcela {parcela.num_parcela} - Venc: {parcela.data_vencimento.strftime('%m/%d/%Y')}")
        p.drawRightString(width - 1.2 * inch, y, f"$ {parcela.valor_parcela:.2f} ({status})")
        y -= 0.2 * inch

    # Totalização Final
    p.line(1 * inch, 2 * inch, width - 1 * inch, 2 * inch)
    p.setFont("Helvetica-Bold", 14)
    p.drawString(1 * inch, 1.7 * inch, "TOTAL A PAGAR:")
    p.drawRightString(width - 1 * inch, 1.7 * inch, f"$ {fatura.saldo_devedor():.2f}")
    
    p.setFont("Helvetica-Oblique", 8)
    p.drawCentredString(width / 2, 1 * inch, "Obrigado por confiar na G IMIGRA. Este documento é uma fatura oficial.")

    p.showPage()
    p.save()

    buffer.seek(0)
    return FileResponse(buffer, as_attachment=True, filename=f"Invoice_{fatura.doc_entry}.pdf")

def gerar_contrato_pdf(request, processo_id):
    from .models import Processo
    from .models_contracts import ModeloContrato
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable, Table, TableStyle
    from reportlab.lib.units import cm
    from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER
    
    processo = Processo.objects.get(id=processo_id)
    
    # Busca o melhor modelo (específico para o visto ou Geral)
    modelo = ModeloContrato.objects.filter(tipo_visto=processo.tipo_visto, ativo=True).first()
    if not modelo:
        modelo = ModeloContrato.objects.filter(tipo_visto__isnull=True, ativo=True).first()
    
    if not modelo:
        return HttpResponse("Nenhum modelo de contrato ativo encontrado.", status=404)

    # Lógica de Substituição de Variáveis
    texto_final = modelo.conteudo
    texto_final = texto_final.replace("{{cliente_nome}}", f"<b>{processo.cliente.nome.upper()}</b>")
    texto_final = texto_final.replace("{{passaporte}}", f"<b>{processo.cliente.passaporte or 'N/A'}</b>")
    texto_final = texto_final.replace("{{tipo_visto}}", f"<b>{processo.tipo_visto.nome if processo.tipo_visto else 'N/A'}</b>")
    texto_final = texto_final.replace("{{data_hoje}}", f"<b>{timezone.now().strftime('%d/%m/%Y')}</b>")

    # Configuração do Documento
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="Contrato_{processo.id}.pdf"'
    
    doc = SimpleDocTemplate(response, pagesize=A4, rightMargin=2*cm, leftMargin=2*cm, topMargin=2*cm, bottomMargin=2*cm)
    styles = getSampleStyleSheet()
    
    # Estilos Customizados
    style_tit = ParagraphStyle('ContractTitle', parent=styles['Normal'], fontSize=14, leading=18, alignment=TA_CENTER, fontName='Helvetica-Bold', spaceAfter=20)
    style_body = ParagraphStyle('ContractBody', parent=styles['Normal'], fontSize=10, leading=14, alignment=TA_JUSTIFY, spaceAfter=10)
    style_label = ParagraphStyle('SigLabel', parent=styles['Normal'], fontSize=9, alignment=TA_CENTER)
    
    elements = []
    
    # Cabeçalho Institucional Simples
    elements.append(Paragraph("G IMIGRA SOLUTIONS", ParagraphStyle('H', parent=style_tit, fontSize=16, color=colors.HexColor("#002347"))))
    elements.append(Paragraph("Consultoria Imigratória Internacional", ParagraphStyle('SH', parent=style_label, fontSize=8, color=colors.grey)))
    elements.append(Spacer(1, 0.5*cm))
    elements.append(HRFlowable(width="100%", thickness=1, color=colors.black, spaceAfter=1*cm))
    
    # Título do Contrato
    elements.append(Paragraph("CONTRATO DE PRESTAÇÃO DE SERVIÇOS", style_tit))
    
    # Conteúdo (Processando parágrafos)
    linhas = texto_final.split('\n')
    for linha in linhas:
        if linha.strip():
            elements.append(Paragraph(linha, style_body))
        else:
            elements.append(Spacer(1, 0.3*cm))
            
    # Rodapé de Assinaturas
    elements.append(Spacer(1, 3*cm))
    sig_data = [
        [HRFlowable(width=6*cm, thickness=1), "", HRFlowable(width=6*cm, thickness=1)],
        [Paragraph("G IMIGRA SOLUTIONS", style_label), "", Paragraph(processo.cliente.nome.upper(), style_label)],
        [Paragraph("CONTRATADA", style_label), "", Paragraph("CONTRATANTE", style_label)]
    ]
    sig_table = Table(sig_data, colWidths=[7*cm, 2*cm, 7*cm])
    elements.append(sig_table)
    
    doc.build(elements)
    return response
