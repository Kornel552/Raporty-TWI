from django import forms
from .models import Uczen, Szkolenie, BrakSzkolenia, Nieobecnosc, DniWolne, Tekst, Audyt

class UczenForm(forms.ModelForm):
    class Meta:
        model = Uczen
        fields = '__all__'

class DateInput(forms.DateInput):
    input_type = 'date'

class LastActiveForm(forms.ModelForm):
    class Meta:
        model = Uczen
        exclude = ['user']
        widgets = {
            'planned_start': DateInput(),
            'planned_end': DateInput(),
        }
        labels = {
            'name': 'Imię',
            'last_name': 'Nazwisko',
            'planned_start': 'Planowany start',
            'planned_end': 'Planowany koniec',
            'ilosc_szkolen': 'Ilość dni szkoleniowych',
            'category': 'Zmiana'
        }

class SzkolenieForm(forms.ModelForm):
    class Meta:
        model = Szkolenie
        fields = ['data']
        widgets = {
            'data': forms.DateInput(attrs={'type': 'date'})
        }

class BrakSzkoleniaForm(forms.ModelForm):
    class Meta:
        model = BrakSzkolenia
        fields = ['data']
        widgets = {
            'data': forms.DateInput(attrs={'type': 'date'})
        }

class NieobecnoscForm(forms.ModelForm):
    class Meta:
        model = Nieobecnosc
        fields = ['data']
        widgets = {
            'data': forms.DateInput(attrs={'type': 'date'})
        }

class DniWolneForm(forms.ModelForm):
    class Meta:
        model = DniWolne
        fields = ['data']
        widgets = {
            'data': forms.DateInput(attrs={'type': 'date'})
        }

class AudytForm(forms.ModelForm):
    class Meta:
        model = Audyt
        fields = ['data']
        widgets = {
            'data': forms.DateInput(attrs={'type': 'date'})
        }

class SelectUczenForm(forms.Form):
    uczen = forms.ModelChoiceField(queryset=Uczen.objects.none(), empty_label="Wybierz ucznia")

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(SelectUczenForm, self).__init__(*args, **kwargs)
        if user is not None:
            self.fields['uczen'].queryset = Uczen.objects.filter(user=user)

class TekstForm(forms.ModelForm):
    class Meta:
        model = Tekst
        fields = ['tresc']

