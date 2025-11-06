# FinanceBot (Docker)

## Запуск локально
```
cp .env.example .env
# встав BOT_TOKEN
sudo docker compose up -d
```

## Backup бази
```
docker exec -t financebot_db pg_dump -U finance_user finance_db > backup.sql
```
Відновлення:
```
cat backup.sql | docker exec -i financebot_db psql -U finance_user finance_db
```