from django.shortcuts import render
from django.shortcuts import redirect
from django.contrib.auth.models import User
from django.contrib import auth
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from collections import defaultdict
from django.db.models.functions import ExtractWeek
from django.db.models import Count
from .models import Uczen, Szkolenie, BrakSzkolenia, Nieobecnosc, DniWolne, Tekst, Audyt
from .forms import LastActiveForm, SelectUczenForm, TekstForm
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
import matplotlib.ticker as ticker
from django.views.decorators.http import require_http_methods
from io import BytesIO
import base64
from datetime import timedelta

def signup_page(request):
    context = {}
    if request.method == 'POST':
        try:
            user = User.objects.get(username=request.POST['username'])
            context['error'] = 'Podana nazwa użytkownika już istnieje'
            return render(request, 'login/signup.html', context)
        except User.DoesNotExist:
            if request.POST['password1'] != request.POST['password2']:
                context['error'] = 'Podane hasła są różne!'
                return render(request, 'login/signup.html', context)
            else:
                user = User.objects.create_user(request.POST['username'], password=request.POST['password1'])
                auth.login(request, user)
                return redirect('home')
    else:
        return render(request, 'login/signup.html', context)

def login_page(request):
    context = {}
    if request.method == 'POST':
        user = auth.authenticate(username=request.POST['username'], password=request.POST['password'])
        if user is not None:
            auth.login(request, user)
            if request.POST.get('redir'):
                return redirect(f"{request.POST.get('redir')}")
            else:
                return redirect('home')
        else:
            context['error'] = 'Podane hasło lub login są błędne! Podaj poprawne dane.'
            if request.POST.get('redir'):
                context['next'] = 'Tylko zalogowani użytkonicy mają dostęp do tej strony!'
                context['nextURL'] = request.GET.get('next')
            return render(request, 'login/login.html', context)
    else:
        if request.GET.get('next'):
            context['next'] = 'Tylko zalogowani użytkonicy mają dostęp do tej strony!'
            context['nextURL'] = request.GET.get('next')
        return render(request, 'login/login.html', context)

def logout_page(request):
    if request.method == 'POST':
        auth.logout(request)
        return redirect('home')

def home(request):
    return render(request, 'home.html')


@login_required
def dodaj_szkolenie(request):
    wybrany_uczen_id = request.session.get('wybrany_uczen_id')
    if wybrany_uczen_id:
        wybrany_uczen = Uczen.objects.get(id=wybrany_uczen_id)
    else:
        wybrany_uczen = None

    if request.method == 'POST':
        if 'delete_tekst' in request.POST:
            tekst_ids = request.POST.getlist('tekst_ids')
            for tekst_id in tekst_ids:
                Tekst.objects.filter(id=tekst_id).delete()
            return redirect('dodaj_szkolenie')
        elif 'delete_dates' in request.POST:
            szkolenie_ids = request.POST.getlist('szkolenie_ids')
            for szkolenie_id in szkolenie_ids:
                Szkolenie.objects.filter(id=szkolenie_id).delete()
            brak_ids = request.POST.getlist('brak_ids')
            for brak_id in brak_ids:
                BrakSzkolenia.objects.filter(id=brak_id).delete()
            nieobecnosc_ids = request.POST.getlist('nieobecnosc_ids')
            for nieobecnosc_id in nieobecnosc_ids:
                Nieobecnosc.objects.filter(id=nieobecnosc_id).delete()
            wolne_ids = request.POST.getlist('wolne_ids')
            for wolne_id in wolne_ids:
                DniWolne.objects.filter(id=wolne_id).delete()
            audyt_ids = request.POST.getlist('audyt_ids')
            for audyt_id in audyt_ids:
                Audyt.objects.filter(id=audyt_id).delete()
            return redirect('dodaj_szkolenie')
        elif 'submit_szkolenie' in request.POST:
            data = request.POST.get('data')
            typ_zajec = request.POST.get('typ_zajec')
            if wybrany_uczen and data and typ_zajec:
                if typ_zajec == 'szkolenie':
                    Szkolenie.objects.create(data=data, uczen=wybrany_uczen)
                elif typ_zajec == 'brak_szkolenia':
                    BrakSzkolenia.objects.create(data=data, uczen=wybrany_uczen)
                elif typ_zajec == 'nieobecnosc':
                    Nieobecnosc.objects.create(data=data, uczen=wybrany_uczen)
                elif typ_zajec == 'dzien_wolny':
                    DniWolne.objects.create(data=data, uczen=wybrany_uczen)
                elif typ_zajec == 'audyt':
                    Audyt.objects.create(data=data, uczen=wybrany_uczen)
        elif 'submit_tekst' in request.POST:
            tekst_form = TekstForm(request.POST)
            if tekst_form.is_valid():
                nowy_tekst = tekst_form.save(commit=False)
                nowy_tekst.uczen = wybrany_uczen
                nowy_tekst.user = request.user
                nowy_tekst.save()

    szkolenia = Szkolenie.objects.filter(uczen=wybrany_uczen)
    braki_szkolenia = BrakSzkolenia.objects.filter(uczen=wybrany_uczen)
    nieobecnosci = Nieobecnosc.objects.filter(uczen=wybrany_uczen)
    dni_wolne = DniWolne.objects.filter(uczen=wybrany_uczen)
    audyty = Audyt.objects.filter(uczen=wybrany_uczen)
    teksty = Tekst.objects.filter(uczen=wybrany_uczen, user=request.user)

    if wybrany_uczen_id:
        wybrany_uczen = Uczen.objects.get(id=wybrany_uczen_id)
        liczba_szkolen = wybrany_uczen.szkolenie.count()  # liczy dni szkoleniowe
        calkowita_ilosc_szkolen = wybrany_uczen.ilosc_szkolen.dni  # całkowita ilość szkoleń

        # Obliczenie procentowego wykonania szkoleń
        procent_wykonania = round(((liczba_szkolen / calkowita_ilosc_szkolen * 100) if calkowita_ilosc_szkolen > 0 else 0),2)

    context = {
        'wybrany_uczen': wybrany_uczen,
        'szkolenia': szkolenia,
        'braki_szkolenia': braki_szkolenia,
        'nieobecnosci': nieobecnosci,
        'dni_wolne': dni_wolne,
        'audyty': audyty,
        'tekst_form': TekstForm(),
        'teksty': teksty,
        'calkowita_ilosc_szkolen': calkowita_ilosc_szkolen,
        'liczba_szkolen': liczba_szkolen,
        'procent_wykonania': procent_wykonania
    }

    return render(request, 'dodaj_szkolenie.html', context)

    szkolenia = Szkolenie.objects.filter(uczen=wybrany_uczen)
    braki_szkolenia = BrakSzkolenia.objects.filter(uczen=wybrany_uczen)
    nieobecnosci = Nieobecnosc.objects.filter(uczen=wybrany_uczen)
    dni_wolne = DniWolne.objects.filter(uczen=wybrany_uczen)
    teksty = Tekst.objects.filter(uczen=wybrany_uczen, user=request.user)

    context = {
        'wybrany_uczen': wybrany_uczen,
        'szkolenia': szkolenia,
        'braki_szkolenia': braki_szkolenia,
        'nieobecnosci': nieobecnosci,
        'dni_wolne': dni_wolne,
        'tekst_form': TekstForm(), # Formularz do dodawania tekstu
        'teksty': teksty,
    }

    return render(request, 'dodaj_szkolenie.html', context)

@login_required
def wybierz_ucznia(request):
    if request.method == 'POST':
        form = SelectUczenForm(request.POST, user=request.user)
        if form.is_valid():
            uczen = form.cleaned_data['uczen']
            request.session['wybrany_uczen_id'] = uczen.id
            return redirect('dodaj_szkolenie')
    else:
        form = SelectUczenForm(user=request.user)

    return render(request, 'wybierz_ucznia.html', {'form': form})


@login_required
def dodaj_ucznia(request):
    form = LastActiveForm(request.POST or None)

    if request.method == 'POST':
        if 'delete_uczen' in request.POST:
            uczen_id = request.POST.get('uczen_id')
            if uczen_id:
                uczen = Uczen.objects.get(id=uczen_id)
                uczen.delete()
                # Logika usuwania ucznia i powiązanych danych...
                return redirect('dodaj_ucznia')
        elif form.is_valid():
            uczen = form.save(commit=False)
            uczen.user = request.user
            uczen.save()
            return redirect('dodaj_ucznia')

    uczniowie = Uczen.objects.filter(user=request.user).select_related('category')
    for uczen in uczniowie:
        uczen.planned_start = uczen.planned_start.strftime('%d-%m-%Y')
        uczen.planned_end = uczen.planned_end.strftime('%d-%m-%Y')

    context = {
        'form': form,
        'uczniowie': uczniowie
    }

    return render(request, 'dodaj_ucznia.html', context)

@require_http_methods(["GET"])
def raport_ogolny(request):
    tekst = Tekst.objects.all()
    if not (request.user.is_authenticated and request.user.is_superuser):
        return HttpResponse(f'Tylko administrator ma dostęp do tej strony.\n'
                            f'<a href="http://127.0.0.1:8000/">wróć</a>', status=403)
    data_dict = defaultdict(lambda: {'szkolenia': 0, 'braki_szkolenia': 0, 'nieobecnosci': 0})
    planowane_szkolenia_na_tydzien = defaultdict(int)
    przesuniete_dni = []
    # Przetwarzanie każdego ucznia
    for uczen in Uczen.objects.all():
        start_date = uczen.planned_start
        end_date = uczen.planned_end
        dni_wolne_ucznia = [d.data for d in uczen.dzien_wolny.all()]
        braki_szkolenia_ucznia = [b.data for b in uczen.brak_szkolenia.all()]
        nieobecnosci_ucznia = [n.data for n in uczen.nieobecnosc.all()]

        dni_szkolenia_do_zrealizowania = uczen.ilosc_szkolen.dni


        while dni_szkolenia_do_zrealizowania > 0:
            # Sprawdzenie, czy dzień jest dniem wolnym, brakiem szkolenia lub nieobecnością
            if start_date in dni_wolne_ucznia or start_date in braki_szkolenia_ucznia or start_date in nieobecnosci_ucznia:
                przesuniete_dni.append(start_date)
                # Przesunięcie planowanego końca, jeśli jest to dzień wolny
                if start_date in dni_wolne_ucznia:
                    end_date += timedelta(days=1)
            else:
                # Dodanie dnia szkoleniowego
                current_week = start_date.isocalendar()[1]
                planowane_szkolenia_na_tydzien[current_week] += 1
                dni_szkolenia_do_zrealizowania -= 1

            start_date += timedelta(days=1)

            if start_date > end_date and dni_szkolenia_do_zrealizowania > 0:
                end_date += timedelta(days=1)

        #
        for dzien_wolny in dni_wolne_ucznia:
            holiday_week = dzien_wolny.isocalendar()[1]
            if planowane_szkolenia_na_tydzien[holiday_week] >= 0:
                planowane_szkolenia_na_tydzien[holiday_week] -= 1

    # Zliczanie rekordów i przypisywanie ich do numeru tygodnia
    szkolenia_counts = Szkolenie.objects.annotate(week=ExtractWeek('data')).values('week').annotate(total=Count('id'))
    braki_szkolenia_counts = BrakSzkolenia.objects.annotate(week=ExtractWeek('data')).values('week').annotate(
        total=Count('id'))
    nieobecnosci_counts = Nieobecnosc.objects.annotate(week=ExtractWeek('data')).values('week').annotate(
        total=Count('id'))

    for entry in szkolenia_counts:
        data_dict[entry['week']]['szkolenia'] = entry['total']
    for entry in braki_szkolenia_counts:
        data_dict[entry['week']]['braki_szkolenia'] = entry['total']
    for entry in nieobecnosci_counts:
        data_dict[entry['week']]['nieobecnosci'] = entry['total']

    # Tworzenie wykresu
    fig, ax = plt.subplots()

    weeks = sorted(list(data_dict.keys()))
    szkolenia_values = [data_dict[week]['szkolenia'] for week in weeks]
    braki_szkolenia_values = [data_dict[week]['braki_szkolenia'] for week in weeks]
    nieobecnosci_values = [data_dict[week]['nieobecnosci'] for week in weeks]

    # Stosowanie słupków na wykresie
    ax.bar(weeks, szkolenia_values, color='green', label='Szkolenie')
    ax.bar(weeks, braki_szkolenia_values, color='red', bottom=szkolenia_values, label='Brak szkolenia')
    ax.bar(weeks, nieobecnosci_values, color='blue',
           bottom=[i + j for i, j in zip(szkolenia_values, braki_szkolenia_values)], label='Nieobecność')

    # Etykiety do słupków
    for i in ax.containers:
        ax.bar_label(i, label_type='center')

    # Dodanie linii dla planowanych szkoleń
    planowane_szkolenia_values = [
        planowane_szkolenia_na_tydzien[week] + len([d for d in przesuniete_dni if d.isocalendar()[1] == week]) for week
        in weeks]
    ax.plot(weeks, planowane_szkolenia_values, color='orange', marker='o', linestyle='-',
            label='Planowane szkolenia')


    # Dodanie etykiet i legendy
    ax.set_xlabel('Numer tygodnia')
    ax.set_ylabel('Dni robocze')
    ax.yaxis.set_major_locator(ticker.MaxNLocator(integer=True))
    ax.set_xticks(weeks)
    ax.set_xticklabels([f'{week}' for week in weeks])
    ax.legend()

    # Zapisanie wykresu do pliku w pamięci
    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    plt.close(fig)

    buffer.seek(0)
    chart_data = base64.b64encode(buffer.read()).decode('utf-8')

    form = LastActiveForm(request.POST or None)
    uczniowie = Uczen.objects.select_related('category').prefetch_related('audyt')
    audyty = Audyt.objects.all()
    for uczen in uczniowie:
        uczen.planned_start = uczen.planned_start.strftime('%d-%m-%Y')
        uczen.planned_end = uczen.planned_end.strftime('%d-%m-%Y')
        liczba_szkolen = uczen.szkolenie.count()  # liczy dni szkoleniowe
        calkowita_ilosc_szkolen = uczen.ilosc_szkolen.dni  # całkowita ilość szkoleń
        uczen.procent_wykonania = round(
            ((liczba_szkolen / calkowita_ilosc_szkolen * 100) if calkowita_ilosc_szkolen > 0 else 0), 2)
        uczen.ilosc_nieobecnosci = uczen.nieobecnosc.count()
        uczen.ilosc_braku_szkolen = uczen.brak_szkolenia.count()

    context = {
        'chart_data': chart_data,
        'tekst': tekst,
        'audyty': audyty,
        'uczniowie': uczniowie,
        'form': form,
    }

    # Przekazanie wygenerowanego wykresu do szablonu
    return render(request, 'raport_ogolny.html',context)