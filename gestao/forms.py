from django import forms
from .models import Pagamento, Cliente, Parcela
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
