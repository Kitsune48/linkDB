from sqlalchemy.exc import OperationalError


def print_database_connection_error(command_name: str, error: OperationalError) -> int:
    print(f"Failed to {command_name}.")
    print("Database connection failed.")
    print(str(error))
    print(
        "Check that MySQL is running and that backend/.env DATABASE_URL matches infra/.env MYSQL_PASSWORD."
    )
    return 1
