import os
import django

# Configuração do ambiente Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core_erp.settings')
django.setup()

from gestao.models import TipoVisto

visitas_data = [
    {
        "codigo": "EB-1A",
        "nome": "Habilidade Extraordinária",
        "descricao": "Visto de imigrante para indivíduos com habilidades extraordinárias nas ciências, artes, educação, negócios ou atletismo. Não exige oferta de emprego nos EUA.",
        "taxa": 715.00
    },
    {
        "codigo": "EB-2 NIW",
        "nome": "National Interest Waiver",
        "descricao": "Visto para profissionais com grau avançado ou habilidade excepcional, cujas atividades são de interesse nacional dos EUA, dispensando oferta de emprego.",
        "taxa": 715.00
    },
    {
        "codigo": "EB-3",
        "nome": "Trabalhadores Qualificados",
        "descricao": "Visto para trabalhadores qualificados, profissionais e outros trabalhadores patrocinados por um empregador americano.",
        "taxa": 715.00
    },
    {
        "codigo": "O-1",
        "nome": "Habilidade Extraordinária (Não-Imigrante)",
        "descricao": "Visto temporário para indivíduos com alto nível de expertise nas ciências, educação, negócios ou atletismo.",
        "taxa": 460.00
    },
    {
        "codigo": "L-1A",
        "nome": "Executivo/Gerente Multinacional",
        "descricao": "Visto para transferência de executivos ou gerentes de empresas internacionais para filiais nos Estados Unidos.",
        "taxa": 460.00
    },
    {
        "codigo": "H-1B",
        "nome": "Ocupações Especializadas",
        "descricao": "Visto para trabalhadores em ocupações que requerem conhecimento altamente especializado e diploma de nível superior.",
        "taxa": 460.00
    },
    {
        "codigo": "F-1",
        "nome": "Estudante Acadêmico",
        "descricao": "Visto para estudantes matriculados em programas de graduação, pós-graduação ou cursos de idiomas aprovados pelos EUA.",
        "taxa": 160.00
    },
    {
        "codigo": "P-1",
        "nome": "Atletas e Artistas",
        "descricao": "Visto para atletas, artistas e grupos de entretenimento reconhecidos internacionalmente.",
        "taxa": 460.00
    },
    {
        "codigo": "T-Visa",
        "nome": "Tráfico Humano",
        "descricao": "Visto humanitário para vítimas de tráfico humano que auxiliam as autoridades na investigação desses crimes.",
        "taxa": 0.00
    },
    {
        "codigo": "U-Visa",
        "nome": "Vítimas de Crimes",
        "descricao": "Visto para vítimas de crimes graves (violência doméstica, etc.) que sofreram abuso físico/mental e colaboram com a lei.",
        "taxa": 0.00
    },
    {
        "codigo": "K-1",
        "nome": "Visto de Noivo(a)",
        "descricao": "Visto para estrangeiros que pretendem se casar com cidadãos americanos nos EUA em até 90 dias após a chegada.",
        "taxa": 265.00
    }
]

print("Iniciando cadastro dos tipos de visto...")

for data in visitas_data:
    visto, created = TipoVisto.objects.update_or_create(
        codigo=data["codigo"],
        defaults={
            "nome": data["nome"],
            "descricao": data["descricao"],
            "taxa_uscis_padrao": data["taxa"]
        }
    )
    if created:
        print(f"Criado: {data['codigo']} - {data['nome']}")
    else:
        print(f"Atualizado: {data['codigo']} - {data['nome']}")

print("\nCadastro concluído com sucesso!")
