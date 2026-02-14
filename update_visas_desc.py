import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core_erp.settings')
django.setup()

from gestao.models import TipoVisto

# Dicionário completo com descrições detalhadas e profissionais para cada categoria
descricoes_detalhadas = {
    "EB-1A": """Análise de Elegibilidade: Avaliação criteriosa do perfil do candidato com base nos critérios de Habilidade Extraordinária.
Coleta de Evidências: Orientação e revisão de documentos comprobatórios de prêmios, publicações e reconhecimento internacional.
Redação da Petição (I-140): Elaboração de argumentação jurídica robusta demonstrando a proeminência do candidato.
Cartas de Recomendação: Suporte na estruturação e revisão de cartas de especialistas da área.
Resposta a RFE: Assessoria completa em caso de Solicitação de Evidências Adicionais pelo USCIS.
Acompanhamento Processual: Monitoramento contínuo até a decisão final.""",

    "EB-2 NIW": """Análise de Mérito Nacional: Avaliação do impacto e importância nacional do empreendimento proposto.
Planejamento Estratégico: Definição da tese jurídica para isenção da oferta de emprego (National Interest Waiver).
Elaboração do Plano de Negócios/Profissional: Orientação para estruturar o Business Plan ou Professional Plan.
Petição I-140: Redação técnica focada nos critérios de Dhanasar (Mérito Substancial, Importância Nacional).
Documentação de Suporte: Organização de diplomas, históricos e cartas de recomendação.
Processamento Consular ou Ajuste de Status: Orientação pós-aprovação do I-140.""",

    "EB-3": """Certificação Laboral (PERM): Gestão completa do processo junto ao Department of Labor (DOL).
Determinação de Salário (PWD): Solicitação e análise da Prevailing Wage Determination.
Recrutamento: Assessoria na etapa de recrutamento obrigatório e documentação de compliance.
Petição I-140: Protocolo do pedido de imigração após aprovação do PERM.
Ajuste de Status/Processo Consular: Suporte na fase final para emissão do Green Card para o titular e dependentes.""",

    "O-1": """Avaliação de Extraordinariedade: Análise de prêmios, leads em produções e reconhecimento da mídia.
Advisory Opinion: Obtenção de pareceres de sindicatos ou grupos de pares (Peer Groups) nos EUA.
Contratos e Itinerário: Organização dos contratos de trabalho e plano de atividades para o período do visto.
Petição I-129: Preparação e protocolo do formulário para trabalhadores não-imigrantes.
Suporte ao Peticionário: Orientação ao agente ou empregador americano sobre suas responsabilidades.""",

    "L-1A": """Elegibilidade Corporativa: Análise da relação entre a empresa estrangeira e a filial americana (Qualifying Relationship).
Comprovação de Cargo: Documentação da função executiva ou gerencial do candidato no exterior e nos EUA.
Plano de Negócios (New Office): Para novos escritórios, auxílio na elaboração do plano de expansão.
Petição I-129 e Suplemento L: Preenchimento e protocolo do pacote completo.
Preparação para Entrevista: Treinamento para a entrevista consular focada em perguntas corporativas.""",

    "H-1B": """Labor Condition Application (LCA): Protocolo e certificação junto ao DOL garantindo condições salariais.
Registro na Loteria: Gestão da inscrição no sorteio anual do H-1B (se aplicável).
Petição I-129: Preparação do processo demonstrando a especialidade da ocupação (Specialty Occupation).
Equivalência Acadêmica: Orientação sobre evaluations de diplomas estrangeiros.
Compliance do Empregador: Assessoria sobre a manutenção do Public Access File.""",

    "F-1": """Emissão do I-20: Orientação para obtenção do formulário junto à instituição de ensino (DSO).
Formulário DS-160: Preenchimento e revisão do formulário de visto de não-imigrante.
Pagamento Taxa SEVIS: Instruções para pagamento da taxa I-901.
Preparação para Entrevista: Simulação de entrevista focada em demonstrar vínculos com o país de origem e intenção de estudo.
Vínculos Financeiros: Análise da documentação financeira para comprovação de custeio.""",

    "P-1": """Elegibilidade de Grupo/Atleta: Comprovação de reconhecimento internacional do grupo ou atleta.
Itinerário de Eventos: Organização do calendário de competições ou apresentações nos EUA.
Consulta Sindical: Obtenção da carta de não-objeção de organizações trabalhistas americanas.
Petição I-129: Protocolo do pedido para atletas e grupos de entretenimento.
Suporte a Equipe de Apoio (P-1S): Inclusão de pessoal essencial de suporte no processo.""",

    "K-1": """Petição I-129F: Preparação e protocolo da petição inicial para noivos estrangeiros.
Evidências de Relacionamento: Organização de fotos, mensagens e provas de encontros presenciais.
Processamento no NVC: Acompanhamento da transferência do caso para o Centro Nacional de Vistos.
Formulário DS-160 e Documentos: Auxílio na preparação para a entrevista consular.
Ajuste de Status: Orientação preliminar sobre os passos pós-casamento nos EUA.""",

    "T-Visa": """Declaração Pessoal: Auxílio na estruturação do relato da vítima (sem aconselhamento legal criminal).
Formulário I-914: Preenchimento do pedido de status de não-imigrante T.
Cooperação com Autoridades: Organização de evidências de colaboração com a lei (se aplicável).
Pedido de Perdão (Waiver): Se necessário, preparação do I-192.
Autorização de Trabalho: Inclusão do pedido de Employment Authorization Document (EAD).""",

    "U-Visa": """Certificação I-918 Suplemento B: Orientação sobre a obtenção da assinatura da autoridade policial/judicial.
Formulário I-918: Preparação completa da petição U.
Declaração de Sofrimento: Apoio na documentação do abuso físico ou mental sofrido.
Aprovação Condicional: Monitoramento da lista de espera e concessão de ação diferida.
Work Permit: Solicitação de autorização de trabalho baseada em caso pendente ou aprovado."""
}

print("Atualizando descrições detalhadas dos vistos...")

for codigo, descricao in descricoes_detalhadas.items():
    try:
        # Tenta buscar pelo código exato primeiro
        visto = TipoVisto.objects.filter(codigo=codigo).first()
        
        # Se não achar, tenta buscar 'contém' (ex: 'EB-2' pode achar 'EB-2 NIW')
        if not visto:
            visto = TipoVisto.objects.filter(codigo__icontains=codigo).first()
            
        if visto:
            visto.descricao = descricao
            visto.save()
            print(f"[OK] Atualizado: {visto.nome} ({visto.codigo})")
        else:
            print(f"[ALERTA] Visto nao encontrado para codigo: {codigo}")
            
    except Exception as e:
        print(f"[ERRO] Erro ao atualizar {codigo}: {str(e)}")

print("\nProcesso de atualização concluído!")
