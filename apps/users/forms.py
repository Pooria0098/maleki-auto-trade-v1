from django import forms
from apps.users.models import Profile
from apps.users.models import API


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        exclude = ('user', 'role', 'avatar',)

    def __init__(self, *args, **kwargs):
        super(ProfileForm, self).__init__(*args, **kwargs)

        for field_name, field in self.fields.items():
            self.fields[field_name].widget.attrs['placeholder'] = field.label
            self.fields[field_name].widget.attrs['class'] = 'form-control'
            self.fields[field_name].widget.attrs['required'] = False


class QuillFieldForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ('bio',)


class APIForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        try:
            user = kwargs.pop('user')
            self.user = user
        except:
            self.user = None
        super().__init__(*args, **kwargs)

        self.fields['exchange'].widget.attrs.update({
            'class': "form-control",
            # 'required': True
        })
        self.fields['market_type'].widget.attrs.update({
            'class': "form-control",
            # 'required': True
        })
        self.fields['api_name'].widget.attrs.update({
            # 'required': True,
            'class': "form-control",
        })
        self.fields['api_key'].widget.attrs.update({
            # 'required': False,
            'class': "form-control",
        })
        self.fields['secret_key_hashed'].widget.attrs.update({
            # 'required': True,
            'class': "form-control",
        })
        self.fields['api_mode'].widget.attrs.update({
            'class': "form-control",
            # 'required': True,
        })

    class Meta:
        model = API
        fields = [
            'exchange',
            'market_type',
            'api_name',
            'api_key',
            'secret_key_hashed',
            'api_mode',
        ]

    # def save(self, commit=True):
    #     self.instance.user = self.user
    #     super(APIForm, self).save()
