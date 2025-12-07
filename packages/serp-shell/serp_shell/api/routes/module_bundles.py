"""
Module Bundle API routes

Serves compiled JavaScript bundles for module UIs.
Each module builds its UI components into a bundle that can be
dynamically loaded by the shell at runtime.
"""

import importlib.metadata
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse, JSONResponse

router = APIRouter()


def find_module_bundle_path(module_id: str) -> Optional[Path]:
    """
    Find the path to a module's UI bundle.

    Looks for the bundle in the module's package directory.
    The bundle should be at: {module_package}/ui/dist/crm-module.iife.js

    Args:
        module_id: The module identifier (e.g., 'crm', 'invoicing')

    Returns:
        Path to the bundle file, or None if not found
    """
    # Map module_id to package name
    package_name = f"serp_{module_id}"

    try:
        # Get the package location
        dist = importlib.metadata.distribution(f"serp-{module_id}")
        package_files = dist.files

        if package_files:
            # Find the package root
            for file in package_files:
                if file.name == "__init__.py" and package_name in str(file):
                    package_root = Path(file.locate()).parent
                    bundle_path = package_root / "ui" / "dist" / f"{module_id}-module.iife.js"
                    if bundle_path.exists():
                        return bundle_path
                    break

    except importlib.metadata.PackageNotFoundError:
        pass

    # Fallback: try common development paths
    dev_paths = [
        # Installed in development mode
        Path(__file__).parent.parent.parent.parent.parent.parent
        / "modules"
        / f"serp-{module_id}"
        / package_name
        / "ui"
        / "dist"
        / f"{module_id}-module.iife.js",
        # Direct path for development
        Path(__file__).parent.parent.parent.parent.parent.parent
        / "modules"
        / f"serp-{module_id}"
        / package_name
        / "ui"
        / "dist"
        / f"{module_id}-module.iife.js",
    ]

    for path in dev_paths:
        if path.exists():
            return path

    return None


@router.get("/modules/{module_id}/bundle.js")
async def get_module_bundle(module_id: str):
    """
    Get the JavaScript bundle for a module's UI.

    This endpoint serves the compiled JavaScript that contains
    all React components for the specified module.

    Args:
        module_id: Module identifier (e.g., 'crm')

    Returns:
        JavaScript file containing the module's UI components
    """
    bundle_path = find_module_bundle_path(module_id)

    if bundle_path is None:
        raise HTTPException(
            status_code=404,
            detail=f"Bundle not found for module '{module_id}'. "
            f"Make sure the module UI has been built.",
        )

    return FileResponse(
        path=bundle_path,
        media_type="application/javascript",
        headers={
            "Cache-Control": "no-cache",  # Don't cache during development
            "Access-Control-Allow-Origin": "*",
        },
    )


@router.get("/modules/{module_id}/bundle.js.map")
async def get_module_bundle_sourcemap(module_id: str):
    """
    Get the sourcemap for a module's UI bundle.

    Returns:
        Sourcemap file for debugging
    """
    bundle_path = find_module_bundle_path(module_id)

    if bundle_path is None:
        raise HTTPException(
            status_code=404,
            detail=f"Bundle not found for module '{module_id}'",
        )

    sourcemap_path = bundle_path.with_suffix(".js.map")

    if not sourcemap_path.exists():
        raise HTTPException(
            status_code=404,
            detail=f"Sourcemap not found for module '{module_id}'",
        )

    return FileResponse(
        path=sourcemap_path,
        media_type="application/json",
        headers={
            "Cache-Control": "no-cache",
            "Access-Control-Allow-Origin": "*",
        },
    )


@router.get("/modules/available")
async def list_available_modules():
    """
    List all modules that have UI bundles available.

    Returns:
        List of module IDs with available bundles
    """
    available = []

    # Check known modules
    known_modules = ["crm", "users", "invoicing"]

    for module_id in known_modules:
        bundle_path = find_module_bundle_path(module_id)
        if bundle_path:
            available.append(
                {
                    "moduleId": module_id,
                    "bundleUrl": f"/api/modules/{module_id}/bundle.js",
                    "hasBundle": True,
                }
            )

    return JSONResponse(content={"modules": available})
