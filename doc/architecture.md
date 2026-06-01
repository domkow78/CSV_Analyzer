# Architektura startowa

- `src/app.py` – backend + GUI (NiceGUI), parsowanie CSV, przygotowanie danych wykresów, wykresy Plotly i eksport XLSX.
- `data/` – przykładowe dane CSV do testów ręcznych.
- `requirements.txt` – zależności Pythona.

## Przepływ danych
1. Import: drag-and-drop (1-3 pliki CSV).
2. Parse CSV: autodetekcja separatora i kolumny czasu.
3. Transformacja: dla każdego pliku liczony jest `elapsed_s` od startu serii i wybrana wspólna metryka.
4. Wizualizacja: 1-3 wykresy Plotly (`w-full`, `autosize`, `responsive`) z `connectgaps=False`.
5. Podgląd tabelaryczny: dane `chart01..03` z paginacją 10 i przewijaniem.
6. Eksport: XLSX z arkuszami `Chart_01..N`.
