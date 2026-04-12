# Шаг 7: Подготовка Dynamic Analysis (Container Sandbox) без запуска malware

Цель этапа:
- подготовить backend к подключению isolated dynamic analysis,
- не запускать ничего на хосте,
- сделать безопасный orchestration-контур для следующего шага.

## Что делаем в этом этапе

1. Добавляем контракт dynamic-analysis в БД и API (без исполнения):
- `dynamic_requested` для submission,
- `dynamic_status` (`NOT_REQUESTED|QUEUED|RUNNING|DONE|FAILED`),
- `dynamic_report` (JSON, nullable).

2. Добавляем Celery task-заглушку:
- `submission.process_dynamic` (пока без Container Sandbox вызова),
- переводит статус `QUEUED -> RUNNING -> FAILED_SAFE` по timeout-шаблону,
- пишет audit-событие.

3. Добавляем strict safety guardrails (код + конфиг):
- явный флаг `DYNAMIC_EXECUTION_ENABLED=false` по умолчанию,
- если флаг false — только dry-run заглушка,
- запрет любых локальных subprocess запусков sample на host.

4. Подготавливаем интерфейс Container Sandbox controller (adapter layer):
- `prepare_vm()`
- `restore_snapshot()`
- `copy_sample_in()`
- `execute_in_guest()`
- `collect_artifacts()`
- `rollback_vm()`

Все методы на этом этапе: `NotImplemented` + typed контракты.

---

## Что НЕ делаем на этом этапе

- не исполняем образцы,
- не подключаем реальный Docker CLI/API,
- не открываем network egress из sandbox,
- не добавляем YARA/EDR/advanced hooks.

---

## Критерий завершения этапа

- API умеет принимать флаг dynamic request,
- submission получает отдельный dynamic lifecycle status,
- worker вызывает dynamic task-заглушку,
- в коде есть безопасный adapter-контур под Container Sandbox,
- доказуемо отсутствует host execution path.

---

## Следующий шаг (Step 8)

Подключение реального Container Sandbox controller:
- snapshot restore,
- guest execution,
- artifact collection,
- rollback после каждого запуска.
