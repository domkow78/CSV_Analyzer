# Deployment / Uruchomienie aplikacji

Poniżej pełna instrukcja uruchomienia aplikacji `CSV Analyzer` (Python + NiceGUI) lokalnie.

## 1) Wymagania wstępne

- Python 3.11 lub nowszy
- `pip` (standardowo z Pythonem)
- Dostęp do terminala w katalogu projektu

Zalecenie: Python 3.11 lub 3.12 (najbardziej przewidywalny dla pakietów data-science).

## 2) Przejście do katalogu projektu

Uruchom terminal i przejdź do folderu projektu:

```powershell
cd "c:\Programs\WorkDirDev\## Git Hub\CSV_Analyzer"
```

## 3) Utworzenie środowiska wirtualnego (venv)

```powershell
python -m venv .venv
```

Po tej operacji powstanie katalog `.venv` z izolowanym środowiskiem Pythona.

## 4) Aktywacja venv

### Windows PowerShell

```powershell
.\.venv\Scripts\Activate.ps1
```

Uwaga: w PowerShell musi być prefiks `./` lub `.\`.
Bez tego PowerShell może próbować potraktować `.venv` jak moduł i zwrócić błąd `CouldNotAutoLoadModule`.

Jeśli pojawi się błąd polityki wykonywania skryptów, uruchom jednorazowo:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

i ponownie aktywuj:

```powershell
.\.venv\Scripts\Activate.ps1
```

### Windows CMD

```cmd
.venv\Scripts\activate.bat
```

### Linux / macOS (bash/zsh)

```bash
source .venv/bin/activate
```

Po aktywacji zwykle zobaczysz prefiks `(.venv)` w terminalu.

## 5) Instalacja zależności z requirements.txt

Najpierw zaktualizuj `pip`, potem zainstaluj pakiety:

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## 6) Uruchomienie aplikacji

```powershell
python src/app.py
```

Po uruchomieniu otwórz w przeglądarce adres pokazany w terminalu (domyślnie):

- http://localhost:8080

## 7) Szybki test działania

1. Wgraj od 1 do 3 plików CSV metodą drag-and-drop.
2. Wybierz wspólną metrykę.
3. Sprawdź, że liczba wykresów odpowiada liczbie plików (1-3), a wykresy wypełniają szerokość panelu.
4. Sprawdź tabelę podglądu na dole (10 rekordów na stronę, przewijanie).
5. Użyj eksportu XLSX (`Chart_01..N`).

## 8) Dezaktywacja środowiska

Po zakończeniu pracy:

```powershell
deactivate
```

## 9) Najczęstsze problemy

### `python` nie jest rozpoznawany
- Sprawdź instalację Pythona.
- W Windows doinstaluj Python z opcją dodania do `PATH`.

### Brak modułów (`ModuleNotFoundError`)
- Upewnij się, że venv jest aktywny.
- Wykonaj ponownie `pip install -r requirements.txt`.

### Błąd instalacji `pandas` (Meson / `vswhere.exe`)
- Najczęściej oznacza próbę kompilacji ze źródeł zamiast instalacji gotowego wheel.
- Upewnij się, że używasz aktualnego `requirements.txt` (z `pandas==2.2.3`).
- Spróbuj wymusić instalację binarną:

```powershell
pip install --only-binary=:all: pandas==2.2.3
pip install -r requirements.txt
```

- Jeśli problem nadal występuje, użyj Pythona 3.12 i odtwórz venv:

```powershell
deactivate
Remove-Item -Recurse -Force .venv
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### Port 8080 zajęty
- Zamknij proces, który używa portu, albo uruchom aplikację na innym porcie (konfiguracja w `ui.run(...)` w [src/app.py](src/app.py)).

### `CancelledError` / `KeyboardInterrupt` po uruchomieniu
- Jeśli wcześniej pojawił się komunikat `NiceGUI ready to go on http://localhost:8080`, to aplikacja wystartowała poprawnie.
- Taki traceback zwykle oznacza ręczne zatrzymanie procesu (`Ctrl+C`) i nie jest błędem logiki aplikacji.

