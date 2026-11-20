from database.database import Base, engine, SessionLocal
from database.models import Author, Book, Genre, Publisher, Reader

Base.metadata.create_all(bind=engine)
db = SessionLocal()
try:
    authors_data = [
        ("Тарас Шевченко", "Український поет і художник"),
        ("Іван Франко", "Український письменник і науковець"),
        ("Леся Українка", "Українська письменниця і поетеса"),
        ("Михайло Коцюбинський", "Український письменник"),
        ("Джордж Орвелл", "Англійський письменник"),
        ("Жуль Верн", "Французький письменник"),
        ("Артур Конан Дойл", "Британський письменник"),
    ]
    for name, bio in authors_data:
        if not db.query(Author).filter_by(name=name).first():
            db.add(Author(name=name, biography=bio))
    for name, city in [("А-БА-БА-ГА-ЛА-МА-ГА", "Київ"), ("Фоліо", "Харків"),
                       ("Клуб Сімейного Дозвілля", "Харків"), ("Видавництво Старого Лева", "Львів")]:
        if not db.query(Publisher).filter_by(name=name).first():
            db.add(Publisher(name=name, city=city))
    for name in ["Поезія", "Роман", "Пригоди", "Фантастика", "Детектив", "Повість"]:
        if not db.query(Genre).filter_by(name=name).first():
            db.add(Genre(name=name))
    db.commit()
    A = {x.name: x for x in db.query(Author).all()}
    P = {x.name: x for x in db.query(Publisher).all()}
    G = {x.name: x for x in db.query(Genre).all()}
    rows = [
        ("Кобзар","Тарас Шевченко","А-БА-БА-ГА-ЛА-МА-ГА",1840,320,["Поезія"]),
        ("Гайдамаки","Тарас Шевченко","Фоліо",1841,180,["Поезія"]),
        ("Катерина","Тарас Шевченко","Фоліо",1838,64,["Поезія"]),
        ("Захар Беркут","Іван Франко","Клуб Сімейного Дозвілля",1883,240,["Роман"]),
        ("Мойсей","Іван Франко","Фоліо",1905,120,["Поезія"]),
        ("Лис Микита","Іван Франко","А-БА-БА-ГА-ЛА-МА-ГА",1890,160,["Пригоди"]),
        ("Лісова пісня","Леся Українка","Видавництво Старого Лева",1911,128,["Повість"]),
        ("Кассандра","Леся Українка","Фоліо",1908,150,["Роман"]),
        ("Тіні забутих предків","Михайло Коцюбинський","Фоліо",1911,160,["Повість"]),
        ("Intermezzo","Михайло Коцюбинський","Фоліо",1908,48,["Повість"]),
        ("1984","Джордж Орвелл","Клуб Сімейного Дозвілля",1949,328,["Роман","Фантастика"]),
        ("Колгосп тварин","Джордж Орвелл","Фоліо",1945,120,["Роман"]),
        ("Двадцять тисяч льє під водою","Жуль Верн","А-БА-БА-ГА-ЛА-МА-ГА",1870,420,["Пригоди","Фантастика"]),
        ("Навколо світу за 80 днів","Жуль Верн","Фоліо",1872,280,["Пригоди"]),
        ("Таємничий острів","Жуль Верн","Фоліо",1874,500,["Пригоди","Фантастика"]),
        ("Собака Баскервілів","Артур Конан Дойл","Клуб Сімейного Дозвілля",1902,240,["Детектив"]),
        ("Знак чотирьох","Артур Конан Дойл","Фоліо",1890,180,["Детектив"]),
    ]
    for title, author, pub, year, pages, genre_names in rows:
        if not db.query(Book).filter_by(title=title, author_id=A[author].id).first():
            db.add(Book(title=title, author_id=A[author].id, publisher_id=P[pub].id,
                        year=year, pages=pages, genres=[G[n] for n in genre_names]))
    for name, email in [("Олена Петренко","olena@example.com"),
                        ("Андрій Коваль","andrii@example.com"),
                        ("Марія Шевчук","maria@example.com")]:
        if not db.query(Reader).filter_by(email=email).first():
            db.add(Reader(name=name, email=email))
    db.commit()
    print("Added sample data: 7 authors, 17 books, 4 publishers, 6 genres, 3 readers.")
finally:
    db.close()
