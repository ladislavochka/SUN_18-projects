# Полиця: Books API

FastAPI + SQLAlchemy + JWT, зі стильним веб-інтерфейсом на головній сторінці.

## Запуск
```bash
python -m venv .venv && source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env                                    # і постав свій SECRET_KEY
python seed.py                                          # (необов'язково) демо-книги, вхід demo / demo12345
uvicorn main:app --reload
```
- Інтерфейс: http://127.0.0.1:8000/
- Swagger: http://127.0.0.1:8000/docs

Тести: `pip install -r requirements-dev.txt && pytest`

## API
| Метод | Шлях | Доступ | Що робить |
|---|---|---|---|
| POST | `/auth/register` | всі | реєстрація (перевірка username і email) |
| POST | `/auth/login` | всі | вхід за ім'ям або email |
| GET | `/auth/me` | токен | мій профіль |
| GET | `/books/` | всі | список: `q`, `genre`, `author`, `sort`, `page`, `size` |
| GET | `/books/my` | токен | мої книги (ті самі параметри) |
| GET | `/books/genres` | всі | список жанрів |
| GET | `/books/stats` | всі | статистика бібліотеки |
| GET | `/books/{id}` | всі | одна книга |
| POST | `/books/` | токен | додати книгу |
| PATCH | `/books/{id}` | власник | змінити книгу |
| DELETE | `/books/{id}` | власник | видалити книгу |

`sort`: `newest` (за замовчуванням), `oldest`, `title`, `author`, `rating`.
Списки повертають `{items, total, page, size, pages}`.
