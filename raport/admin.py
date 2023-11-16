from django.contrib import admin
from .models import Category, Uczen, DniWolne, Szkolenie, BrakSzkolenia, Nieobecnosc, Tekst, Audyt, OpcjaSzkolenia

class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
admin.site.register(Category, CategoryAdmin)

class UczenAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'last_name')
admin.site.register(Uczen, UczenAdmin)

class SzkolenieAdmin(admin.ModelAdmin):
    list_display = ('data',)
admin.site.register(Szkolenie, SzkolenieAdmin)

class BrakSzkoleniaAdmin(admin.ModelAdmin):
    list_display = ('data',)
admin.site.register(BrakSzkolenia, BrakSzkoleniaAdmin)

class NieobecnoscAdmin(admin.ModelAdmin):
    list_display = ('data',)
admin.site.register(Nieobecnosc, NieobecnoscAdmin)

class DniWolneAdmin(admin.ModelAdmin):
    list_display = ('data',)
admin.site.register(DniWolne, DniWolneAdmin)

class AudytAdmin(admin.ModelAdmin):
    list_display = ('data',)
admin.site.register(Audyt, AudytAdmin)

class TekstAdmin(admin.ModelAdmin):
    list_display = ('tresc',)
admin.site.register(Tekst, TekstAdmin)

class OpcjaSzkoleniaAdmin(admin.ModelAdmin):
    list_display = ('dni',)
admin.site.register(OpcjaSzkolenia,OpcjaSzkoleniaAdmin)