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
        print(
            "Usage: python -m app.scripts.reset_password <username> <new-password>",
            file=sys.stderr,
        )
        return 1

    _, username, new_password = sys.argv
    session = SessionLocal()
    try:
        user = session.scalar(select(User).where(User.username == username))
        if user is None:
            print(f'User "{username}" not found.', file=sys.stderr)
            return 1

        user.password = hash_password(new_password)
        session.commit()
        print(f'Password updated successfully for "{user.username}".')
        print("password: stored as bcrypt hash")
        return 0
    finally:
        session.close()


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except OperationalError as error:
        raise SystemExit(print_database_connection_error("reset password", error))
