import sys

from dotenv import load_dotenv
from sqlalchemy import select
from sqlalchemy.exc import OperationalError

from app.db.models import User
from app.db.session import SessionLocal
from app.security.password import hash_password
from app.scripts.common import print_database_connection_error


def main() -> int:
    load_dotenv()
    if len(sys.argv) != 3:
        print("Usage: python -m app.scripts.create_user <username> <password>", file=sys.stderr)
        return 1

    _, username, password = sys.argv
    session = SessionLocal()
    try:
        existing_user = session.scalar(select(User).where(User.username == username))
        if existing_user is not None:
            print(f'User "{username}" already exists.', file=sys.stderr)
            return 1

        user = User(username=username, password=hash_password(password))
        session.add(user)
        session.commit()
        session.refresh(user)

        print("User created successfully.")
        print(f"id: {user.id}")
        print(f"username: {user.username}")
        print(f"created_at: {user.created_at.isoformat()}")
        print("password: stored as bcrypt hash")
        return 0
    finally:
        session.close()


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except OperationalError as error:
        raise SystemExit(print_database_connection_error("create user", error))
