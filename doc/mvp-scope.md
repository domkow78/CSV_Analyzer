# MVP Scope

## Cel
Analizator CSV dla danych pomiarowych oparty o Python + NiceGUI.

## Zakres MVP
- Import od 1 do 3 plików CSV przez drag-and-drop (jedyny tryb).
- Wybór wspólnej kolumny metryki.
- 1-3 wykresy na jednym ekranie (w zależności od liczby plików).
- Niezależna oś czasu dla każdego wykresu (czas od startu danej serii) oraz przerwy dla braków danych (`connectgaps=False`).
- Eksport XLSX do arkuszy `Chart_01..N` (N = liczba załadowanych plików).
- Tabela podglądu z paginacją 10 rekordów i przewijaniem.

## Poza zakresem
- Baza danych.
- Zaawansowana obróbka statystyczna.
- Interpolacja braków danych.
