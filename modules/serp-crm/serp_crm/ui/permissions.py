"""
CRM Module Permissions
Defines all permission constants for the CRM module
"""

CRM_PERMISSIONS = {
    # Partner permissions
    "PARTNER_CREATE": "crm.partners.create",
    "PARTNER_READ": "crm.partners.read",
    "PARTNER_UPDATE": "crm.partners.update",
    "PARTNER_DELETE": "crm.partners.delete",
    "PARTNER_LIST": "crm.partners.list",
    # Contact permissions
    "CONTACT_CREATE": "crm.contacts.create",
    "CONTACT_READ": "crm.contacts.read",
    "CONTACT_UPDATE": "crm.contacts.update",
    "CONTACT_DELETE": "crm.contacts.delete",
    "CONTACT_LIST": "crm.contacts.list",
    # Lead permissions
    "LEAD_CREATE": "crm.leads.create",
    "LEAD_READ": "crm.leads.read",
    "LEAD_UPDATE": "crm.leads.update",
    "LEAD_DELETE": "crm.leads.delete",
    "LEAD_LIST": "crm.leads.list",
    # Opportunity permissions
    "OPPORTUNITY_CREATE": "crm.opportunities.create",
    "OPPORTUNITY_READ": "crm.opportunities.read",
    "OPPORTUNITY_UPDATE": "crm.opportunities.update",
    "OPPORTUNITY_DELETE": "crm.opportunities.delete",
    "OPPORTUNITY_LIST": "crm.opportunities.list",
}


def getAllCRMPermissions() -> list[str]:
    """
    Get all CRM permissions as a list.

    Returns:
        list[str]: All CRM permission strings
    """
    return list(CRM_PERMISSIONS.values())


__all__ = ["CRM_PERMISSIONS", "getAllCRMPermissions"]
