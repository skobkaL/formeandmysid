# apps/tools/forms.py
from django import forms
from .models import Tool, ToolMovement, Location, ToolCategory


class ToolForm(forms.ModelForm):
    class Meta:
        model = Tool
        fields = ['name', 'brand', 'model', 'inventory_number', 'category', 
                  'purchase_date', 'initial_cost', 'residual_cost', 'location', 'notes']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'brand': forms.TextInput(attrs={'class': 'form-control'}),
            'model': forms.TextInput(attrs={'class': 'form-control'}),
            'inventory_number': forms.TextInput(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'purchase_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'initial_cost': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'residual_cost': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'location': forms.Select(attrs={'class': 'form-select'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class IssueReturnForm(forms.ModelForm):
    class Meta:
        model = ToolMovement
        fields = ['employee', 'operation_type', 'from_location', 'to_location', 'notes']
        widgets = {
            'employee': forms.Select(attrs={'class': 'form-select'}),
            'operation_type': forms.Select(attrs={'class': 'form-select'}),
            'from_location': forms.Select(attrs={'class': 'form-select'}),
            'to_location': forms.Select(attrs={'class': 'form-select'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }
    
    def __init__(self, *args, **kwargs):
        tool = kwargs.pop('tool', None)
        super().__init__(*args, **kwargs)
        
        if tool:
            # Определяем доступную операцию
            if tool.status == 'in_stock':
                # Только выдача
                self.fields['operation_type'].choices = [('issue', 'Выдача')]
                self.fields['operation_type'].initial = 'issue'
                self.fields['operation_type'].widget.attrs['readonly'] = True
                self.fields['operation_type'].widget.attrs['class'] = 'form-select bg-light'
                # Скрываем from_location (не нужен при выдаче)
                self.fields['from_location'].widget = forms.HiddenInput()
                self.fields['to_location'].required = True
            elif tool.status == 'issued':
                # Только возврат
                self.fields['operation_type'].choices = [('return', 'Возврат')]
                self.fields['operation_type'].initial = 'return'
                self.fields['operation_type'].widget.attrs['readonly'] = True
                self.fields['operation_type'].widget.attrs['class'] = 'form-select bg-light'
                # Скрываем to_location (не нужен при возврате)
                self.fields['to_location'].widget = forms.HiddenInput()
                self.fields['from_location'].required = True