# Шаг 6: Enhanced static file analysis (MVP v1)

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

## Scoring model v1 (прозрачная)

Индикаторы и баллы:
- extension mismatch: +10
- high entropy section (>= 7.2): +12 за секцию
- executable + writable section: +15
- abnormal section name: +10
- packed/obfuscated heuristic (all sections high entropy): +15
- suspicious imports: +5 за импорт (до +30)
- PE-like extension but parse failed: +15

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
