import os
import django
import sys

# Configure Django
sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core_erp.settings')
django.setup()

from gestao.models import EtapaPadrao, EtapaProcesso

def comprehensive_fix():
    # Mapeamento de padrões quebrados observados na imagem
    replacements = {
        'Contrata?o': 'Contratação',
        'Contrata??o': 'Contratação',
        'Biogrficos': 'Biográficos',
        'Biogr?ficos': 'Biográficos',
        'formulrios': 'formulários',
        'formul?rios': 'formulários',
        'An?lise': 'Análise',
        'Documenta?o': 'Documentação',
        'Documenta??o': 'Documentação',
        't?cnica': 'técnica',
        't??cnica': 'técnica',
        'Revis?o': 'Revisão',
        'Revis??o': 'Revisão',
        'padr?o': 'padrão',
        'padr??o': 'padrão',
        'notifica??es': 'notificações',
        'notifica?es': 'notificações',
    }

    print("Iniciando correção manual e cirúrgica de acentuação...")

    # Corrigir Etapas Padrão
    eps = EtapaPadrao.objects.all()
    for ep in eps:
        for old, new in replacements.items():
            ep.titulo = ep.titulo.replace(old, new)
            ep.descricao = ep.descricao.replace(old, new)
        ep.save()

    # Corrigir Etapas de Processo
    evs = EtapaProcesso.objects.all()
    for ev in evs:
        for old, new in replacements.items():
            ev.titulo = ev.titulo.replace(old, new)
            ev.descricao = ev.descricao.replace(old, new)
        ev.save()
    
    # Tentativa de correção via caracteres Unicode se sobrar algo
    def clean_text(text):
        if not text: return text
        # Correções genéricas de fallback
        return text.replace('??o', 'ão').replace('?o', 'ão').replace('?a', 'á').replace('?i', 'í').replace('?e', 'é')

    for ep in EtapaPadrao.objects.all():
        ep.titulo = clean_text(ep.titulo)
        ep.descricao = clean_text(ep.descricao)
        ep.save()

    for ev in EtapaProcesso.objects.all():
        ev.titulo = clean_text(ev.titulo)
        ev.descricao = clean_text(ev.descricao)
        ev.save()

    print("Correções aplicadas com sucesso!")

if __name__ == "__main__":
    comprehensive_fix()
