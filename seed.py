from app import create_app, db
from app.models import User

app = create_app()


def seed_users():
    with app.app_context():
        db.create_all()

        if User.query.first() is None:
            print("testowi uzytkownicy")

            users_data = [
                {'username': 'szef', 'email': 'szef@warsztat.pl', 'role': 'szef', 'first_name': 'Jan',
                 'last_name': 'Kowalski'},
                {'username': 'recepcja1', 'email': 'recepcja@warsztat.pl', 'role': 'recepcja', 'first_name': 'Anna',
                 'last_name': 'Nowak'},
                {'username': 'mechanik1', 'email': 'mechanik1@warsztat.pl', 'role': 'mechanik', 'first_name': 'Piotr',
                 'last_name': 'Zieliński'},
                {'username': 'klient1', 'email': 'klient@mail.pl', 'role': 'klient', 'first_name': 'Tomasz',
                 'last_name': 'Lis'}
            ]

            for u_data in users_data:
                user = User(
                    username=u_data['username'],
                    email=u_data['email'],
                    role=u_data['role'],
                    first_name=u_data['first_name'],
                    last_name=u_data['last_name']
                )
                user.set_password('haslo123')
                db.session.add(user)

            db.session.commit()
            print("Dodano konta: szef, recepcja1, mechanik1, klient1 (haslo: haslo123)")
        else:
            print("W bazie są użytkownicy. nie trzeba dodawać testowych")

        from app.models import Part
        if Part.query.first() is None:
            print("Testowe części w magazynie")
            parts_data = [
                Part(name='Klocki hamulcowe przód (Bosh)', part_number='BOS-1234', price=150.00, stock_quantity=12),
                Part(name='Tarcza hamulcowa wentylowana', part_number='TRW-998', price=210.00, stock_quantity=4),
                Part(name='Olej silnikowy 5W-30 5L (Castrol)', part_number='CAS-5W30', price=180.00, stock_quantity=20),
                Part(name='Filtr oleju (Filtron)', part_number='FIL-001', price=35.00, stock_quantity=15),
                Part(name='Uszczelka pod głowice (Erling)', part_number='ERL-888', price=120.00, stock_quantity=0)
                # Brak na stanie
            ]
            db.session.add_all(parts_data)
            db.session.commit()


if __name__ == '__main__':