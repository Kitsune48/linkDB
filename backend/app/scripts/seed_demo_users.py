from dotenv import load_dotenv
from sqlalchemy import select
from sqlalchemy.exc import OperationalError

from app.db.models import User
from app.db.session import SessionLocal
from app.security.password import hash_password
from app.scripts.common import print_database_connection_error


DEMO_USERS = [
    {"username": "alice", "password": "alice-demo-password"},
    {"username": "bob", "password": "bob-demo-password"},
]


def main() -> int:
    load_dotenv()
    session = SessionLocal()
    try:
        for demo_user in DEMO_USERS:
            user = session.scalar(select(User).where(User.username == demo_user["username"]))
            password_hash = hash_password(demo_user["password"])
            if user is None:
                session.add(
                    User(
                        username=demo_user["username"],
                        password=password_hash,
                    )
                )
            else:
                user.password = password_hash
        session.commit()

        print("Demo users upserted successfully.")
        print("Passwords are stored as bcrypt hashes in users.password.")
        print("Demo credentials:")
        for demo_user in DEMO_USERS:
            print(f'- {demo_user["username"]} / {demo_user["password"]}')
        return 0
    finally:
        session.close()


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except OperationalError as error:
        raise SystemExit(print_database_connection_error("seed demo users", error))
