"""Test that frontend API calls match backend route trailing slashes."""

import os
import re
import glob

import pytest


def get_backend_routes():
    """Extract all backend route paths (without prefix) from router files."""
    routes = []
    router_dir = os.path.join(os.path.dirname(__file__), "..", "app", "routers")

    # Pattern: @router.get("/path"), @router.post("/path"), etc.
    method_pattern = re.compile(
        r'@router\.(get|post|put|patch|delete)\(\s*"([^"]*)"'
    )

    for filepath in sorted(glob.glob(os.path.join(router_dir, "*.py"))):
        with open(filepath) as f:
            content = f.read()

        # Find router prefix
        prefix_match = re.search(
            r'router\s*=\s*APIRouter\(prefix\s*=\s*"([^"]*)"', content
        )
        prefix = prefix_match.group(1) if prefix_match else ""

        for match in method_pattern.finditer(content):
            method = match.group(1).upper()
            path = match.group(2)
            full_path = f"/api{prefix}{path}"
            # Normalize: collapse double slashes, strip trailing except root
            full_path = re.sub(r"/+", "/", full_path)
            routes.append({"method": method, "path": full_path})

    return routes


def get_frontend_api_calls():
    """Extract API URLs from frontend source files."""
    src_dir = os.path.join(os.path.dirname(__file__), "..", "..", "src")
    calls = []

    # Match patterns like `${apiUrl}/api/...` or `${API_URL}/agents/...`
    # We normalize API_URL to /api since that's its value
    url_pattern = re.compile(
        r'`(\$\{(?:apiUrl|API_URL)\})(/api/[^`]*)`'
    )

    for filepath in sorted(
        glob.glob(os.path.join(src_dir, "**", "*.vue"), recursive=True)
        + glob.glob(os.path.join(src_dir, "**", "*.ts"), recursive=True)
        + glob.glob(os.path.join(src_dir, "**", "*.js"), recursive=True)
    ):
        with open(filepath) as f:
            content = f.read()

        rel_path = os.path.relpath(filepath, src_dir)
        for match in url_pattern.finditer(content):
            url_template = match.group(2)
            # Replace dynamic parts with placeholders for matching
            normalized = re.sub(r"\$\{[^}]+\}", "{param}", url_template)
            # Remove query strings for path matching
            normalized = normalized.split("?")[0]
            calls.append({
                "file": rel_path,
                "template": normalized,
                "raw": url_template,
            })

    return calls


def test_no_trailing_slash_mismatches():
    """Frontend API calls must match backend route trailing slash patterns."""
    backend_routes = get_backend_routes()
    frontend_calls = get_frontend_api_calls()

    # Build a lookup: normalized path -> expected trailing slash
    # A route ending with / expects trailing slash
    # A route NOT ending with / (and not just /api) expects no trailing slash
    route_lookup = {}
    for r in backend_routes:
        path = r["path"]
        has_trailing = path.endswith("/")
        key = re.sub(r"\{[^}]+\}", "{param}", path)
        route_lookup[key] = has_trailing

    mismatches = []
    for call in frontend_calls:
        template = call["template"]
        frontend_has_trailing = template.endswith("/")

        # Find best matching backend route
        for route_key, backend_has_trailing in route_lookup.items():
            # Simple pattern match: replace {param} with regex
            pattern = re.sub(r"\{param\}", r"[^/?]+", re.escape(route_key))
            if re.fullmatch(pattern, template):
                if frontend_has_trailing != backend_has_trailing:
                    mismatches.append({
                        "file": call["file"],
                        "frontend_call": template,
                        "backend_route": route_key,
                        "frontend_has_trailing": frontend_has_trailing,
                        "backend_has_trailing": backend_has_trailing,
                    })
                break

    if mismatches:
        msg = "Trailing-slash mismatches found:\n"
        for m in mismatches:
            msg += (
                f"  {m['file']}: {m['frontend_call']} "
                f"({'with' if m['frontend_has_trailing'] else 'without'} trailing) "
                f"vs backend {m['backend_route']} "
                f"({'with' if m['backend_has_trailing'] else 'without'} trailing)\n"
            )
        pytest.fail(msg)
