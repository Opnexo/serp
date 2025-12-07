"""
CRM Module UI Configuration
Entry point for UI plugin system
"""

from serp_crm.ui.permissions import CRM_PERMISSIONS, getAllCRMPermissions


def load_ui_config() -> dict:
    """
    Entry point for UI configuration.

    This function is called by the SERP plugin system to discover
    and load the module's UI configuration (toolbar, routes, permissions).

    Returns:
        dict: UI configuration with toolbar tabs, groups, buttons, and routes
    """
    return {
        "moduleId": "crm",
        "moduleName": "CRM",
        "version": "0.1.0",
        "icon": "Users",
        "description": "Customer Relationship Management",
        "ribbon": {
            "tabId": "crm",
            "tabLabel": "CRM",
            "tabIcon": "Users",
            "tabOrder": 10,
            "groups": [
                {
                    "groupId": "crm-partners",
                    "groupLabel": "Partners",
                    "groupOrder": 1,
                    "buttons": [
                        {
                            "buttonId": "crm-partners-list",
                            "label": "Partners",
                            "icon": "Building2",
                            "permission": CRM_PERMISSIONS["PARTNER_LIST"],
                            "action": {
                                "type": "navigate",
                                "route": "/crm/partners",
                            },
                            "buttonOrder": 1,
                            "tooltip": "View all partners",
                        },
                        {
                            "buttonId": "crm-partners-new",
                            "label": "New Partner",
                            "icon": "Plus",
                            "permission": CRM_PERMISSIONS["PARTNER_CREATE"],
                            "action": {
                                "type": "navigate",
                                "route": "/crm/partners/new",
                            },
                            "variant": "primary",
                            "buttonOrder": 2,
                            "tooltip": "Create a new partner",
                        },
                        {
                            "buttonId": "crm-contacts-list",
                            "label": "Contacts",
                            "icon": "Contact",
                            "permission": CRM_PERMISSIONS["CONTACT_LIST"],
                            "action": {
                                "type": "navigate",
                                "route": "/crm/contacts",
                            },
                            "buttonOrder": 3,
                            "tooltip": "View all contacts",
                        },
                    ],
                },
                {
                    "groupId": "crm-sales",
                    "groupLabel": "Sales",
                    "groupOrder": 2,
                    "buttons": [
                        {
                            "buttonId": "crm-leads-list",
                            "label": "Leads",
                            "icon": "UserPlus",
                            "permission": CRM_PERMISSIONS["LEAD_LIST"],
                            "action": {
                                "type": "navigate",
                                "route": "/crm/leads",
                            },
                            "buttonOrder": 1,
                            "tooltip": "View all leads",
                        },
                        {
                            "buttonId": "crm-opportunities-list",
                            "label": "Opportunities",
                            "icon": "Target",
                            "permission": CRM_PERMISSIONS["OPPORTUNITY_LIST"],
                            "action": {
                                "type": "navigate",
                                "route": "/crm/opportunities",
                            },
                            "buttonOrder": 2,
                            "tooltip": "View all opportunities",
                        },
                    ],
                },
            ],
        },
        "routes": [
            # Partners
            {
                "routeId": "crm-partners",
                "path": "/crm/partners",
                "permission": CRM_PERMISSIONS["PARTNER_LIST"],
                "component": "PartnersListView",
            },
            {
                "routeId": "crm-partners-detail",
                "path": "/crm/partners/:id",
                "permission": CRM_PERMISSIONS["PARTNER_READ"],
                "component": "PartnerDetailView",
            },
            {
                "routeId": "crm-partners-edit",
                "path": "/crm/partners/:id/edit",
                "permission": CRM_PERMISSIONS["PARTNER_UPDATE"],
                "component": "PartnerEditView",
            },
            # Contacts
            {
                "routeId": "crm-contacts",
                "path": "/crm/contacts",
                "permission": CRM_PERMISSIONS["CONTACT_LIST"],
                "component": "ContactsListView",
            },
            # Leads
            {
                "routeId": "crm-leads",
                "path": "/crm/leads",
                "permission": CRM_PERMISSIONS["LEAD_LIST"],
                "component": "LeadsListView",
            },
            # Opportunities
            {
                "routeId": "crm-opportunities",
                "path": "/crm/opportunities",
                "permission": CRM_PERMISSIONS["OPPORTUNITY_LIST"],
                "component": "OpportunitiesListView",
            },
        ],
        "permissions": getAllCRMPermissions(),
    }


__all__ = ["load_ui_config"]
