from pathlib import Path
import sqlite3
import os

def db_connect():
    path = os.environ.get("FORGE_DB_PATH", "digital_twin.db")
    database_path = Path(__file__).parent / path

    connection = sqlite3.connect(database_path)
    connection.row_factory = sqlite3.Row

    return connection

connection = db_connect()

cursor = connection.cursor()

def create_tables() -> None:
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS part_requirements (
            id TEXT,
            revision INTEGER,
            part TEXT,
            description TEXT,
            category TEXT,
            nominal REAL,
            upper_limit REAL,
            lower_limit REAL,
            primary_datum TEXT,
            secondary_datum TEXT,
            tertiary_datum TEXT,
            log_comment TEXT,
            PRIMARY KEY(id, revision)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS vehicle_requirements (
            id TEXT,
            revision INTEGER,
            program TEXT,
            system TEXT,
            description TEXT,
            nominal REAL,
            lower_limit REAL,
            upper_limit REAL,
            log_comment TEXT,
            PRIMARY KEY(id, revision)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tolerance_stacks (
            id TEXT,
            revision INTEGER,
            description TEXT,
            target_requirement_id TEXT,
            target_requirement_revision INTEGER,
            life_cycle_status TEXT,
            target_changed INTEGER,
            review_required INTEGER,
            review_remark TEXT,
            validation_changed INTEGER,
            PRIMARY KEY(id, revision)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS contributors (
            id INTEGER PRIMARY KEY,
            stack_id TEXT,
            stack_revision INTEGER,
            requirement_id TEXT,
            requirement_revision INTEGER,
            instance_label TEXT
        )
    """)

    connection.commit()

def get_latest_part_requirement(requirement_id: str):
    cursor.execute("""
        SELECT *
        FROM part_requirements
        WHERE id = ?
        ORDER BY revision DESC
        LIMIT 1
    """, (requirement_id,))
    return cursor.fetchone()

def get_latest_part_requirements():
    cursor.execute("""
        SELECT *
        FROM part_requirements
        WHERE (id, revision) IN (
            SELECT id, MAX(revision)
            FROM part_requirements
            GROUP BY id
        )
        ORDER BY id
    """)
    return cursor.fetchall()

def get_rev_of_part_requirement(requirement_id: str, revision: int):
    cursor.execute("""
        SELECT *
        FROM part_requirements
        WHERE id = ? AND revision = ?
    """,(requirement_id, revision))
    return cursor.fetchone()

def get_latest_vehicle_requirement(requirement_id: str):
    cursor.execute("""
        SELECT *
        FROM vehicle_requirements
        WHERE id = ?
        ORDER BY revision DESC
        LIMIT 1
    """, (requirement_id,))
    return cursor.fetchone()

def get_latest_vehicle_requirements():
    cursor.execute("""
        SELECT *
        FROM vehicle_requirements
        WHERE (id, revision) IN (
            SELECT id, MAX(revision)
            FROM vehicle_requirements
            GROUP BY id
        )
        ORDER BY id
    """)
    return cursor.fetchall()

def get_rev_of_vehicle_requirement(requirement_id:str, revision: int):
    cursor.execute("""
        SELECT *
        FROM vehicle_requirements
        WHERE id = ? AND revision = ?
    """,(requirement_id, revision)
    )
    return cursor.fetchone()

def get_all_latest_part_requirement_revisions():
    cursor.execute("""
        SELECT id, MAX(revision) AS revision
        FROM part_requirements
        GROUP BY id
    """)
    return cursor.fetchall()

def get_latest_tolerance_stack_revision(stack_id: str):
    cursor.execute(
        """
        SELECT *
        FROM tolerance_stacks
        WHERE id = ?
        ORDER BY revision DESC
        LIMIT 1
        """, (stack_id,)
    )
    return cursor.fetchone()

def get_current_tolerance_stack(stack_id: str):
    cursor.execute(
        """
        SELECT *
        FROM tolerance_stacks
        WHERE id = ? AND life_cycle_status = "current"
        """, (stack_id,)
    )
    return cursor.fetchone()

def get_tolerance_stacks_to_review():
    cursor.execute(
        """
        SELECT *
        FROM tolerance_stacks
        WHERE review_required = 1
        """
    )
    return cursor.fetchall()

def get_revision_of_stack(stack_id: str, revision:int):
    cursor.execute("""
        SELECT *
        FROM tolerance_stacks
        WHERE id = ? AND revision =?
    """, (stack_id, revision)
    )
    return cursor.fetchone()

def get_contributors_for_tolerance_stack(stack_id: str, revision:int):
    cursor.execute("""
        SELECT*
        FROM contributors
        WHERE stack_id = ? AND stack_revision = ?
    """, (stack_id, revision)
    )
    return cursor.fetchall()

def get_all_current_stacks():
    cursor.execute("""
        SELECT id, revision, description, target_requirement_id
        FROM tolerance_stacks
        WHERE life_cycle_status = 'current'
        ORDER BY id
    """)
    return cursor.fetchall()

connection.commit()

if __name__ == "__main__":
    connection.close()