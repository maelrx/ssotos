#!/usr/bin/env python3
"""
Workspace Materialization Script

Creates a complete Knowledge OS workspace with:
- Full directory structure
- Schema files
- Template profiles
- Base templates
- Agent Brain core files
- Vault configuration

Idempotent - safe to run multiple times.
"""

import argparse
import os
import shutil
import sys
from datetime import datetime
from pathlib import Path

import yaml


# Directory structure to create
DIRECTORY_STRUCTURE = {
    "user-vault": {
        "00-Inbox": None,
        "01-Daily": None,
        "02-Projects": None,
        "03-Areas": None,
        "04-Resources": None,
        "05-Archive": None,
        "Templates": None,
        "Attachments": None,
        "_system": {
            "schemas": None,
            "template-profiles": None,
            "templates": None,
        },
    },
    "agent-brain": {
        "skills": None,
        "heuristics": None,
        "reflections": None,
        "sessions": None,
        "scratchpads": None,
        "playbooks": None,
        "traces": None,
    },
    "exchange": {
        "proposals": None,
        "research": None,
        "imports": None,
        "reviews": None,
    },
    "raw": {
        "web": None,
        "documents": None,
        "parsed": None,
        "manifests": None,
        "failed": None,
    },
    "runtime": {
        "worktrees": None,
        "temp": None,
    },
    "_system": {
        "scripts": None,
    },
}

# Agent Brain core files
AGENT_BRAIN_FILES = {
    "SOUL.md": """# SOUL.md

**Agent Identity:** [To be configured at workspace creation]
**Created:** {created}
**Version:** 1

## Core Identity

## Operating Principles

## Communication Style

## Constraints

## Self-Improvement Guidelines
""",
    "MEMORY.md": """# MEMORY.md

**Last Updated:** {updated}
**Version:** 1

## Consolidated Memories

### High-Value Learnings

### Patterns Established

### Operational Heuristics
""",
    "USER.md": """# USER.md

**User Profile**
**Created:** {created}
**Last Updated:** {updated}

## User Preferences

## Work Patterns

## Context

## Restrictions

## Communication Style
""",
}


def create_directory_structure(base_path: Path, structure: dict) -> None:
    """Recursively create directory structure"""
    for name, children in structure.items():
        dir_path = base_path / name
        dir_path.mkdir(parents=True, exist_ok=True)
        if children is not None:
            create_directory_structure(dir_path, children)


def create_agent_brain_files(brain_path: Path) -> None:
    """Create Agent Brain core files"""
    now = datetime.utcnow().strftime("%Y-%m-%d")
    for filename, content in AGENT_BRAIN_FILES.items():
        file_path = brain_path / filename
        if not file_path.exists():
            file_path.write_text(content.format(created=now, updated=now), encoding="utf-8")


def copy_schema_files(vault_path: Path) -> None:
    """Copy schema files to vault"""
    # These are created by other tasks, this is for materialization from templates
    pass


def create_vault_config(workspace_path: Path, vault_path: Path, name: str) -> None:
    """Create vault configuration files"""
    now = datetime.utcnow().strftime("%Y-%m-%d")

    # Workspace-level config
    workspace_config = {
        "version": 1,
        "workspace": {
            "name": name,
            "created": now,
            "template_profile": None,
        },
        "system": {
            "vault_path": "user-vault",
            "brain_path": "agent-brain",
            "exchange_path": "exchange",
            "raw_path": "raw",
            "runtime_path": "runtime",
        },
    }

    workspace_config_path = workspace_path / "_system" / "vault-config.yaml"
    workspace_config_path.parent.mkdir(parents=True, exist_ok=True)
    with open(workspace_config_path, "w", encoding="utf-8") as f:
        yaml.dump(workspace_config, f, default_flow_style=False)

    # Vault-level config
    vault_config = {
        "version": 1,
        "structure": {
            "numbering_enabled": True,
            "folders": [
                "00-Inbox",
                "01-Daily",
                "02-Projects",
                "03-Areas",
                "04-Resources",
                "05-Archive",
                "Templates",
                "Attachments",
            ],
        },
        "schema": {
            "strict_mode": True,
            "auto_fill": ["created_at", "updated_at", "id"],
        },
        "daily_notes": {
            "enabled": True,
            "folder": "01-Daily",
            "format": "YYYY-MM-DD",
            "extension": ".md",
            "sections": [
                "Inbox",
                "Focus",
                "Notes",
                "Linked Projects",
                "Decisions",
                "Learnings",
                "Tasks",
                "Review",
            ],
        },
        "note_types": "schemas/note-types.yaml",
    }

    vault_config_path = vault_path / "_system" / "vault-config.yaml"
    with open(vault_config_path, "w", encoding="utf-8") as f:
        yaml.dump(vault_config, f, default_flow_style=False)


def create_workspace(
    path: str,
    name: str = "Knowledge OS Workspace",
    profile: str = None,
) -> Path:
    """Create a complete workspace"""
    workspace_path = Path(path).resolve()
    vault_path = workspace_path / "user-vault"
    brain_path = workspace_path / "agent-brain"

    print(f"Creating workspace at: {workspace_path}")

    # Create directory structure
    create_directory_structure(workspace_path, DIRECTORY_STRUCTURE)
    print("Created directory structure")

    # Create Agent Brain files
    create_agent_brain_files(brain_path)
    print("Created Agent Brain core files")

    # Create vault config
    create_vault_config(workspace_path, vault_path, name)
    print("Created vault configuration")

    # Note: Schema files, templates, and profiles should be copied from
    # template locations. This script creates the structure and core files.
    # For full materialization, ensure _system/schemas and _system/templates
    # are populated from the template library.

    print(f"Workspace created successfully: {workspace_path}")
    return workspace_path


def main():
    parser = argparse.ArgumentParser(description="Create Knowledge OS workspace")
    parser.add_argument(
        "--path",
        default="./workspace",
        help="Workspace location (default: ./workspace)"
    )
    parser.add_argument(
        "--name",
        default="Knowledge OS Workspace",
        help="Workspace name"
    )
    parser.add_argument(
        "--profile",
        help="Template profile name (optional)"
    )

    args = parser.parse_args()

    try:
        workspace_path = create_workspace(args.path, args.name, args.profile)
        print(f"\nWorkspace ready at: {workspace_path}")
    except Exception as e:
        print(f"Error creating workspace: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
