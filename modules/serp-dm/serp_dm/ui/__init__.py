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
        "moduleId": "dm",
        "moduleName": "Document Management",
        "version": "0.1.0",
        "icon": "FileText",
        "description": "Document management with version control and approvals",
        # HMR configuration for development hot reload
        "hmr": {
            "port": 5174,
        },
        "ribbon": {
            "tabId": "dm",
            "tabLabel": "Documents",
            "tabIcon": "FileText",
            "tabOrder": 20,
            "groups": [
                {
                    "groupId": "dm-new",
                    "groupLabel": "New",
                    "groupOrder": 1,
                    "buttons": [
                        {
                            "buttonId": "dm-new-document",
                            "label": "New Document",
                            "icon": "FilePlus",
                            "action": {
                                "type": "navigate",
                                "route": "/dm/documents/new",
                            },
                            "variant": "primary",
                            "buttonOrder": 1,
                            "tooltip": "Register a new document",
                        },
                        {
                            "buttonId": "dm-new-folder",
                            "label": "New Folder",
                            "icon": "FolderPlus",
                            "action": {
                                "type": "navigate",
                                "route": "/dm/folders/new",
                            },
                            "buttonOrder": 2,
                            "tooltip": "Create a new folder",
                        },
                    ],
                },
                {
                    "groupId": "dm-actions",
                    "groupLabel": "Actions",
                    "groupOrder": 2,
                    "buttons": [
                        {
                            "buttonId": "dm-upload",
                            "label": "Upload",
                            "icon": "Upload",
                            "action": {
                                "type": "navigate",
                                "route": "/dm/upload",
                            },
                            "buttonOrder": 1,
                            "tooltip": "Upload document files",
                        },
                        {
                            "buttonId": "dm-download",
                            "label": "Download",
                            "icon": "Download",
                            "action": {
                                "type": "trigger",
                                "event": "dm:download-selected",
                            },
                            "buttonOrder": 2,
                            "tooltip": "Download selected documents",
                        },
                    ],
                },
            ],
        },
        "routes": [
            {
                "path": "/dm/documents",
                "name": "Documents",
                "component": "DocumentsListView",
                "permission": "dm.document.list",
            },
            {
                "path": "/dm/documents/new",
                "name": "New Document",
                "component": "DocumentFormView",
                "permission": "dm.document.create",
            },
            {
                "path": "/dm/documents/:id",
                "name": "Document Detail",
                "component": "DocumentDetailView",
                "permission": "dm.document.read",
            },
            {
                "path": "/dm/folders",
                "name": "Folders",
                "component": "DocumentsListView",
                "permission": "dm.folder.list",
            },
            {
                "path": "/dm/folders/new",
                "name": "New Folder",
                "component": "DocumentFormView",
                "permission": "dm.folder.create",
            },
            {
                "path": "/dm/upload",
                "name": "Upload Document",
                "component": "DocumentFormView",
                "permission": "dm.document.create",
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
        "permissions": [
            "dm.document.list",
            "dm.document.read",
            "dm.document.create",
            "dm.document.update",
            "dm.document.delete",
            "dm.document.upload_version",
            "dm.document.download",
            "dm.document.move_stage",
            "dm.document.submit_approval",
            "dm.stage.list",
            "dm.stage.manage",
            "dm.folder.list",
            "dm.folder.read",
            "dm.folder.create",
            "dm.folder.update",
            "dm.folder.delete",
            "dm.template.list",
            "dm.template.manage",
            "dm.doctype.list",
            "dm.doctype.manage",
            "dm.approval.view",
            "dm.approval.decide",
            "dm.project.export",
            "dm.audit.view",
        ],
    }
