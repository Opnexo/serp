"""Permissions for logistics module."""

from serp_users.domain import Permission

# Picking permissions
PICKING_CREATE = Permission("logistics.picking.create", "Create picking operations")
PICKING_VIEW = Permission("logistics.picking.view", "View picking operations")
PICKING_ASSIGN = Permission("logistics.picking.assign", "Assign pickers")
PICKING_EXECUTE = Permission("logistics.picking.execute", "Execute picking")
PICKING_COMPLETE = Permission(
    "logistics.picking.complete", "Complete picking operations"
)
PICKING_CANCEL = Permission("logistics.picking.cancel", "Cancel picking operations")

# Packing permissions
PACKING_CREATE = Permission("logistics.packing.create", "Create packing operations")
PACKING_VIEW = Permission("logistics.packing.view", "View packing operations")
PACKING_EXECUTE = Permission("logistics.packing.execute", "Execute packing")
PACKING_COMPLETE = Permission(
    "logistics.packing.complete", "Complete packing operations"
)

# Shipment permissions
SHIPMENT_CREATE = Permission("logistics.shipment.create", "Create shipments")
SHIPMENT_VIEW = Permission("logistics.shipment.view", "View shipments")
SHIPMENT_CONFIRM = Permission(
    "logistics.shipment.confirm", "Confirm shipments with tracking"
)
SHIPMENT_UPDATE = Permission("logistics.shipment.update", "Update shipment status")
SHIPMENT_CANCEL = Permission("logistics.shipment.cancel", "Cancel shipments")

# Carrier permissions
CARRIER_CREATE = Permission("logistics.carrier.create", "Create carriers")
CARRIER_VIEW = Permission("logistics.carrier.view", "View carriers")
CARRIER_UPDATE = Permission("logistics.carrier.update", "Update carriers")

# Route permissions
ROUTE_CREATE = Permission("logistics.route.create", "Create delivery routes")
ROUTE_VIEW = Permission("logistics.route.view", "View delivery routes")
ROUTE_UPDATE = Permission("logistics.route.update", "Update delivery routes")
ROUTE_EXECUTE = Permission("logistics.route.execute", "Execute delivery routes")

# RMA permissions
RMA_CREATE = Permission("logistics.rma.create", "Create return authorizations")
RMA_VIEW = Permission("logistics.rma.view", "View return authorizations")
RMA_APPROVE = Permission("logistics.rma.approve", "Approve return authorizations")
RMA_REJECT = Permission("logistics.rma.reject", "Reject return authorizations")
RMA_PROCESS = Permission("logistics.rma.process", "Process returns")


# Permission groups by role
WAREHOUSE_OPERATOR_PERMISSIONS = [
    PICKING_VIEW,
    PICKING_EXECUTE,
    PACKING_VIEW,
    PACKING_EXECUTE,
]

WAREHOUSE_MANAGER_PERMISSIONS = [
    *WAREHOUSE_OPERATOR_PERMISSIONS,
    PICKING_CREATE,
    PICKING_ASSIGN,
    PICKING_COMPLETE,
    PICKING_CANCEL,
    PACKING_CREATE,
    PACKING_COMPLETE,
    SHIPMENT_VIEW,
]

SHIPPING_COORDINATOR_PERMISSIONS = [
    SHIPMENT_CREATE,
    SHIPMENT_VIEW,
    SHIPMENT_CONFIRM,
    SHIPMENT_UPDATE,
    CARRIER_VIEW,
    ROUTE_VIEW,
]

CARRIER_DISPATCHER_PERMISSIONS = [
    SHIPMENT_VIEW,
    ROUTE_CREATE,
    ROUTE_VIEW,
    ROUTE_UPDATE,
    ROUTE_EXECUTE,
]

CUSTOMER_SERVICE_PERMISSIONS = [
    RMA_CREATE,
    RMA_VIEW,
    RMA_APPROVE,
    RMA_REJECT,
    RMA_PROCESS,
    SHIPMENT_VIEW,
]

LOGISTICS_ADMIN_PERMISSIONS = [
    *WAREHOUSE_MANAGER_PERMISSIONS,
    *SHIPPING_COORDINATOR_PERMISSIONS,
    *CARRIER_DISPATCHER_PERMISSIONS,
    *CUSTOMER_SERVICE_PERMISSIONS,
    SHIPMENT_CANCEL,
    CARRIER_CREATE,
    CARRIER_UPDATE,
]


__all__ = [
    # Picking permissions
    "PICKING_CREATE",
    "PICKING_VIEW",
    "PICKING_ASSIGN",
    "PICKING_EXECUTE",
    "PICKING_COMPLETE",
    "PICKING_CANCEL",
    # Packing permissions
    "PACKING_CREATE",
    "PACKING_VIEW",
    "PACKING_EXECUTE",
    "PACKING_COMPLETE",
    # Shipment permissions
    "SHIPMENT_CREATE",
    "SHIPMENT_VIEW",
    "SHIPMENT_CONFIRM",
    "SHIPMENT_UPDATE",
    "SHIPMENT_CANCEL",
    # Carrier permissions
    "CARRIER_CREATE",
    "CARRIER_VIEW",
    "CARRIER_UPDATE",
    # Route permissions
    "ROUTE_CREATE",
    "ROUTE_VIEW",
    "ROUTE_UPDATE",
    "ROUTE_EXECUTE",
    # RMA permissions
    "RMA_CREATE",
    "RMA_VIEW",
    "RMA_APPROVE",
    "RMA_REJECT",
    "RMA_PROCESS",
    # Permission groups
    "WAREHOUSE_OPERATOR_PERMISSIONS",
    "WAREHOUSE_MANAGER_PERMISSIONS",
    "SHIPPING_COORDINATOR_PERMISSIONS",
    "CARRIER_DISPATCHER_PERMISSIONS",
    "CUSTOMER_SERVICE_PERMISSIONS",
    "LOGISTICS_ADMIN_PERMISSIONS",
]
