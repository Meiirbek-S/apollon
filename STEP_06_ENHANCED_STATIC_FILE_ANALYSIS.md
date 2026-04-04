# Шаг 6: Enhanced static file analysis (MVP v2 scoring)

На этом шаге усиливаем file static-report без VirtualBox и без YARA.

## Что добавлено в report

Для любого файла:
- submission_id
- original_filename
- md5
- sha256
- file_size
- mime_type
- extension
- extension_mismatch
- risk_score
- risk_level
- risk_indicators
- verdict_reason
- created_at

Для PE-файлов дополнительно:
- is_pe
- machine_type
- compile_timestamp
- entry_point
- image_base
- pe_sections[]
- imported_functions[]
- suspicious_imports[]

---

## Scoring model v2 (прозрачная)

Базовые факторы:
- extension mismatch: +10
- high entropy section (>7.2): +10 за секцию
- RWX section: +15 за секцию
- abnormal section name (`upx0/upx1/upx2/.upx/...`): +10
- packed/obfuscated heuristic (all sections entropy>=7.0): +15
- PE-like extension but parse failed: +25
- suspicious compile timestamp year (<2000 или > current_year+1): +5

Suspicious imports (взвешенно):
- `VirtualAlloc`: +10
- `CreateRemoteThread`: +12
- `WriteProcessMemory`: +12
- `CreateProcess*`: +8
- `LoadLibrary*`: +5
- `GetProcAddress`: +6
- `WinExec`: +8
- `ShellExecute*`: +6
- `InternetOpen/InternetConnect/URLMon`: +5
- `RegSetValue*`: +6
- count bonus: `+2 * N`, максимум +15

Пороги:
- 0–24 => SAFE
- 25–59 => SUSPICIOUS
- 60+ => MALWARE-LIKE

---

## Миграция

Добавлена миграция:
- `20260404_0006_expand_static_analysis_result_fields.py`

---

## Команды

```bash
docker compose -f infra/docker-compose.yml down
docker compose -f infra/docker-compose.yml up -d --build
docker compose -f infra/docker-compose.yml exec api alembic upgrade head
```

Проверка file flow:

```bash
curl -X POST http://localhost:8000/api/v1/submissions/file/upload \
  -F "file=@/absolute/path/to/sample.exe"

curl http://localhost:8000/api/v1/submissions/<submission_id>
curl http://localhost:8000/api/v1/submissions/<submission_id>/report
```
