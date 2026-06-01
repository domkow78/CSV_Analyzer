from __future__ import annotations

import csv
import io
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Dict, List

import pandas as pd
import plotly.graph_objects as go
from nicegui import events, ui


@dataclass
class ParsedCsv:
    file_name: str
    time_column: str
    numeric_columns: List[str]
    frame: pd.DataFrame


class AnalyzerState:
    def __init__(self) -> None:
        self.uploaded: Dict[str, bytes] = {}
        self.selected_metric: str = ''
        self.parsed: List[ParsedCsv] = []
        self.chart_frames: List[pd.DataFrame] = []
        self.is_dark: bool = False


MAX_FILES = 3
COLORS = ['#2563eb', '#059669', '#dc2626']
state = AnalyzerState()
dark_mode = None




def detect_delimiter(sample: str) -> str:
    try:
        dialect = csv.Sniffer().sniff(sample, delimiters=',;\t|')
        return dialect.delimiter
    except csv.Error:
        return ','


def decode_bytes(content: bytes) -> str:
    for enc in ('utf-8-sig', 'utf-8', 'cp1250', 'latin-1'):
        try:
            return content.decode(enc)
        except UnicodeDecodeError:
            continue
    return content.decode('utf-8', errors='ignore')


def detect_time_column(columns: List[str]) -> str:
    lowered = [c.lower() for c in columns]
    for idx, col in enumerate(lowered):
        if 'ts_' in col or 'timestamp' in col or 'time' in col:
            return columns[idx]
    return columns[0]


def parse_uploaded_csv(file_name: str, content: bytes) -> ParsedCsv:
    text = decode_bytes(content)
    sample = '\n'.join(text.splitlines()[:10])
    delimiter = detect_delimiter(sample)

    df = pd.read_csv(io.StringIO(text), sep=delimiter, engine='python')
    if df.empty:
        raise ValueError(f'Plik {file_name} nie zawiera danych.')

    df.columns = [str(c).strip() for c in df.columns]
    time_column = detect_time_column(list(df.columns))

    parsed_time = pd.to_datetime(df[time_column], errors='coerce')
    if parsed_time.isna().all():
        numeric_time = pd.to_numeric(df[time_column], errors='coerce')
        if numeric_time.notna().any():
            median = numeric_time.dropna().median()
            unit = 'ms' if median > 1_000_000_000_000 else 's'
            parsed_time = pd.to_datetime(numeric_time, unit=unit, errors='coerce')

    numeric_columns: List[str] = []
    for col in df.columns:
        if col == time_column:
            continue
        numeric_series = pd.to_numeric(df[col], errors='coerce')
        if numeric_series.notna().any():
            df[col] = numeric_series
            numeric_columns.append(col)

    if not numeric_columns:
        raise ValueError(f'Plik {file_name} nie ma kolumn numerycznych.')

    work = pd.DataFrame({'timestamp': parsed_time})
    for col in numeric_columns:
        work[col] = df[col]

    work = work.dropna(subset=['timestamp']).sort_values('timestamp').reset_index(drop=True)
    if work.empty:
        raise ValueError(f'Plik {file_name} nie zawiera poprawnych znaczników czasu.')

    return ParsedCsv(
        file_name=file_name,
        time_column=time_column,
        numeric_columns=numeric_columns,
        frame=work,
    )


def get_common_metrics(files: List[ParsedCsv]) -> List[str]:
    if not files:
        return []
    common = set(files[0].numeric_columns)
    for f in files[1:]:
        common = common.intersection(f.numeric_columns)
    return sorted(common)


def build_chart_frames(files: List[ParsedCsv], metric: str) -> List[pd.DataFrame]:
    frames: List[pd.DataFrame] = []
    for f in files:
        frame = f.frame[['timestamp', metric]].copy().rename(columns={metric: 'value'})
        frame = frame.dropna(subset=['timestamp']).sort_values('timestamp').reset_index(drop=True)
        if frame.empty:
            frames.append(pd.DataFrame(columns=['timestamp', 'elapsed_s', 'value']))
            continue

        start_ts = frame.loc[0, 'timestamp']
        frame['elapsed_s'] = (frame['timestamp'] - start_ts).dt.total_seconds()
        frames.append(frame[['timestamp', 'elapsed_s', 'value']])

    return frames


def make_chart_figure(frame: pd.DataFrame, title: str, color: str, is_dark: bool = False) -> go.Figure:
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=frame['elapsed_s'],
            y=frame['value'],
            mode='lines',
            line={'color': color, 'width': 2},
            connectgaps=False,
            name=title,
        )
    )
    fig.update_layout(
        title=title,
        autosize=True,
        margin={'l': 20, 'r': 20, 't': 40, 'b': 20},
        height=500,
        template='plotly_dark' if is_dark else 'plotly_white',
        xaxis_title='Czas od startu [s]',
    )
    return fig


def export_xlsx() -> None:
    if not state.chart_frames or not state.selected_metric or len(state.parsed) < 1:
        ui.notify('Brak danych do eksportu.', color='negative')
        return

    with NamedTemporaryFile(delete=False, suffix='.xlsx') as tmp:
        tmp_path = Path(tmp.name)

    with pd.ExcelWriter(tmp_path, engine='openpyxl') as writer:
        for idx in range(1, len(state.parsed) + 1):
            source_name = state.parsed[idx - 1].file_name
            sheet_name = f'Chart_{idx:02d}'
            chart_frame = state.chart_frames[idx - 1]
            export_df = pd.DataFrame(
                {
                    'timestamp': chart_frame['timestamp'],
                    'elapsed_s': chart_frame['elapsed_s'],
                    'source_file': source_name,
                    'metric': state.selected_metric,
                    'value': chart_frame['value'],
                }
            )
            export_df.to_excel(writer, index=False, sheet_name=sheet_name)

    stamp = datetime.now().strftime('%Y%m%d-%H%M%S')
    ui.download(str(tmp_path), filename=f'comparison-{stamp}.xlsx')


def refresh_ui() -> None:
    files_label.text = f'Wgrane pliki CSV: {len(state.uploaded)} / {MAX_FILES}'

    if len(state.uploaded) < 1:
        status_label.text = 'Wgraj od 1 do 3 plików CSV.'
        metric_select.options = []
        metric_select.value = None
        state.chart_frames = []
        state.parsed = []
        for chart in charts:
            chart.set_visibility(False)
        preview_rows.rows = []
        export_button.disable()
        return

    try:
        selected = list(state.uploaded.items())[:MAX_FILES]
        state.parsed = [parse_uploaded_csv(name, data) for name, data in selected]
        common_metrics = get_common_metrics(state.parsed)

        if not common_metrics:
            raise ValueError('Brak wspólnej kolumny numerycznej w 3 plikach.')

        if state.selected_metric not in common_metrics:
            state.selected_metric = common_metrics[0]

        metric_select.options = common_metrics
        metric_select.value = state.selected_metric

        state.chart_frames = build_chart_frames(state.parsed, state.selected_metric)

        for idx, chart in enumerate(charts, start=1):
            if idx <= len(state.parsed):
                title = f'Chart_{idx:02d} - {state.parsed[idx - 1].file_name}'
                color = COLORS[idx - 1]
                fig = make_chart_figure(state.chart_frames[idx - 1], title, color, state.is_dark)
                chart.figure = fig
                chart.set_visibility(True)
                chart.update()
            else:
                chart.set_visibility(False)

        max_len = max((len(frame) for frame in state.chart_frames), default=0)
        preview = pd.DataFrame({'sample': list(range(max_len))})
        for idx, frame in enumerate(state.chart_frames, start=1):
            preview[f'chart{idx:02d}'] = frame['value'].reset_index(drop=True)
        preview_rows.rows = preview.to_dict(orient='records')

        status_label.text = f'Dane gotowe. Załadowano {len(state.parsed)} plik(i/ów).'
        export_button.enable()

    except Exception as ex:
        status_label.text = f'Błąd: {ex}'
        for chart in charts:
            chart.set_visibility(False)
        preview_rows.rows = []
        export_button.disable()


def on_upload(e: events.UploadEventArguments) -> None:
    if len(state.uploaded) >= MAX_FILES:
        ui.notify(f'Można wgrać maksymalnie {MAX_FILES} pliki. Użyj Wyczyść i wgraj ponownie.', color='warning')
        return

    content = e.content.read()
    state.uploaded[e.name] = content
    refresh_ui()


def on_metric_change() -> None:
    if metric_select.value is None:
        return
    state.selected_metric = str(metric_select.value)
    refresh_ui()


def clear_all() -> None:
    state.uploaded.clear()
    state.parsed = []
    state.chart_frames = []
    state.selected_metric = ''
    refresh_ui()


def on_theme_change(e: events.ValueChangeEventArguments) -> None:
    state.is_dark = bool(e.value)
    if dark_mode is not None:
        dark_mode.set_value(state.is_dark)
    refresh_ui()


ui.page_title('CSV Analyzer - NiceGUI')
dark_mode = ui.dark_mode(state.is_dark)
with ui.column().classes('w-full max-w-[1400px] mx-auto p-4 gap-4'):
    ui.label('CSV Analyzer').classes('text-h4')
    ui.label('Drag and drop jest głównym trybem importu (od 1 do 3 plików CSV).').classes('text-subtitle2')

    with ui.row().classes('items-center gap-3'):
        ui.switch('Tryb ciemny', value=state.is_dark, on_change=on_theme_change)

    upload = ui.upload(
        on_upload=on_upload,
        multiple=True,
        max_files=MAX_FILES,
        auto_upload=True,
    ).classes('w-full')
    upload.props('accept=.csv label="Przeciągnij i upuść pliki CSV (1-3 szt.)"')

    with ui.row().classes('items-center gap-3'):
        files_label = ui.label(f'Wgrane pliki CSV: 0 / {MAX_FILES}')
        status_label = ui.label('Wgraj od 1 do 3 plików CSV.')

    with ui.row().classes('items-end gap-3'):
        metric_select = ui.select(options=[], label='Wspólna metryka', on_change=lambda _: on_metric_change())
        export_button = ui.button('Eksport XLSX (Chart_01..N)', on_click=export_xlsx)
        clear_button = ui.button('Wyczyść', on_click=clear_all)

    export_button.disable()

    with ui.column().classes('w-full items-stretch gap-4'):
        chart_1 = ui.plotly(go.Figure()).classes('w-full').style('width: 100%; height: 500px').props('config={"responsive": true}')
        chart_2 = ui.plotly(go.Figure()).classes('w-full').style('width: 100%; height: 500px').props('config={"responsive": true}')
        chart_3 = ui.plotly(go.Figure()).classes('w-full').style('width: 100%; height: 500px').props('config={"responsive": true}')

    charts = [chart_1, chart_2, chart_3]
    for ch in charts:
        ch.set_visibility(False)

    preview_rows = ui.table(
        columns=[
            {'name': 'sample', 'label': 'sample', 'field': 'sample'},
            {'name': 'chart01', 'label': 'Chart_01', 'field': 'chart01'},
            {'name': 'chart02', 'label': 'Chart_02', 'field': 'chart02'},
            {'name': 'chart03', 'label': 'Chart_03', 'field': 'chart03'},
        ],
        rows=[],
        row_key='sample',
        pagination=10,
    ).classes('w-full').props('rows-per-page-options=[10] virtual-scroll').style('max-height: 360px')


if __name__ in {'__main__', '__mp_main__'}:
    try:
        ui.run(title='CSV Analyzer', reload=False)
    except KeyboardInterrupt:
        print('Aplikacja zatrzymana przez użytkownika (Ctrl+C).')
