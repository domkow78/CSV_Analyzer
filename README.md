# CSV Analyzer (NiceGUI)

Aplikacja Python (backend + GUI) do analizy danych pomiarowych CSV.

## Zakres MVP
- import 1-3 plików CSV przez drag-and-drop (jedyny tryb),
- porównanie na 1-3 wykresach na jednym ekranie,
- niezależna oś czasu dla każdego wykresu (czas od startu danej serii),
- braki danych jako przerwy na wykresie,
- eksport XLSX do arkuszy `Chart_01..N` (zgodnie z liczbą załadowanych plików),
- tabela podglądu z 10 samplami na stronę i możliwością przewijania.

## Wymagania
- Python 3.11+ (zalecane 3.11 lub 3.12)
- pakiety z [requirements.txt](requirements.txt)

## Uruchomienie
1. `pip install -r requirements.txt`
2. `python src/app.py`
3. Otwórz adres z terminala (domyślnie `http://localhost:8080`).

## Użycie
1. Wgraj od 1 do 3 plików CSV przez DnD.
2. Wybierz wspólną metrykę.
3. Porównaj serie na 1-3 wykresach.
4. Eksportuj do XLSX.

## Dokumentacja
- zakres: [doc/mvp-scope.md](doc/mvp-scope.md)
- architektura: [doc/architecture.md](doc/architecture.md)
- kryteria akceptacji: [doc/acceptance-criteria.md](doc/acceptance-criteria.md)
