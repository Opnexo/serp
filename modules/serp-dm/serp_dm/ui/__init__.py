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
                    "groupId": "dm-documents",
                    "groupLabel": "Documents",
                    "groupOrder": 1,
                    "buttons": [
                        {
                            "buttonId": "dm-projects-list",
                            "label": "Projects",
                            "icon": "Files",
                            "action": {
                                "type": "navigate",
                                "route": "/dm/projects",
                            },
                            "buttonOrder": 1,
                            "tooltip": "View all projects",
                        },
                        {
                            "buttonId": "dm-documents-new",
                            "label": "Register",
                            "icon": "FilePlus",
                            "action": {
                                "type": "navigate",
                                "route": "/dm/documents/new",
                            },
                            "variant": "primary",
                            "buttonOrder": 2,
                            "tooltip": "Register a new document",
                        },
                        {
                            "buttonId": "dm-export",
                            "label": "Export",
                            "icon": "Download",
                            "action": {
                                "type": "navigate",
                                "route": "/dm/export",
                            },
                            "buttonOrder": 3,
                            "tooltip": "Export documents as ZIP",
                        },
                    ],
                },
                {
                    "groupId": "dm-kanban",
                    "groupLabel": "Workflow",
                    "groupOrder": 2,
                    "buttons": [
                        {
                            "buttonId": "dm-kanban",
                            "label": "Kanban",
                            "icon": "Columns",
                            "action": {
                                "type": "navigate",
                                "route": "/dm/kanban",
                            },
                            "buttonOrder": 1,
                            "tooltip": "View Kanban board",
                        },
                        {
                            "buttonId": "dm-stage-new",
                            "label": "New Stage",
                            "icon": "Plus",
                            "action": {
                                "type": "navigate",
                                "route": "/dm/kanban?action=new-stage",
                            },
                            "buttonOrder": 2,
                            "tooltip": "Create a new workflow stage",
                        },
                    ],
                },
                {
                    "groupId": "dm-admin",
                    "groupLabel": "Admin",
                    "groupOrder": 3,
                    "buttons": [
                        {
                            "buttonId": "dm-templates",
                            "label": "Templates",
                            "icon": "LayoutTemplate",
                            "permission": "dm.template.list",
                            "action": {
                                "type": "navigate",
                                "route": "/dm/admin/templates",
                            },
                            "buttonOrder": 1,
                            "tooltip": "Manage storage templates",
                        },
                        {
                            "buttonId": "dm-stage-templates",
                            "label": "Workflows",
                            "icon": "GitPullRequest",
                            "permission": "dm.template.list",
                            "action": {
                                "type": "navigate",
                                "route": "/dm/admin/stage-templates",
                            },
                            "buttonOrder": 2,
                            "tooltip": "Manage workflow templates",
                        },
                        {
                            "buttonId": "dm-doctypes",
                            "label": "Doc Types",
                            "icon": "Tag",
                            "permission": "dm.doctype.list",
                            "action": {
                                "type": "navigate",
                                "route": "/dm/admin/document-types",
                            },
                            "buttonOrder": 3,
                            "tooltip": "Manage document types",
                        },
                    ],
                },
            ],
        },
        "routes": [
            {
                "path": "/dm/projects",
                "name": "Projects",
                "component": "DMProjectsListView",
                "permission": "dm.document.list",
            },
            {
                "path": "/dm/projects/:projectId",
                "name": "Project Detail",
                "component": "DMProjectView",
                "permission": "dm.document.list",
            },
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
                "path": "/dm/kanban",
                "name": "Kanban Board",
                "component": "KanbanBoardView",
                "permission": "dm.stage.list",
            },
             {
                "path": "/dm/export",
                "name": "Export",
                "component": "ExportView",
                "permission": "dm.project.export",
            },
            {
                "path": "/dm/admin/templates",
                "name": "Storage Templates",
                "component": "TemplatesView",
                "permission": "dm.template.list",
            },
            {
                "path": "/dm/admin/stage-templates",
                "name": "Workflow Templates",
                "component": "StageTemplatesView",
                "permission": "dm.template.list",
            },
            {
                "path": "/dm/admin/document-types",
                "name": "Document Types",
                "component": "DocumentTypesView",
                "permission": "dm.doctype.list",
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
