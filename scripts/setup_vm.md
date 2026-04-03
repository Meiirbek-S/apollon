# VirtualBox sandbox setup (MVP)

1. Создать VM `WinSandbox`.
2. Отключить shared folders, clipboard, drag&drop.
3. Сконфигурировать сеть NAT (и host-only только при необходимости лог-сбора).
4. Установить guest-инструменты мониторинга (например Sysmon + custom collector).
5. Сделать clean snapshot `CleanState`.
