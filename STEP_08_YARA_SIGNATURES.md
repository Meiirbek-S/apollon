# Шаг 8: YARA signature scanning

## Что добавлено
- Интегрирован сигнатурный анализ YARA в static file analysis worker.
- Добавлены дефолтные YARA-правила (`backend/yara_rules/default_rules.yar`), включая детект EICAR.
- Результаты YARA теперь сохраняются в БД (`yara_matched`, `yara_match_count`, `yara_rule_names`).
- Данные YARA возвращаются API и отображаются во frontend-отчете по файлу.

## Архитектура интеграции
1. Worker в `_analyze_file` после PE/эвристик вызывает `_scan_with_yara(temp_path)`.
2. `_scan_with_yara` компилирует все `.yar/.yara` из `settings.yara_rules_dir`.
3. Совпадения правил добавляются в risk indicators и увеличивают общий `risk_score`.
4. Итоги сохраняются в `static_analysis_results`.

## Конфигурация
Новые параметры в `Settings`:
- `yara_enabled` (bool, default `True`) — включение/выключение YARA-сканирования.
- `yara_rules_dir` (str, default `/app/yara_rules`) — путь к каталогу с YARA-правилами.
- `yara_match_score` (int, default `40`) — базовый вес YARA-срабатывания в score.

## Миграция БД
Добавлена миграция `20260412_0008_add_yara_results_to_static_analysis.py`, которая добавляет поля:
- `yara_matched` (bool)
- `yara_match_count` (int)
- `yara_rule_names` (json array)

## Тестирование на EICAR
### 1. Запуск сервисов
```bash
cd /workspace/apollon
cp .env.example .env
docker compose -f infra/docker-compose.yml up -d --build
docker compose -f infra/docker-compose.yml exec api alembic upgrade head
```

### 2. Подготовка EICAR-файла
```bash
cat > /tmp/eicar.com <<'EICAR'
X5O!P%@AP[4\PZX54(P^)7CC)7}$EICAR-STANDARD-ANTIVIRUS-TEST-FILE!$H+H*
EICAR
```

### 3. Отправка файла на анализ
```bash
curl -s -X POST \
  -F "file=@/tmp/eicar.com" \
  http://localhost:8000/api/v1/submissions/file/upload
```

### 4. Получение отчета
```bash
curl -s http://localhost:8000/api/v1/submissions/<submission_id>/report
```

Ожидаемо в отчете:
- `report.yara_matched = true`
- `report.yara_match_count >= 1`
- `report.yara_rule_names` содержит `EICAR_Test_File`
- `risk_indicators` содержит строки вида `yara match: ...`

## Расширение сигнатур
- Добавляйте новые `.yar/.yara` файлы в `backend/yara_rules/`.
- Перезапускайте API/worker после обновления правил.
- Для production рекомендуется хранить правила в отдельном репозитории и подписывать релизы правил.

## Troubleshooting (500 при /report после внедрения YARA)
Если видите 500/503 и в деталях фигурируют `yara_matched`, `yara_match_count` или `yara_rule_names`, почти всегда причина — миграция не применена в БД.

Проверка:
```bash
docker compose -f infra/docker-compose.yml logs api --tail=200
docker compose -f infra/docker-compose.yml logs worker --tail=200
docker compose -f infra/docker-compose.yml exec api alembic current
docker compose -f infra/docker-compose.yml exec api alembic upgrade head
docker compose -f infra/docker-compose.yml exec postgres psql -U apollon -d apollon -c "\\d+ static_analysis_results"
```

В таблице `static_analysis_results` должны присутствовать поля:
- `yara_matched`
- `yara_match_count`
- `yara_rule_names`
