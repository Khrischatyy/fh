#!/usr/bin/env python3
"""
FastAPI Routes Lister - Similar to 'php artisan route:list'
"""
import sys
import os

# Ensure we can import from src
sys.path.insert(0, "/app")

from fastapi.routing import APIRoute
from typing import List, Dict


def get_app():
    """Dynamically import the app to avoid initialization issues."""
    # Temporarily disable logging config
    import logging.config
    original_file_config = logging.config.fileConfig
    logging.config.fileConfig = lambda *args, **kwargs: None

    try:
        from src.main import app
        return app
    finally:
        logging.config.fileConfig = original_file_config


def get_routes_info(app) -> List[Dict[str, str]]:
    """Extract route information from FastAPI app."""
    routes_info = []

    for route in app.routes:
        if isinstance(route, APIRoute):
            # Get tags
            tags = ", ".join(route.tags) if route.tags else ""

            # Get methods, exclude HEAD and OPTIONS for cleaner output
            methods = [m for m in route.methods if m not in ["HEAD", "OPTIONS"]]
            method_str = ", ".join(sorted(methods))

            routes_info.append({
                "method": method_str,
                "path": route.path,
                "name": route.name or "",
                "tags": tags,
            })

    return routes_info


def print_routes_table(routes: List[Dict[str, str]]):
    """Print routes in a formatted table."""
    if not routes:
        print("No routes found.")
        return

    # Calculate column widths
    method_width = max((len(r["method"]) for r in routes), default=6)
    path_width = max((len(r["path"]) for r in routes), default=4)
    name_width = max((len(r["name"]) for r in routes), default=4)
    tags_width = max((len(r["tags"]) for r in routes), default=4)

    # Ensure minimum widths
    method_width = max(method_width, 10)
    path_width = max(path_width, 50)
    name_width = max(name_width, 30)
    tags_width = max(tags_width, 20)

    # Print header
    separator = "+" + "-" * (method_width + 2) + "+" + "-" * (path_width + 2) + "+" + "-" * (name_width + 2) + "+" + "-" * (tags_width + 2) + "+"

    print(separator)
    print(
        f"| {'METHOD'.ljust(method_width)} | "
        f"{'PATH'.ljust(path_width)} | "
        f"{'NAME'.ljust(name_width)} | "
        f"{'TAGS'.ljust(tags_width)} |"
    )
    print(separator)

    # Print routes
    for route in routes:
        print(
            f"| {route['method'].ljust(method_width)} | "
            f"{route['path'].ljust(path_width)} | "
            f"{route['name'].ljust(name_width)} | "
            f"{route['tags'].ljust(tags_width)} |"
        )

    print(separator)


def main():
    print(f"\n{'='*140}")
    print(f"FastAPI Routes List (similar to 'php artisan route:list')")
    print(f"{'='*140}\n")

    try:
        app = get_app()
        routes = get_routes_info(app)

        # Sort routes by path, then by method
        routes.sort(key=lambda x: (x["path"], x["method"]))

        print_routes_table(routes)

        print(f"\n Total routes: {len(routes)}\n")
    except Exception as e:
        print(f"Error loading routes: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()