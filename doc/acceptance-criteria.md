# Kryteria akceptacji

1. Użytkownik importuje pliki przez drag-and-drop.
2. Aplikacja przyjmuje od 1 do 3 plików CSV i pokazuje tyle wykresów, ile plików załadowano.
3. Wykresy pokazują luki (`null`) jako przerwy linii.
4. Każdy wykres używa własnej osi czasu od startu danej serii i wypełnia całą szerokość panelu.
5. Eksport XLSX tworzy arkusze `Chart_01..N` (N zgodne z liczbą załadowanych plików).
6. Tabela podglądu na dole pokazuje 10 rekordów na stronę i umożliwia przewijanie.
7. Aplikacja działa jako backend + GUI NiceGUI uruchamiany z `python src/app.py`.
