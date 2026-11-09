from django import forms
from .models import Pagamento, Cliente, Parcela, AnexoCliente
from django.utils.translation import gettext_lazy as _


class PagamentoForm(forms.ModelForm):
    """
    Formulário principal para registro e baixa de pagamentos com seleção de parcelas.
    Inspirado em telas de Baixa de Contas a Receber (SAP/Totvs).
    """
    class Meta:
        model = Pagamento
        fields = ['cliente', 'data_pagamento', 'metodo', 'valor_total', 'referencia']
        widgets = {
            'data_pagamento': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'cliente': forms.Select(attrs={'class': 'form-control select2', 'data-placeholder': 'Selecione o Cliente'}),
            'metodo': forms.Select(attrs={'class': 'form-control'}),
            'valor_total': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'readonly': 'readonly'}), # Calculado via JS
            'referencia': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nº Comprovante / Cheque'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # O campo valor_total pode ser sobrescrito se o usuário quiser pagar um valor diferente do somatório das parcelas (adiantamento)
        self.fields['valor_total'].required = True


class FiltroParcelasForm(forms.Form):
    """
    Filtros para buscar parcelas na tela de baixa (ex: SAP 'Selection Criteria').
    """
    data_inicio = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}))
    data_fim = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}))
    status = forms.ChoiceField(choices=[('ABERTO', 'Aberto / Atrasado'), ('TODOS', 'Todos')], required=False, widget=forms.Select(attrs={'class': 'form-control'}))


class MultipleFileInput(forms.ClearableFileInput):
    """
    Widget que habilita a seleção de múltiplos arquivos simultaneamente (<input type="file" multiple>).
    Retorna o primeiro arquivo na validação unitária do ModelForm, enquanto todos os arquivos
    são processados em lote pelo Admin via request.FILES.getlist().
    """
    allow_multiple_selected = True

    def value_from_datadict(self, data, files, name):
        if files:
            file_list = files.getlist(name)
            if file_list:
                return file_list[0]
        return super().value_from_datadict(data, files, name)


class AnexoClienteAdminForm(forms.ModelForm):
    """
    Formulário da tela Adicionar/Editar Anexo do Cliente com suporte a múltiplos arquivos.
    """
    class Meta:
        model = AnexoCliente
        fields = '__all__'
        widgets = {
            'titulo': forms.TextInput(attrs={
                'class': 'vTextField anexo-form-titulo',
                'placeholder': 'Deixe em branco para usar automaticamente o nome de cada arquivo...',
                'style': 'width: 100%; max-width: 520px; padding: 8px 10px; border-radius: 6px;'
            }),
            'arquivo': MultipleFileInput(attrs={
                'multiple': True,
                'class': 'anexo-multi-file-input',
            }),
            'observacoes': forms.Textarea(attrs={
                'rows': 2,
                'placeholder': 'Observações opcionais sobre este(s) documento(s)...',
                'style': 'width: 100%; max-width: 520px; padding: 8px 10px; border-radius: 6px; resize: vertical;'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['titulo'].required = False


class AnexoClienteInlineForm(forms.ModelForm):
    """
    Formulário compacto e responsivo para o Inline de Anexos no cadastro de clientes.
    Também suporta selecionar múltiplos arquivos de uma vez em uma única linha.
    """
    class Meta:
        model = AnexoCliente
        fields = '__all__'
        widgets = {
            'titulo': forms.TextInput(attrs={
                'class': 'anexo-input-titulo',
                'placeholder': 'Opcional (usa nome do arquivo)...',
                'style': 'width: 100%; min-width: 120px; box-sizing: border-box; padding: 6px 8px; font-size: 13px; border-radius: 4px; border: 1px solid #ced4da;'
            }),
            'categoria': forms.Select(attrs={
                'class': 'anexo-select-categoria',
                'style': 'width: 100%; min-width: 110px; box-sizing: border-box; padding: 6px 6px; font-size: 12px; border-radius: 4px; border: 1px solid #ced4da;'
            }),
            'arquivo': MultipleFileInput(attrs={
                'multiple': True,
                'class': 'anexo-inline-multi-file',
            }),
            'observacoes': forms.TextInput(attrs={
                'class': 'anexo-input-obs',
                'placeholder': 'Notas / observações...',
                'style': 'width: 100%; min-width: 100px; box-sizing: border-box; padding: 6px 8px; font-size: 12px; border-radius: 4px; border: 1px solid #ced4da;'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['titulo'].required = False
