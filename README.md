### Предварительные требования

Убедитесь, что у вас установлен Python 3.7 или выше и PostgreSQL.

### Установка зависимостей
```
pip install fastapi[all] sqlalchemy psycopg2-binary passlib python-jose
```

```
pip install bcrypt
```

## Запуск
``` 
uvicorn main:app --reload
```
## Проверка 
```
http://127.0.0.1:8000/docs
```
