# 📦 Система резервного копирования CRM

## 📋 Конфигурация

| Параметр | Значение |
|----------|----------|
| Образ | `prodrigestivill/postgres-backup-local:latest` |
| Расписание | **Каждый час** (`BACKUP_FREQUENCY=60m`) |
| Дамп при старте | **Да** (`BACKUP_ON_START=TRUE`) |
| Сжатие | Максимальное (`-Z 9`) |
| Хранение daily | 30 файлов (`BACKUP_NUM_KEEP=30`) |
| Хранение weekly | 4 недели |
| Хранение monthly | 6 месяцев |
| Ожидание БД | До полной готовности (healthcheck) |

## 📁 Структура хранения
./infra/backups/
├── last/ # Последний дамп (с временной меткой)
├── daily/ # Ежедневные дампы (30 шт.)
├── weekly/ # Еженедельные дампы (4 шт.)
└── monthly/ # Ежемесячные дампы (6 шт.)

text

В каждой папке есть симлинк `latest.sql.gz` → актуальный файл.

---

## 🔄 Восстановление из дампа

### Восстановить последний дамп

```bash
gunzip -c ./infra/backups/last/crm_main_database-latest.sql.gz | docker compose exec -T db psql -U crm_admin -d crm_main_database
Восстановить с полной перезаписью таблиц
bash
gunzip -c ./infra/backups/last/crm_main_database-latest.sql.gz | docker compose exec -T db psql -U crm_admin -d crm_main_database --clean --if-exists
Восстановить конкретный daily-дамп
bash
gunzip -c ./infra/backups/daily/crm_main_database-20260618.sql.gz | docker compose exec -T db psql -U crm_admin -d crm_main_database
Восстановить weekly-дамп
bash
gunzip -c ./infra/backups/weekly/crm_main_database-latest.sql.gz | docker compose exec -T db psql -U crm_admin -d crm_main_database
Восстановить monthly-дамп
bash
gunzip -c ./infra/backups/monthly/crm_main_database-latest.sql.gz | docker compose exec -T db psql -U crm_admin -d crm_main_database
🔍 Проверка и мониторинг
Посмотреть содержимое дампа (первые 50 строк)
bash
gunzip -c ./infra/backups/last/crm_main_database-latest.sql.gz | head -50
Список всех дампов
bash
ls -lh ./infra/backups/last/
ls -lh ./infra/backups/daily/
ls -lh ./infra/backups/weekly/
ls -lh ./infra/backups/monthly/
Логи бэкап-контейнера
bash
docker compose logs backup --tail 20
Статус контейнера
bash
docker compose ps backup
⚠️ Важные замечания
Размер дампа 4 KB — нормально для пустой/тестовой БД. В продакшене будет больше.

Права на папку — если меняешь расположение ./infra/backups, выполни:

bash
mkdir -p ./infra/backups
chmod 777 ./infra/backups
Флаг -T в docker compose exec обязателен при использовании пайпа (|).

--clean --if-exists — удаляет существующие таблицы перед восстановлением. Используй осторожно!

🚀 Быстрый перезапуск бэкапа
bash
docker compose restart backup
docker compose logs backup --tail 10





docker exec -it crm_backup_service //backup.sh
бекапит сразу