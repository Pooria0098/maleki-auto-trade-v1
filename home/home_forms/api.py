from django import forms
from home.models import API


class APIForm(forms.ModelForm):

  def __init__(self, *args, **kwargs):
    try:
      user = kwargs.pop('user')
      self.user = user
    except:
      self.user = None
    super().__init__(*args, **kwargs)
    self.fields['parent'] = 'form_components'
    self.fields['segment'] = 'form_validation'

    self.fields['exchange'].widget.attrs.update({
      'class': "form-control",
      'required': True
    })
    self.fields['api_name'].widget.attrs.update({
      'required': True,
      'class': "form-control",
    })
    self.fields['api_key'].widget.attrs.update({
      'required': True,
      'class': "form-control",
    })
    self.fields['secret_key_hashed'].widget.attrs.update({
      'required': True,
      'class': "form-control",
    })
    self.fields['api_mode'].widget.attrs.update({
      'class': "form-control",
      'required': True,
    })

  class Meta:
    model = API
    fields = [
      'exchange',
      'api_name',
      'api_key',
      'secret_key_hashed',
      'api_mode',
    ]

  def save(self, commit=True):
    self.instance.user = self.user
    super(APIForm, self).save()
