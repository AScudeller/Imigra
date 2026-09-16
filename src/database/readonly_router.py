"""
Read-Only Database Router
Protege o banco de dados de produção durante o desenvolvimento
"""

from django.conf import settings


class ReadOnlyRouter:
    """
    Router que força o banco de dados a operar em modo Read-Only
    durante o desenvolvimento, bloqueando qualquer operação de escrita.
    """
    
    def db_for_read(self, model, **hints):
        """
        Todas as operações de leitura vão para o banco 'default'
        """
        return 'default'
    
    def db_for_write(self, model, **hints):
        """
        Bloqueia todas as operações de escrita quando DB_READ_ONLY=True
        """
        if getattr(settings, 'DB_READ_ONLY', False):
            raise Exception(
                "\n"
                "=" * 60 + "\n"
                "⚠️  ESCRITA BLOQUEADA - MODO READ-ONLY ATIVO\n"
                "=" * 60 + "\n"
                "O banco de dados está protegido em modo Read-Only.\n"
                "Nenhuma operação de escrita é permitida durante o desenvolvimento.\n"
                "\n"
                "Para habilitar escritas (APENAS EM PRODUÇÃO):\n"
                "1. Edite o arquivo .env\n"
                "2. Altere DB_READ_ONLY=False\n"
                "3. Reinicie o servidor Django\n"
                "=" * 60
            )
        return 'default'
    
    def allow_relation(self, obj1, obj2, **hints):
        """
        Permite relações entre objetos do mesmo banco
        """
        return True
    
    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """
        Bloqueia migrações quando em modo Read-Only
        """
        if getattr(settings, 'DB_READ_ONLY', False):
            return False
        return True
