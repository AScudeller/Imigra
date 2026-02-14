import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core_erp.settings')
django.setup()

from gestao.models_contracts import ModeloContrato

contrato_texto = """
CONTRATO DE PRESTAÇÃO DE SERVIÇOS DE ASSESSORIA IMIGRATÓRIA

CONTRATADA: G IMIGRA SOLUTIONS, com sede administrativa e canais de atendimento oficiais, doravante denominada simplesmente CONTRATADA.

CONTRATANTE: {{cliente_nome}}, portador do passaporte nº {{passaporte}}, doravante denominado simplesmente CONTRATANTE.

As partes acima identificadas têm, entre si, justo e acertado o presente Contrato de Prestação de Serviços, que se regerá pelas seguintes cláusulas e condições:

CLÁUSULA PRIMEIRA - DO OBJETO
O presente contrato tem como objeto a prestação de serviços de assessoria e consultoria administrativa para o processo de solicitação de visto americano na categoria {{tipo_visto}}.

CLÁUSULA SEGUNDA - DAS OBRIGAÇÕES DA CONTRATADA
A CONTRATADA obriga-se a:
1. Analisar a documentação fornecida pelo CONTRATANTE;
2. Orientar sobre o preenchimento de formulários oficiais;
3. Realizar o acompanhamento das etapas burocráticas descritas no escopo do serviço.

CLÁUSULA TERCEIRA - DAS OBRIGAÇÕES DO CONTRATANTE
O CONTRATANTE obriga-se a fornecer todas as informações e documentos solicitados pela CONTRATADA de forma verídica e tempestiva, sob pena de atraso ou indeferimento do processo por culpa exclusiva do solicitante.

CLÁUSULA QUARTA - DOS HONORÁRIOS
Pelos serviços prestados, o CONTRATANTE pagará à CONTRATADA os valores acordados em proposta comercial anexa, seguindo o cronograma de pagamentos estipulado no sistema de gestão.

CLÁUSULA QUINTA - DA RESPONSABILIDADE
A CONTRATADA presta serviços de assessoria e meio. A decisão final sobre a concessão de qualquer visto é de competência exclusiva e soberana das autoridades imigratórias dos Estados Unidos (USCIS/Departamento de Estado), não podendo a CONTRATADA garantir o resultado positivo do pleito.

CLÁUSULA SEXTA - DO FORO
Para dirimir quaisquer controvérsias oriundas deste contrato, as partes elegem o foro da sede da CONTRATADA.

Data do Aceite: {{data_hoje}}
"""

print("Cadastrando Modelo de Contrato Padrão...")

modelo, created = ModeloContrato.objects.update_or_create(
    nome="Contrato Padrão G IMIGRA - Geral",
    defaults={
        "conteudo": contrato_texto,
        "ativo": True,
        "tipo_visto": None # Geral
    }
)

if created:
    print("Modelo de contrato criado com sucesso!")
else:
    print("Modelo de contrato atualizado!")
