import os
import django
import sys
from datetime import date, timedelta

# Configure Django
sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core_erp.settings')
django.setup()

from gestao.models import Cliente, Processo, TipoVisto, Fatura, Parcela, Pagamento, Lead, Despesa, EtapaProcesso, EtapaPadrao

def generate_demo_data():
    print("Gerando dados de simulação (G IMIGRA)...")

    # 1. Criar Visto EB-2 NIW se não existir
    eb2, _ = TipoVisto.objects.get_or_create(
        codigo='EB2NIW', 
        defaults={'nome': 'EB-2 NIW (Interesse Nacional)', 'taxa_uscis_padrao': 715.00}
    )

    # 2. Criar Cliente de Simulação
    cliente, created = Cliente.objects.update_or_create(
        email='cliente@exemplo.com',
        defaults={
            'nome': 'João Silva das Neves',
            'telefone': '+55 11 99999-8888',
            'passaporte': 'BR123456',
            'nacionalidade': 'Brasileiro'
        }
    )
    print(f"Cliente: {cliente.nome}")

    # 3. Criar Processo
    processo, _ = Processo.objects.get_or_create(
        cliente=cliente,
        tipo_visto=eb2,
        defaults={'status': 'QUALIFICACAO'}
    )

    # Gerar checklist para o processo
    if not processo.etapas.exists():
        for ep in eb2.etapas_padrao.all():
            EtapaProcesso.objects.create(
                processo=processo, ordem=ep.ordem, titulo=ep.titulo, descricao=ep.descricao
            )
        # Concluir as duas primeiras
        e1 = processo.etapas.first()
        if e1: e1.concluida = True; e1.save()

    # 4. Criar Fatura Profissional
    fatura, _ = Fatura.objects.get_or_create(
        cliente=cliente,
        processo=processo,
        defaults={'total_fatura': 5000.00, 'status': 'ABERTO'}
    )

    if not fatura.parcelas.exists():
        Parcela.objects.create(fatura=fatura, num_parcela=1, data_vencimento=date.today(), valor_parcela=2500.00)
        Parcela.objects.create(fatura=fatura, num_parcela=2, data_vencimento=date.today() + timedelta(days=30), valor_parcela=2500.00)

    # 5. Criar alguns Leads (CRM)
    Lead.objects.get_or_create(nome='Maria Oliveira', telefone='12345', status='NOVO', interesse=eb2)
    Lead.objects.get_or_create(nome='Carlos Diniz', telefone='54321', status='PROPOSTA', interesse=eb2)

    # 6. Criar algumas Despesas (Contas a Pagar)
    Despesa.objects.get_or_create(descricao='Aluguel Escritório Miami', categoria='ALUGUEL', valor=1200.00, data_vencimento=date.today() + timedelta(days=5))
    Despesa.objects.get_or_create(descricao='Assinatura Adobe Acrobat', categoria='SOFTWARE', valor=60.00, data_vencimento=date.today(), pago=True)

    print("--- SIMULAÇÃO CONCLUÍDA COM SUCESSO ---")
    print(f"Acesse o Dashboard: http://127.0.0.1:8000/admin/")
    print(f"Portal do Cliente Login: cliente@exemplo.com / Passaporte: {cliente.passaporte}")
    print(f"Portal do Cliente URL: http://127.0.0.1:8000/portal/")

if __name__ == "__main__":
    generate_demo_data()
