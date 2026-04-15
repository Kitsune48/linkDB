import sys

from dotenv import load_dotenv
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError, OperationalError

from app.db.models import User
from app.db.session import SessionLocal
from app.scripts.common import print_database_connection_error


def main() -> int:
    load_dotenv()
    if len(sys.argv) != 2:
        print("Usage: python -m app.scripts.delete_user <username>", file=sys.stderr)
        return 1

    _, username = sys.argv
    session = SessionLocal()
    try:
        user = session.scalar(select(User).where(User.username == username))
        if user is None:
            print(f'User "{username}" not found.', file=sys.stderr)
            return 1

        session.delete(user)
        session.commit()
        print(f'User "{username}" deleted successfully.')
        return 0
    except IntegrityError:
        session.rollback()
        print(f'Cannot delete "{username}" because related records still exist.', file=sys.stderr)
        print("Delete or reassign the user's links first.", file=sys.stderr)
        return 1
    finally:
        session.close()


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except OperationalError as error:
        raise SystemExit(print_database_connection_error("delete user", error))
