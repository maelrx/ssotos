#!/usr/bin/env python3
"""Apply a patch bundle from CLI.

Usage:
    python apply-patch.py --bundle /path/to/bundle [--dry-run]
"""
import argparse
import sys
from pathlib import Path

# Navigate from workspace/_system/scripts/ to project root
# 3 levels up gets us to project root, then add src
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "src"))

from services.git_service import GitService
from services.patch_service import PatchService


def main():
    parser = argparse.ArgumentParser(description="Apply a patch bundle")
    parser.add_argument("--bundle", required=True, help="Path to patch bundle directory")
    parser.add_argument("--dry-run", action="store_true", help="Validate without applying")

    args = parser.parse_args()

    git = GitService(Path("workspace/user-vault"))
    patch = PatchService(git)

    result = patch.apply_patch_bundle(Path(args.bundle), dry_run=args.dry_run)

    if result.success:
        print(f"Patch applied successfully")
        if result.commit_sha:
            print(f"Commit: {result.commit_sha}")
        if result.files_changed:
            print(f"Files changed: {result.files_changed}")
    else:
        print(f"Patch failed: {result.error}")
        sys.exit(1)


if __name__ == "__main__":
    main()
