"""
UI configuration for Document Management module.
"""

from typing import Any


def load_ui_config() -> dict[str, Any]:
    """
    Load UI configuration for the Document Management module.
    
    This function is called by serp-shell during module discovery.
    
    Returns:
        Dictionary containing UI configuration (toolbar, routes, etc.)
    """
    return {
        "module_id": "dm",
        "module_name": "Document Management",
        "toolbar": {
            "tabs": [
                {
                    "id": "documents",
                    "label": "Documents",
                    "icon": "FileText",
                    "groups": [
                        {
                            "id": "new",
                            "label": "New",
                            "buttons": [
                                {
                                    "id": "new_document",
                                    "label": "New Document",
                                    "icon": "FilePlus",
                                    "action": "dm.document.create",
                                    "permission": "dm.document.create",
                                },
                                {
                                    "id": "new_folder",
                                    "label": "New Folder",
                                    "icon": "FolderPlus",
                                    "action": "dm.folder.create",
                                    "permission": "dm.folder.create",
                                },
                            ],
                        },
                        {
                            "id": "actions",
                            "label": "Actions",
                            "buttons": [
                                {
                                    "id": "upload",
                                    "label": "Upload",
                                    "icon": "Upload",
                                    "action": "dm.document.upload",
                                    "permission": "dm.document.create",
                                },
                                {
                                    "id": "download",
                                    "label": "Download",
                                    "icon": "Download",
                                    "action": "dm.document.download",
                                    "permission": "dm.document.download",
                                },
                            ],
                        },
                    ],
                }
            ],
        },
        "routes": [
            {
                "path": "/dm/documents",
                "name": "Documents",
                "component": "DocumentList",
                "permission": "dm.document.list",
            },
            {
                "path": "/dm/documents/:id",
                "name": "Document Detail",
                "component": "DocumentDetail",
                "permission": "dm.document.read",
            },
            {
                "path": "/dm/folders",
                "name": "Folders",
                "component": "FolderList",
                "permission": "dm.folder.list",
            },
        ],
        "navigation": [
            {
                "label": "Documents",
                "icon": "FileText",
                "path": "/dm/documents",
                "permission": "dm.document.list",
            },
        ],
    }
