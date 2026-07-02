import psycopg


class HealthDatabaseError(Exception):
	"""Возникает, когда проверка доступности базы данных завершается ошибкой."""


def check_database_health(conn: psycopg.Connection) -> None:
	query = "SELECT 1"

	try:
		with conn.cursor() as cur:
			cur.execute(query)
			cur.fetchone()
	except psycopg.Error as exc:
		raise HealthDatabaseError("Проверка доступности базы данных завершилась ошибкой") from exc
