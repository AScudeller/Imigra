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
    from .models import Processo, ModeloContrato
    processo = Processo.objects.get(id=processo_id)
    
    # Busca o melhor modelo (específico para o visto ou Geral)
    modelo = ModeloContrato.objects.filter(tipo_visto=processo.tipo_visto, ativo=True).first()
    if not modelo:
        modelo = ModeloContrato.objects.filter(tipo_visto='GERAL', ativo=True).first()
    
    if not modelo:
        return HttpResponse("Nenhum modelo de contrato ativo encontrado.", status=404)

    # Lógica de Substituição de Variáveis
    texto_final = modelo.conteudo
    texto_final = texto_final.replace("{{cliente_nome}}", processo.cliente.nome.upper())
    texto_final = texto_final.replace("{{passaporte}}", processo.cliente.passaporte or "N/A")
    texto_final = texto_final.replace("{{tipo_visto}}", processo.get_tipo_visto_display())
    texto_final = texto_final.replace("{{data_hoje}}", timezone.now().strftime('%d/%m/%Y'))

    # Gerar PDF
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    
    p.setFont("Helvetica-Bold", 14)
    p.drawCentredString(width/2, height - 1*inch, "CONTRATO DE PRESTAÇÃO DE SERVIÇOS")
    
    p.setFont("Helvetica", 11)
    text_object = p.beginText(1*inch, height - 1.5*inch)
    text_object.setFont("Helvetica", 11)
    
    # Quebra de linha simples para o conteúdo
    lines = texto_final.split('\n')
    for line in lines:
        text_object.textLine(line)
    
    p.drawText(text_object)
    
    # Espaço para Assinaturas
    y = 3*inch
    p.line(1*inch, y, 3*inch, y)
    p.drawString(1*inch, y - 0.2*inch, "Contrante: " + processo.cliente.nome)
    
    p.line(width - 3*inch, y, width - 1*inch, y)
    p.drawString(width - 3*inch, y - 0.2*inch, "Contratada: G IMIGRA")

    p.showPage()
    p.save()
    buffer.seek(0)
    return FileResponse(buffer, as_attachment=True, filename=f"Contrato_{processo.cliente.nome.replace(' ', '_')}.pdf")
