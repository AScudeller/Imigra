import os
import django
import sys

# Configure Django
sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core_erp.settings')
django.setup()

from gestao.models import TipoVisto, EtapaPadrao, Processo, EtapaProcesso

def fix_visa_data():
    vistos_data = [
        ('ASILO', 'Asilo Político / Refúgio', 'Proteção para indivíduos perseguidos.'),
        ('B1B2', 'B-1/B-2 (Turismo e Negócios)', 'Visitantes temporários.'),
        ('E1', 'E-1 (Comerciante por Tratado)', 'Comércio internacional entre EUA e país do tratado.'),
        ('E2', 'E-2 (Investidor por Tratado)', 'Investidores de países com tratado.'),
        ('EB1A', 'EB-1A (Habilidades Extraordinárias)', 'Indivíduos no topo de sua área (Green Card).'),
        ('EB1B', 'EB-1B (Professores/Pesquisadores De Destaque)', 'Destaque acadêmico internacional.'),
        ('EB1C', 'EB-1C (Executivos Multinacionais)', 'Gerentes e executivos transferidos.'),
        ('EB2NIW', 'EB-2 NIW (Interesse Nacional)', 'Profissionais com dispensa de oferta de trabalho.'),
        ('EB3', 'EB-3 (Trabalhadores Qualificados/Profissionais)', 'Trabalhadores com oferta de emprego.'),
        ('EB5', 'EB-5 (Investidor Imigrante)', 'Investimento mínimo para criação de empregos.'),
        ('F1', 'F-1 (Estudante Acadêmico)', 'Estudantes em tempo integral.'),
        ('H1B', 'H-1B (Ocupação Especializada)', 'Trabalho profissional temporário.'),
        ('J1', 'J-1 (Intercâmbio)', 'Visitantes de intercâmbio/treinamento.'),
        ('K1', 'K-1 (Noivos de Cidadãos Americanos)', 'Casamento nos EUA dentro de 90 dias.'),
        ('L1A', 'L-1A (Executivo/Gerente Transferido)', 'Transferência interna na mesma empresa.'),
        ('L1B', 'L-1B (Conhecimento Especializado)', 'Trabalhadores com saber técnico único.'),
        ('O1A', 'O-1A (Habilidades Extraordinárias - Geral)', 'Ciências, educação, negócios ou atletismo.'),
        ('O1B', 'O-1B (Habilidades Extraordinárias - Artes)', 'Artes, cinema ou televisão.'),
        ('P1', 'P-1 (Atletas e Artistas)', 'Competição ou performance internacional.'),
        ('R1', 'R-1 (Trabalhadores Religiosos)', 'Membros de denominação religiosa.'),
        ('T', 'T Visa (Tráfico Humano)', 'Proteção para vítimas de tráfico.'),
        ('TN', 'TN (Profissionais do USMCA)', 'Trabalhadores do Canadá e México.'),
        ('U', 'U Visa (Vítimas de Crimes)', 'Colaboradores na investigação de crimes.'),
    ]

    print("Corrigindo nomes de vistos...")
    for codigo, nome, desc in vistos_data:
        visto, created = TipoVisto.objects.update_or_create(
            codigo=codigo,
            defaults={'nome': nome, 'descricao': desc}
        )

    # Checklist Geral
    etapas_gerais = [
        (1, 'Contratação e Onboarding', 'Assinatura do contrato e coleta de documentos iniciais.'),
        (2, 'Coleta de Dados Biográficos', 'Preenchimento de formulários de dados pessoais.'),
        (3, 'Análise de Documentação', 'Revisão técnica de toda a documentação recebida.'),
        (4, 'Preparação do Pacote', 'Montagem final do processo para envio.'),
        (5, 'Protocolo/Envio', 'Envio formal ao órgão competente.'),
        (6, 'Acompanhamento', 'Monitoramento do status e respostas a notificações.'),
    ]

    print("Populando checklists padrão...")
    for visto in TipoVisto.objects.all():
        if not visto.etapas_padrao.exists():
            for ordem, titulo, desc in etapas_gerais:
                EtapaPadrao.objects.create(
                    tipo_visto=visto,
                    ordem=ordem,
                    titulo=titulo,
                    descricao=desc
                )

    print("Atualizando processos existentes...")
    count = 0
    for p in Processo.objects.all():
        if not p.etapas.exists():
            etapas_modelo = p.tipo_visto.etapas_padrao.all()
            for modelo in etapas_modelo:
                EtapaProcesso.objects.create(
                    processo=p,
                    titulo=modelo.titulo,
                    descricao=modelo.descricao,
                    ordem=modelo.ordem
                )
            count += 1
    print(f"Checklist gerado para {count} processos existentes.")

if __name__ == "__main__":
    fix_visa_data()
