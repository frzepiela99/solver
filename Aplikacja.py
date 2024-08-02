#!/usr/bin/env python
# coding: utf-8

# In[12]:


import sympy as sp
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkinter import filedialog
from pulp import LpVariable, LpProblem, lpSum, LpMinimize, LpMaximize
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.backends.backend_pdf import PdfPages
import numpy as np
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.lines import Line2D
import matplotlib.colors as mcolors
from matplotlib.patches import Polygon


root = tk.Tk()
root.title("Uniwersalne narzędzie do programowania liniowego")
root.geometry("800x600")

zmienne = {}
ograniczenia = []
problem = None
kierunek_celu = tk.StringVar(value="Minimize")

# Zakładki
zeszyt = ttk.Notebook(root)
zeszyt.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

zakladka_zmienne = tk.Frame(zeszyt)
zakladka_ograniczenia = tk.Frame(zeszyt)
zakladka_funkcja_celu = tk.Frame(zeszyt)

zeszyt.add(zakladka_zmienne, text="Zmienne")
zeszyt.add(zakladka_ograniczenia, text="Ograniczenia")
zeszyt.add(zakladka_funkcja_celu, text="Funkcja Celu")

# Inicjalizacja problemu
def inicjalizuj_problem():
    global problem
    kierunek = LpMinimize if kierunek_celu.get() == "Minimize" else LpMaximize
    problem = LpProblem("Problem Optymalizacyjny", kierunek)

# Inicjalizacja zakładek
def inicjalizuj_zakladki():
    inicjalizuj_zakladke_zmienne()
    inicjalizuj_zakladke_ograniczenia()
    inicjalizuj_zakladke_funkcja_celu()

# Inicjalizacja zakładki zmiennych
def inicjalizuj_zakladke_zmienne():
    wyczysc_ramke(zakladka_zmienne)
    tk.Label(zakladka_zmienne, text="Ilość zmiennych:").pack(side=tk.TOP, fill=tk.X)
    global liczba_zmiennych_entry
    liczba_zmiennych_entry = tk.Entry(zakladka_zmienne)
    liczba_zmiennych_entry.pack(side=tk.TOP, fill=tk.X)
    tk.Button(zakladka_zmienne, text="Generuj pola", command=utworz_pola_zmiennych).pack(side=tk.TOP)

# Inicjalizacja zakładki ograniczeń
def inicjalizuj_zakladke_ograniczenia():
    wyczysc_ramke(zakladka_ograniczenia)
    tk.Label(zakladka_ograniczenia, text="Ilość ograniczeń:").pack(side=tk.TOP, fill=tk.X)
    global liczba_ograniczen_entry
    liczba_ograniczen_entry = tk.Entry(zakladka_ograniczenia)
    liczba_ograniczen_entry.pack(side=tk.TOP, fill=tk.X)
    tk.Button(zakladka_ograniczenia, text="Generuj pola", command=utworz_pola_ograniczen).pack(side=tk.TOP)

# Inicjalizacja zakładki funkcji celu
def inicjalizuj_zakladke_funkcja_celu():
    wyczysc_ramke(zakladka_funkcja_celu)
    tk.Label(zakladka_funkcja_celu, text="Wyrażenie funkcji celu:").pack(side=tk.TOP, fill=tk.X)
    global pole_funkcji_celu
    pole_funkcji_celu = tk.Entry(zakladka_funkcja_celu)
    pole_funkcji_celu.pack(side=tk.TOP, fill=tk.X)
    global kierunek_celu
    kierunek_celu = ttk.Combobox(zakladka_funkcja_celu, values=["Minimize", "Maximize"], state="readonly")
    kierunek_celu.set("Minimize")
    kierunek_celu.pack(side=tk.TOP, fill=tk.X)
    tk.Button(zakladka_funkcja_celu, text="Ustaw funkcję celu i kierunek", command=ustaw_funkcje_celu).pack(side=tk.TOP)

# Utworzenie pól zmiennych
def utworz_pola_zmiennych():
    try:
        liczba_zmiennych = int(liczba_zmiennych_entry.get())
    except ValueError:
        messagebox.showerror("Błąd", "Wprowadź poprawną liczbę zmiennych.")
        return
    
    wyczysc_ramke(zakladka_zmienne)
    inicjalizuj_zakladke_zmienne()
    for i in range(liczba_zmiennych):
        utworz_pole_zmiennej(zakladka_zmienne, i)

# Utworzenie pojedynczego pola zmiennej
def utworz_pole_zmiennej(rodzic, indeks):
    ramka_zmiennej = tk.Frame(rodzic)
    ramka_zmiennej.pack(fill=tk.X, padx=5, pady=5)
    tk.Label(ramka_zmiennej, text=f"Zmienna {indeks+1}:").pack(side=tk.LEFT)
    
    nazwa_entry = tk.Entry(ramka_zmiennej, width=5)
    nazwa_entry.pack(side=tk.LEFT, padx=2)
    
    dolna_skala = tk.Scale(ramka_zmiennej, from_=0, to=999999, orient=tk.HORIZONTAL)
    dolna_skala.pack(side=tk.LEFT, padx=2)
    
    gorna_skala = tk.Scale(ramka_zmiennej, from_=0, to=999999, orient=tk.HORIZONTAL)
    gorna_skala.pack(side=tk.LEFT, padx=2)
    
    combo_kategoria = ttk.Combobox(ramka_zmiennej, values=["Continuous", "Integer"], state="readonly")
    combo_kategoria.set("Continuous")
    combo_kategoria.pack(side=tk.LEFT, padx=2)
    
    przycisk_zapisz = tk.Button(ramka_zmiennej, text="Zapisz", command=lambda ne=nazwa_entry, le=dolna_skala, ue=gorna_skala, cc=combo_kategoria: zapisz_zmienna(ne, le, ue, cc))
    przycisk_zapisz.pack(side=tk.LEFT, padx=2)

def aktualizuj_informacje_o_stanie(wiadomosc):
    info_stanu.config(state='normal')
    info_stanu.insert(tk.END, wiadomosc + "\n")
    info_stanu.config(state='disabled')
    
# Zapisanie zmiennej
def zapisz_zmienna(nazwa_entry, dolna_skala, gorna_skala, combo_kategoria):
    nazwa = nazwa_entry.get()
    dolna = dolna_skala.get()
    gorna = gorna_skala.get()
    kategoria = combo_kategoria.get()
    
    if nazwa == "":
        messagebox.showerror("Błąd", "Nazwa zmiennej nie może być pusta.")
        return
    if nazwa in zmienne:
        messagebox.showerror("Błąd", f"Zmienna '{nazwa}' już istnieje.")
        return
    
    zmienna = LpVariable(nazwa, lowBound=dolna, upBound=gorna, cat=kategoria)
    zmienne[nazwa] = zmienna
    aktualizuj_informacje_o_stanie(f"Zmienna dodana: {nazwa} [{dolna}, {gorna}] {kategoria}")

# Utworzenie pól ograniczeń
def utworz_pola_ograniczen():
    try:
        liczba_ograniczen = int(liczba_ograniczen_entry.get())
    except ValueError:
        messagebox.showerror("Błąd", "Wprowadź poprawną liczbę ograniczeń.")
        return

    wyczysc_ramke(zakladka_ograniczenia)
    inicjalizuj_zakladke_ograniczenia()
    for i in range(liczba_ograniczen):
        utworz_pole_ograniczenia(zakladka_ograniczenia, i)

# Utworzenie pojedynczego pola ograniczenia
def utworz_pole_ograniczenia(rodzic, indeks):
    ramka_ograniczenia = tk.Frame(rodzic)
    ramka_ograniczenia.pack(fill=tk.X, padx=5, pady=2)

    etykieta_ograniczenia = tk.Label(ramka_ograniczenia, text=f"Ograniczenie {indeks+1}:")
    etykieta_ograniczenia.pack(side=tk.LEFT)

    pole_ograniczenia = tk.Entry(ramka_ograniczenia)
    pole_ograniczenia.pack(side=tk.LEFT, fill=tk.X, expand=True)

    przycisk_zapisz = tk.Button(ramka_ograniczenia, text="Zapisz", command=lambda ce=pole_ograniczenia: zapisz_ograniczenie(ce))
    przycisk_zapisz.pack(side=tk.LEFT, padx=5)

# Zapisanie ograniczenia
def zapisz_ograniczenie(pole_ograniczenia):
    ograniczenie = pole_ograniczenia.get()
    if ograniczenie:
        ograniczenia.append(ograniczenie)
        aktualizuj_informacje_o_stanie(f"Ograniczenie dodane: {ograniczenie}")

# Ustawienie funkcji celu z odpowiednim odniesieniem do zmiennych
def ustaw_funkcje_celu():
    global problem  # Deklaracja problemu jako globalnego
    try:
        # Wyciągnięcie wyrażenia z pola funkcji celu
        wyrazenie = pole_funkcji_celu.get()
        if not wyrazenie:
            raise ValueError("Funkcja celu nie może być pusta.")

        # Zamiana nazw zmiennych w wyrażeniu na odniesienia słownikowe
        for nazwa_zmiennej in zmienne.keys():
            wyrazenie = wyrazenie.replace(nazwa_zmiennej, f'zmienne["{nazwa_zmiennej}"]')

        inicjalizuj_problem()  # Ponowna inicjalizacja problemu z odpowiednim kierunkiem

        # Bezpieczna ocena zmodyfikowanego wyrażenia i ustawienie go jako funkcji celu
        problem += eval(wyrazenie), "Funkcja Celu"

        aktualizuj_informacje_o_stanie(f"Funkcja celu ustawiona: {pole_funkcji_celu.get()} [{kierunek_celu.get()}]")
    except Exception as e:
        messagebox.showerror("Błąd", f"Niepoprawne wyrażenie funkcji celu: {e}")

# Rozwiązanie problemu z odpowiednim odniesieniem do zmiennych
def rozwiaz_problem():
    try:
        global problem, ograniczenia, zmienne  # Zapewnienie użycia globalnych zmiennych
        inicjalizuj_problem()  # Ponowna inicjalizacja problemu w celu usunięcia poprzedniej funkcji celu/ograniczeń
        
        # Ponowne ustawienie funkcji celu, ponieważ ponownie inicjalizujemy problem
        wyrazenie = pole_funkcji_celu.get()
        for nazwa_zmiennej in zmienne.keys():
            wyrazenie = wyrazenie.replace(nazwa_zmiennej, f'zmienne["{nazwa_zmiennej}"]')
        problem += eval(wyrazenie), "Funkcja Celu"

        # Aktualizacja ograniczeń z odpowiednim odniesieniem do zmiennych przed dodaniem do problemu
        for ograniczenie_str in ograniczenia:
            wyrazenie_ograniczenia = ograniczenie_str
            for nazwa_zmiennej in zmienne.keys():
                wyrazenie_ograniczenia = wyrazenie_ograniczenia.replace(nazwa_zmiennej, f'zmienne["{nazwa_zmiennej}"]')
            problem += eval(wyrazenie_ograniczenia), ""

        problem.solve()
        wynik = f"Status: {problem.status}, Wartość: {problem.objective.value()}\n"
        for v in zmienne.values():
            wynik += f"{v.name}: {v.varValue}\n"
        aktualizuj_informacje_o_stanie(wynik)
    except Exception as e:
        messagebox.showerror("Błąd", f"Problem z rozwiązaniem: {e}")

# Dodajemy funkcje generujące wykresy
def generuj_wykres_kolowy():
    etykiety = [v.name for v in zmienne.values()]
    wielkosci = [v.varValue for v in zmienne.values()]
    if wielkosci:
        fig, ax = plt.subplots()
        ax.pie(wielkosci, labels=etykiety, autopct='%1.1f%%', startangle=140)
        ax.axis('equal')
        pokaz_wykres(fig)
    else:
        messagebox.showinfo("Informacja", "Brak danych do wykresu kołowego.")

def generuj_wykres_liniowy():
    etykiety = [v.name for v in zmienne.values()]
    wartosci = [v.varValue for v in zmienne.values()]
    if wartosci:
        fig, ax = plt.subplots()
        ax.plot(etykiety, wartosci, marker='o')
        ax.set_xlabel('Zmienne')
        ax.set_ylabel('Wartości')
        ax.set_title('Wykres wartości zmiennych')
        pokaz_wykres(fig)
    else:
        messagebox.showinfo("Informacja", "Brak danych do wykresu liniowego.")
        
def generuj_wykres_slupkowy(zapisz_pdf=None):
    etykiety = [v.name for v in zmienne.values()]
    wartosci = [v.varValue for v in zmienne.values()]
    if wartosci:
        fig, ax = plt.subplots()
        ax.bar(etykiety, wartosci, color='blue')
        ax.set_xlabel('Zmienne')
        ax.set_ylabel('Wartości')
        ax.set_title('Wykres słupkowy wartości zmiennych')
        if zapisz_pdf:
            zapisz_pdf.savefig(fig)
            plt.close(fig)
        else:
            pokaz_wykres(fig)
    else:
        messagebox.showinfo("Informacja", "Brak danych do wykresu słupkowego.")


def pokaz_wykres(fig):
    okno_wykresu = tk.Toplevel(root)
    okno_wykresu.title("Wykres")
    plotno = FigureCanvasTkAgg(fig, master=okno_wykresu)
    plotno.draw()
    plotno.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

# Dodajemy przyciski do generowania wykresów w głównym oknie
def dodaj_przyciski_wykresow():
    ramka_przyciskow = tk.Frame(root)
    ramka_przyciskow.pack(side=tk.BOTTOM, fill=tk.X, pady=15)

    przycisk_rozwiaz = tk.Button(ramka_przyciskow, text="Rozwiąż problem", command=rozwiaz_problem)
    przycisk_rozwiaz.pack(side=tk.LEFT, padx=15)

    przycisk_wykres_nierownosci = tk.Button(ramka_przyciskow, text="Wykres nierówności", command=lambda: generuj_wykres_nierownosci(ograniczenia))
    przycisk_wykres_nierownosci.pack(side=tk.LEFT, padx=15)

    przycisk_wykres_kolowy = tk.Button(ramka_przyciskow, text="Wykres kołowy", command=generuj_wykres_kolowy)
    przycisk_wykres_kolowy.pack(side=tk.LEFT, padx=15)

    przycisk_wykres_liniowy = tk.Button(ramka_przyciskow, text="Wykres liniowy", command=generuj_wykres_liniowy)
    przycisk_wykres_liniowy.pack(side=tk.LEFT, padx=15)
    
    przycisk_wykres_slupkowy = tk.Button(ramka_przyciskow, text="Wykres słupkowy", command=generuj_wykres_slupkowy)
    przycisk_wykres_slupkowy.pack(side=tk.LEFT, padx=15)

    przycisk_zapisz_pdf = tk.Button(ramka_przyciskow, text="Zapisz do PDF", command=zapisz_do_pdf)
    przycisk_zapisz_pdf.pack(side=tk.LEFT, padx=15)

# Funkcja do zapisywania danych i wykresów do PDF
def zapisz_do_pdf():
    nazwa_pliku_pdf = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("Pliki PDF", "*.pdf")])
    if nazwa_pliku_pdf:
        with PdfPages(nazwa_pliku_pdf) as pdf:
            # Zapisz wykres kołowy
            if any(v.varValue for v in zmienne.values()):
                generuj_wykres_kolowy(zapisz_pdf=pdf)
            # Zapisz wykres liniowy
            if any(v.varValue for v in zmienne.values()):
                generuj_wykres_liniowy(zapisz_pdf=pdf)
            # Zapisz wykres słupkowy
            if any(v.varValue for v in zmienne.values()):
                generuj_wykres_slupkowy(zapisz_pdf=pdf)  # Dostosowane do zapisu wykresu słupkowego do PDF
            # Zapisz wykres nierówności
            if ograniczenia:
                generuj_wykres_nierownosci(ograniczenia, pokaz_okno=False, zapisz_pdf=pdf)
            # Zapisz tekst z dolnej części okna
            tekst_info_stanu = info_stanu.get("1.0", tk.END)
            fig = plt.figure(figsize=(8, 0.5))
            plt.text(0, 0, tekst_info_stanu, fontsize=10, wrap=True)
            plt.axis('off')
            pdf.savefig(fig, bbox_inches='tight')
            plt.close()

            messagebox.showinfo("Sukces", "Dane i wykresy zostały zapisane do PDF.")

# Modyfikacja funkcji generujących wykresy, aby mogły zapisywać do PDF
def generuj_wykres_kolowy(zapisz_pdf=None):
    etykiety = [v.name for v in zmienne.values()]
    wielkosci = [v.varValue for v in zmienne.values()]
    fig, ax = plt.subplots()
    ax.pie(wielkosci, labels=etykiety, autopct='%1.1f%%')
    ax.axis('equal')
    if zapisz_pdf:
        zapisz_pdf.savefig(fig)
    else:
        pokaz_wykres(fig)

def generuj_wykres_liniowy(zapisz_pdf=None):
    etykiety = [v.name for v in zmienne.values()]
    wartosci = [v.varValue for v in zmienne.values()]
    fig, ax = plt.subplots()
    ax.plot(etykiety, wartosci, marker='o')
    ax.set_xlabel('Zmienne')
    ax.set_ylabel('Wartości')
    ax.set_title('Wykres wartości zmiennych')
    if zapisz_pdf:
        zapisz_pdf.savefig(fig)
    else:
        pokaz_wykres(fig)

def parse_constraint(constraint_str):
    if '<=' in constraint_str:
        lhs, rhs = constraint_str.split('<=')
        nierownosc = '<='
    elif '>=' in constraint_str:
        lhs, rhs = constraint_str.split('>=')
        nierownosc = '>='
    else:
        raise ValueError("Nieprawidłowy format ograniczenia. Musi zawierać '<=' lub '>='.")
    
    warunki_lhs = lhs.strip().replace(' ', '').split('+')
    wartosc_rhs = float(rhs.strip())
    return warunki_lhs, wartosc_rhs, nierownosc

def stworz_funkcje_ograniczenia(warunki_lhs, wartosc_rhs):
    wspolczynniki = {'P1': 0, 'P2': 0}
    for warunek in warunki_lhs:
        if 'P1' in warunek:
            wsp = warunek.split('*P1')[0]
            wspolczynniki['P1'] = float(wsp) if wsp else 1.0
        elif 'P2' in warunek:
            wsp = warunek.split('*P2')[0]
            wspolczynniki['P2'] = float(wsp) if wsp else 1.0
    return lambda p1, p2: wspolczynniki['P1'] * p1 + wspolczynniki['P2'] * p2 - wartosc_rhs

def znajdz_punkt_przeciecia(funkcje, lista_ograniczen):
    for i in range(len(funkcje)):
        for j in range(i + 1, len(funkcje)):
            p1, p2 = sp.symbols('P1 P2')
            eq1 = sp.Eq(funkcje[i](p1, p2), 0)
            eq2 = sp.Eq(funkcje[j](p1, p2), 0)
            solution = sp.solve((eq1, eq2), (p1, p2))
            if solution:
                if all([funkcje[k](solution[p1], solution[p2]) <= 0 if '<=' in lista_ograniczen[k] else funkcje[k](solution[p1], solution[p2]) >= 0 for k in range(len(funkcje)) if k != i and k != j]):
                    return solution[p1], solution[p2]
    return None, None

def generuj_wykres_nierownosci(lista_ograniczen, pokaz_okno=True, zapisz_pdf=None):
    zakres_p1 = np.linspace(0, 300, 400)
    zakres_p2 = np.linspace(0, 300, 400)
    P1, P2 = np.meshgrid(zakres_p1, zakres_p2)

    fig, ax = plt.subplots(figsize=(10, 8))
    legendy = []

    kolory_linii = ['b', 'g', 'r', 'c', 'm', 'y', 'k', 'w', 'tab:blue', 'tab:orange', 'tab:green', 'tab:red', 'tab:purple', 'tab:brown', 'tab:pink', 'tab:gray', 'tab:olive', 'tab:cyan', 'lime', 'teal']
    kolory_wypelnienia = ['salmon', 'lightgreen', 'lightblue', 'lavender', 'beige', 'wheat', 'tan', 'orchid', 'lightcoral', 'palegreen', 'paleturquoise', 'lightsteelblue', 'powderblue', 'thistle', 'lightgrey', 'rosybrown', 'mediumaquamarine', 'peachpuff', 'khaki', 'bisque']

    funkcje_ograniczen = []
    for i, c in enumerate(lista_ograniczen):
        warunki_lhs, wartosc_rhs, nierownosc = parse_constraint(c)
        funkcja = stworz_funkcje_ograniczenia(warunki_lhs, wartosc_rhs)
        funkcje_ograniczen.append(funkcja)

        ograniczenie = funkcja(P1, P2)
        if nierownosc == '<=':
            ax.contour(P1, P2, ograniczenie, levels=[0], colors=kolory_linii[i], linestyles='-')
            ax.contourf(P1, P2, ograniczenie, levels=[ograniczenie.min(), 0], colors=[kolory_wypelnienia[i]], alpha=0.3)
        elif nierownosc == '>=':
            ax.contour(P1, P2, ograniczenie, levels=[0], colors=kolory_linii[i], linestyles='-')
            ax.contourf(P1, P2, ograniczenie, levels=[0, ograniczenie.max()], colors=[kolory_wypelnienia[i]], alpha=0.3)

        legendy.append(Line2D([0], [0], color=kolory_linii[i], lw=2, label=f"Ograniczenie {i+1}: {c}"))

    # Znajdź punkt przecięcia ograniczeń
    p1_przeciecie, p2_przeciecie = znajdz_punkt_przeciecia(funkcje_ograniczen, lista_ograniczen)
    if p1_przeciecie is not None and p2_przeciecie is not None:
        ax.plot(p1_przeciecie, p2_przeciecie, 'yo', markersize=10)  # Rysuj żółtą kropkę
        # Dodanie informacji o punkcie przecięcia do legendy
        legendy.append(Line2D([0], [0], marker='o', color='yellow', label=f'Punkt przecięcia: ({p1_przeciecie:.2f}, {p2_przeciecie:.2f})', markersize=10))

    ax.legend(handles=legendy, loc='upper right')
    ax.set_xlim((0, 20))
    ax.set_ylim((0, 20))
    ax.set_xlabel('P1')
    ax.set_ylabel('P2')
    ax.set_title('Diagram nierówności')

    if zapisz_pdf:
        zapisz_pdf.savefig(fig)
    if pokaz_okno:
        pokaz_wykres(fig)
    plt.close(fig)

    

def pokaz_wykres(fig):
    okno_wykresu = tk.Toplevel(root)
    okno_wykresu.title("Wykres")
    plotno = FigureCanvasTkAgg(fig, master=okno_wykresu)
    plotno.draw()
    plotno.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

# Funkcja czyszczenia ramki
def wyczysc_ramke(ramka):
    for widget in ramka.winfo_children():
        widget.destroy()
        
# Funkcja czyszczenia wszystkich danych
def wyczysc_wszystko():
    global zmienne, ograniczenia, problem
    zmienne.clear()
    ograniczenia.clear()
    problem = None
    wyczysc_ramke(zakladka_zmienne)
    wyczysc_ramke(zakladka_ograniczenia)
    inicjalizuj_zakladke_zmienne()
    inicjalizuj_zakladke_ograniczenia()
    pole_funkcji_celu.delete(0, tk.END)
    info_stanu.config(state='normal')
    info_stanu.delete('1.0', tk.END)
    info_stanu.config(state='disabled')
    messagebox.showinfo("Informacja", "Dane zostały wyczyszczone.")
    
# Dodanie przycisku czyszczenia do głównego okna
def dodaj_przycisk_czyszczenia():
    przycisk_czyszczenia = tk.Button(root, text="Wyczyść wszystko", command=wyczysc_wszystko)
    przycisk_czyszczenia.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=5)

# Wywołanie funkcji dodającej przycisk
dodaj_przycisk_czyszczenia()

# Inicjalizacja na starcie
inicjalizuj_problem()
inicjalizuj_zakladki()
dodaj_przyciski_wykresow()  # Dodaj przyciski kontrolne na dole

# Pole tekstowe z informacjami o stanie
info_stanu = tk.Text(root, height=10, state='disabled')
info_stanu.pack(fill=tk.BOTH, expand=True)

root.mainloop()


# In[ ]:




