"""Command line interface for the security_md package."""

import argparse

from security_md import Security


def main() -> None:
    """Validate a SECURITY.md file."""
    parser = argparse.ArgumentParser(description="Validate a SECURITY.md file")
    parser.add_argument("--verbose", "-v", type=int, default=0, help="The verbosity level")
    parser.add_argument("file", default="SECURITY.md", nargs="?", help="The SECURITY.md file to validate")
    args = parser.parse_args()

    with open(args.file, encoding="utf-8") as security_file:
        security = Security(security_file.read(), check=False)
        security.check(verbose=args.verbose)
        for version in security.branches():
            print(f"Version: {version}, Published tags: {', '.join(security.all_tags(version))}")


if __name__ == "__main__":
    main()
