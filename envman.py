import os
import sqlite3
import json
import subprocess
import urllib.request
import json as json_module
from pathlib import Path
import click
import keyring
from cryptography.fernet import Fernet, InvalidToken

VERSION = "0.1.0"
REPO_OWNER = "adityamiskin"
REPO_NAME = "envman"

KEYCHAIN_SERVICE = "envman"
KEYCHAIN_KEY_NAME = "encryption_key"


def get_or_create_key():
    key = keyring.get_password(KEYCHAIN_SERVICE, KEYCHAIN_KEY_NAME)
    if not key:
        key = Fernet.generate_key().decode()
        keyring.set_password(KEYCHAIN_SERVICE, KEYCHAIN_KEY_NAME, key)
    return key


def encrypt(content: str) -> str:
    key = get_or_create_key()
    f = Fernet(key.encode())
    return f.encrypt(content.encode()).decode()


def decrypt(encrypted: str) -> str:
    key = get_or_create_key()
    f = Fernet(key.encode())
    return f.decrypt(encrypted.encode()).decode()


def is_encrypted(content: str) -> bool:
    try:
        decrypt(content)
        return True
    except (InvalidToken, Exception):
        return False


STORAGE_DIR = Path.home() / ".envman"
STORAGE_FILE = STORAGE_DIR / "data.db"
LEGACY_JSON_FILE = STORAGE_DIR / "data.json"


def get_db():
    if not STORAGE_DIR.exists():
        STORAGE_DIR.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(STORAGE_FILE)
    conn.row_factory = sqlite3.Row
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS projects (
            name TEXT PRIMARY KEY
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS env_files (
            project_name TEXT,
            filename TEXT,
            content TEXT,
            PRIMARY KEY (project_name, filename),
            FOREIGN KEY (project_name) REFERENCES projects(name) ON DELETE CASCADE
        )
        """
    )
    conn.commit()
    return conn


def migrate_json_to_sqlite():
    if not LEGACY_JSON_FILE.exists():
        return

    with open(LEGACY_JSON_FILE, "r") as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError:
            return

    conn = get_db()
    for project_name, project_data in data.get("projects", {}).items():
        conn.execute(
            "INSERT OR IGNORE INTO projects (name) VALUES (?)", (project_name,)
        )
        for filename, content in project_data.get("env_files", {}).items():
            content = content.replace("\\n", "\n")
            conn.execute(
                "INSERT OR REPLACE INTO env_files (project_name, filename, content) VALUES (?, ?, ?)",
                (project_name, filename, content),
            )
    conn.commit()
    conn.close()

    LEGACY_JSON_FILE.rename(LEGACY_JSON_FILE.with_suffix(".json.bak"))
    click.echo("Migrated legacy JSON data to SQLite.")


def migrate_plaintext_to_encrypted():
    conn = get_db()
    cursor = conn.execute("SELECT project_name, filename, content FROM env_files")
    for row in cursor.fetchall():
        if not is_encrypted(row["content"]):
            encrypted = encrypt(row["content"])
            conn.execute(
                "UPDATE env_files SET content = ? WHERE project_name = ? AND filename = ?",
                (encrypted, row["project_name"], row["filename"]),
            )
    conn.commit()
    conn.close()


def detect_project():
    try:
        git_root = subprocess.check_output(
            ["git", "rev-parse", "--show-toplevel"],
            stderr=subprocess.DEVNULL,
            universal_newlines=True,
        ).strip()
        return os.path.basename(git_root)
    except (
        subprocess.CalledProcessError,
        FileNotFoundError,
        subprocess.SubprocessError,
    ):
        pass
    return os.path.basename(os.getcwd())


@click.group()
@click.option(
    "--version",
    is_flag=True,
    expose_value=False,
    callback=lambda ctx, param, value: click.echo(f"envman {VERSION}")
    if value
    else None,
)
def cli():
    """EnvMan: Manage your project environment files easily."""
    migrate_json_to_sqlite()
    migrate_plaintext_to_encrypted()


def get_latest_version():
    try:
        url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/releases/latest"
        with urllib.request.urlopen(url, timeout=5) as response:
            data = json_module.loads(response.read().decode())
            return data.get("tag_name", "").lstrip("v")
    except Exception:
        return None


def version_compare(v1, v2):
    def parse(v):
        return [int(x) for x in v.split(".")]

    return parse(v1) > parse(v2)


@cli.command(name="version")
def version_cmd():
    """Check installed version and compare with latest release."""
    click.echo(f"envman {VERSION}")

    latest = get_latest_version()
    if latest:
        if version_compare(latest, VERSION):
            click.echo(f"Latest: {latest} (update available)")
            click.echo(
                f"Install: curl -sSf https://raw.githubusercontent.com/{REPO_OWNER}/{REPO_NAME}/main/install.sh | sh"
            )
        else:
            click.echo(f"Latest: {latest} (up to date)")
    else:
        click.echo("Latest: unknown (could not fetch release info)")


@cli.command()
@click.argument("filename", default=".env")
def add(filename):
    """Add a local env file to storage."""
    project = detect_project()
    path = Path(filename)

    if not path.exists():
        click.echo(f"Error: File '{filename}' not found.")
        return

    content = path.read_text().strip("\n")
    encrypted = encrypt(content)
    conn = get_db()

    conn.execute("INSERT OR IGNORE INTO projects (name) VALUES (?)", (project,))
    conn.execute(
        "INSERT OR REPLACE INTO env_files (project_name, filename, content) VALUES (?, ?, ?)",
        (project, filename, encrypted),
    )
    conn.commit()
    conn.close()
    click.echo(f"Added '{filename}' to project '{project}'.")


@cli.command()
@click.option("--output", "-o", help="Output filename")
@click.option("--project", "-p", help="Project name (defaults to current directory)")
@click.argument("filename", default=".env", required=False)
def get(filename, output, project):
    """Retrieve an env file from storage."""
    project = project or detect_project()
    conn = get_db()

    cursor = conn.execute(
        "SELECT content FROM env_files WHERE project_name = ? AND filename = ?",
        (project, filename),
    )
    row = cursor.fetchone()
    conn.close()

    if not row:
        click.echo(f"Error: '{filename}' not found for project '{project}'.")
        return

    try:
        content = decrypt(row["content"])
    except InvalidToken:
        content = row["content"]

    output_path = Path(output if output else filename)
    output_path.write_text(content + "\n")
    click.echo(f"Restored '{filename}' to '{output_path}'.")


@cli.command()
@click.argument("filename", default=".env")
def update(filename):
    """Update stored env file with local content."""
    ctx = click.get_current_context()
    ctx.invoke(add, filename=filename)


@cli.command()
@click.argument("filename", default=".env")
def delete(filename):
    """Delete an env file from storage."""
    project = detect_project()
    conn = get_db()

    cursor = conn.execute(
        "SELECT 1 FROM env_files WHERE project_name = ? AND filename = ?",
        (project, filename),
    )
    if not cursor.fetchone():
        conn.close()
        click.echo(f"Error: '{filename}' not found for project '{project}'.")
        return

    conn.execute(
        "DELETE FROM env_files WHERE project_name = ? AND filename = ?",
        (project, filename),
    )
    conn.commit()
    conn.close()
    click.echo(f"Deleted '{filename}' from project '{project}'.")


@cli.command(name="list")
@click.option("--project", "-p", help="Project name (defaults to current directory)")
def list_files(project):
    """List all stored files for the current project."""
    project = project or detect_project()
    conn = get_db()

    cursor = conn.execute(
        "SELECT filename FROM env_files WHERE project_name = ?", (project,)
    )
    files = cursor.fetchall()
    conn.close()

    if not files:
        click.echo(f"No files stored for project '{project}'.")
        return

    click.echo(f"Stored files for '{project}':")
    for row in files:
        click.echo(f" - {row['filename']}")


@cli.group()
def projects():
    """Manage projects."""
    pass


@projects.command(name="list")
def projects_list():
    """List all managed projects."""
    conn = get_db()
    cursor = conn.execute("SELECT name FROM projects ORDER BY name")
    projects = cursor.fetchall()
    conn.close()

    if not projects:
        click.echo("No projects managed yet.")
        return

    click.echo("Managed projects:")
    for row in projects:
        click.echo(f" - {row['name']}")


@projects.command(name="delete")
@click.argument("project_name")
def projects_delete(project_name):
    """Delete a project and all its stored files."""
    conn = get_db()

    cursor = conn.execute("SELECT 1 FROM projects WHERE name = ?", (project_name,))
    if not cursor.fetchone():
        conn.close()
        click.echo(f"Error: Project '{project_name}' not found.")
        return

    conn.execute("DELETE FROM projects WHERE name = ?", (project_name,))
    conn.commit()
    conn.close()
    click.echo(f"Deleted project '{project_name}'.")


if __name__ == "__main__":
    cli()
