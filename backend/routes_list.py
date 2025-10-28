#!/usr/bin/env python3
"""
FastAPI Routes Lister - Similar to 'php artisan route:list'
Usage: python routes_list.py
"""

from fastapi import FastAPI
from fastapi.routing import APIRoute
from typing import List, Dict
import sys
import os

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from main import app


def get_routes_info() -> List[Dict[str, str]]:
    """Extract route information from FastAPI app."""
    routes_info = []

    for route in app.routes:
        if isinstance(route, APIRoute):
            routes_info.append({
                "method": ",".join(route.methods),
                "path": route.path,
                "name": route.name,
                "endpoint": route.endpoint.__name__ if route.endpoint else "N/A",
            })

    return routes_info


def print_routes_table(routes: List[Dict[str, str]]):
    """Print routes in a formatted table."""
    if not routes:
        print("No routes found.")
        return

    # Calculate column widths
    method_width = max(len(r["method"]) for r in routes) + 2
    path_width = max(len(r["path"]) for r in routes) + 2
    name_width = max(len(r["name"]) for r in routes) + 2
    endpoint_width = max(len(r["endpoint"]) for r in routes) + 2

    # Ensure minimum widths
    method_width = max(method_width, 10)
    path_width = max(path_width, 40)
    name_width = max(name_width, 20)
    endpoint_width = max(endpoint_width, 30)

    # Print header
    header = f"{'METHOD'.ljust(method_width)} | {'PATH'.ljust(path_width)} | {'NAME'.ljust(name_width)} | {'ENDPOINT'.ljust(endpoint_width)}"
    print(header)
    print("-" * len(header))

    # Print routes
    for route in routes:
        print(
            f"{route['method'].ljust(method_width)} | "
            f"{route['path'].ljust(path_width)} | "
            f"{route['name'].ljust(name_width)} | "
            f"{route['endpoint'].ljust(endpoint_width)}"
        )


def main():
    print(f"\n{'='*80}")
    print(f"FastAPI Routes List")
    print(f"{'='*80}\n")

    routes = get_routes_info()

    # Sort routes by path
    routes.sort(key=lambda x: x["path"])

    print_routes_table(routes)

    print(f"\nTotal routes: {len(routes)}\n")


if __name__ == "__main__":
    main()
