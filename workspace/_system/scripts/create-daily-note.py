#!/usr/bin/env python3
"""
Daily Note Creation Script

Creates daily notes on-demand (lazy creation) with YYYY-MM-DD format.
Configurable sections from vault-config.yaml.
"""

import argparse
import os
import sys
import uuid
from datetime import date, datetime
from pathlib import Path

import yaml


def get_vault_config(vault_path: str) -> dict:
    """Load vault-config.yaml"""
    config_path = Path(vault_path) / "_system" / "vault-config.yaml"
    if not config_path.exists():
        raise FileNotFoundError(f"Vault config not found: {config_path}")
    with open(config_path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def get_daily_config(vault_path: str) -> dict:
    """Extract daily note settings from vault config"""
    config = get_vault_config(vault_path)
    return config.get("daily_notes", {})


def format_date(date_obj: date, fmt: str) -> str:
    """Format date to YYYY-MM-DD"""
    return date_obj.strftime("%Y-%m-%d")


def daily_note_exists(vault_path: str, date_str: str, extension: str) -> bool:
    """Check if daily note already exists"""
    config = get_daily_config(vault_path)
    folder = config.get("folder", "01-Daily")
    daily_folder = Path(vault_path) / folder
    note_path = daily_folder / f"{date_str}{extension}"
    return note_path.exists()


def get_template(vault_path: str, template_name: str = "daily") -> str:
    """Load template content"""
    template_path = Path(vault_path) / "_system" / "templates" / f"{template_name}.md"
    if not template_path.exists():
        raise FileNotFoundError(f"Template not found: {template_path}")
    with open(template_path, encoding="utf-8") as f:
        return f.read()


def render_template(template: str, context: dict) -> str:
    """Replace placeholders in template"""
    result = template
    for key, value in context.items():
        placeholder = f"{{{{{key}}}}}"
        result = result.replace(placeholder, str(value))
    return result


def create_daily_note(vault_path: str, date_obj: date, template_profile: str = None) -> Path:
    """Create a daily note for the given date"""
    config = get_daily_config(vault_path)

    # Check if daily notes are enabled
    if not config.get("enabled", True):
        raise ValueError("Daily notes are not enabled in vault config")

    # Get daily folder
    folder = config.get("folder", "01-Daily")
    daily_folder = Path(vault_path) / folder
    daily_folder.mkdir(parents=True, exist_ok=True)

    # Get format settings
    date_str = format_date(date_obj, config.get("format", "YYYY-MM-DD"))
    extension = config.get("extension", ".md")
    note_path = daily_folder / f"{date_str}{extension}"

    # Check if already exists (lazy creation)
    if note_path.exists():
        print(f"Daily note already exists: {note_path}")
        return note_path

    # Get sections from config
    sections = config.get("sections", [])

    # Build context for template
    now = datetime.utcnow()
    context = {
        "id": str(uuid.uuid4()),
        "date": date_str,
        "created_at": now.isoformat(),
        "updated_at": now.isoformat(),
    }

    # Load and render template
    template = get_template(vault_path, "daily")
    content = render_template(template, context)

    # Write the note
    with open(note_path, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"Created daily note: {note_path}")
    return note_path


def link_project_to_daily(note_path: Path, project_id: str) -> None:
    """Link a project to a daily note via frontmatter"""
    # This would update the links.project field in the frontmatter
    # Implementation depends on policy engine in later phase
    pass


def main():
    parser = argparse.ArgumentParser(description="Create daily notes")
    parser.add_argument(
        "--vault",
        default=os.getcwd(),
        help="Path to vault (default: current directory)"
    )
    parser.add_argument(
        "--date",
        help="Date in YYYY-MM-DD format (default: today)"
    )
    parser.add_argument(
        "--profile",
        help="Template profile name (optional)"
    )

    args = parser.parse_args()

    # Parse date
    if args.date:
        try:
            date_obj = datetime.strptime(args.date, "%Y-%m-%d").date()
        except ValueError:
            print(f"Invalid date format: {args.date}. Use YYYY-MM-DD.")
            sys.exit(1)
    else:
        date_obj = date.today()

    try:
        note_path = create_daily_note(args.vault, date_obj, args.profile)
        print(f"Daily note created: {note_path}")
    except Exception as e:
        print(f"Error creating daily note: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
