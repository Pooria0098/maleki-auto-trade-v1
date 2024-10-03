from django import forms
from apps.common.models import Sales



class SalesForm(forms.ModelForm):
    class Meta:
        model = Sales
        fields = '__all__'
    

    def __init__(self, *args, **kwargs):
        super(SalesForm, self).__init__(*args, **kwargs)

        for field_name, field in self.fields.items():
            self.fields[field_name].widget.attrs['placeholder'] = field.label
            self.fields[field_name].widget.attrs['class'] = 'form-control'
            self.fields[field_name].widget.attrs['required'] = False
            self.fields[field_name].widget.attrs['rows'] = '1'