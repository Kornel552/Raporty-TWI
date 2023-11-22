from django.db import models
from django.conf import settings
from django.utils import timezone
from datetime import datetime

class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class OpcjaSzkolenia(models.Model):
    nazwa = models.CharField(max_length=100)
    dni = models.PositiveIntegerField(unique=True)

    def __str__(self):
        return f"{self.nazwa}"

class Uczen(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    planned_start = models.DateField()
    planned_end = models.DateField()
    ilosc_szkolen = models.ForeignKey(
        OpcjaSzkolenia,
        on_delete=models.CASCADE,
        related_name='uczniowie'
    )
    category = models.ForeignKey(Category, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.name} {self.last_name}"

    def oblicz_pozostaly_czas(self):
        if isinstance(self.planned_end, str):
            # Konwersja ciągu znaków na datę
            planned_end_date = datetime.strptime(self.planned_end, '%d-%m-%Y').date()
        else:
            planned_end_date = self.planned_end

        pozostaly_czas = (planned_end_date - timezone.now().date()).days


        return pozostaly_czas


class Szkolenie(models.Model):
    data = models.DateField()
    uczen = models.ForeignKey('Uczen', related_name='szkolenie', on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return str(self.data)


class BrakSzkolenia(models.Model):
    data = models.DateField()
    uczen = models.ForeignKey('Uczen', related_name='brak_szkolenia', on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return str(self.data)


class Nieobecnosc(models.Model):
    data = models.DateField()
    uczen = models.ForeignKey('Uczen', related_name='nieobecnosc', on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return str(self.data)

class DniWolne(models.Model):
    data = models.DateField()
    uczen = models.ForeignKey('Uczen', related_name='dzien_wolny', on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return str(self.data)

class Audyt(models.Model):
    data = models.DateField()
    uczen = models.ForeignKey('Uczen', related_name='audyt', on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return str(self.data)

class Tekst(models.Model):
    tresc = models.TextField()
    uczen = models.ForeignKey(Uczen, on_delete=models.CASCADE, null=True, blank=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def __str__(self):
        return self.tresc