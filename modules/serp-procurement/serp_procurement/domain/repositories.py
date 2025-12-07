"""Repository interfaces for Procurement domain."""

from typing import Protocol

from serp_procurement.domain.entities import (
    RFQ,
    GoodsReceiptNote,
    PurchaseAgreement,
    PurchaseOrder,
)
from serp_procurement.domain.value_objects import PurchaseOrderState, RFQState


class IRFQRepository(Protocol):
    """Repository for RFQ aggregate."""

    def add(self, entity: RFQ) -> None:
        """Add a new RFQ."""
        ...

    def get_by_id(self, entity_id: str) -> RFQ | None:
        """Get RFQ by ID."""
        ...

    def update(self, entity: RFQ) -> None:
        """Update an existing RFQ."""
        ...

    def remove(self, entity_id: str) -> None:
        """Remove an RFQ."""
        ...

    def list_all(self) -> list[RFQ]:
        """List all RFQs."""
        ...

    def get_by_number(self, rfq_number: str) -> RFQ | None:
        """Get RFQ by number."""
        ...

    def list_by_state(self, state: RFQState) -> list[RFQ]:
        """List RFQs by state."""
        ...

    def list_by_supplier(self, supplier_id: str) -> list[RFQ]:
        """List RFQs for a supplier."""
        ...


class IPurchaseOrderRepository(Protocol):
    """Repository for PurchaseOrder aggregate."""

    def add(self, entity: PurchaseOrder) -> None:
        """Add a new PurchaseOrder."""
        ...

    def get_by_id(self, entity_id: str) -> PurchaseOrder | None:
        """Get PurchaseOrder by ID."""
        ...

    def update(self, entity: PurchaseOrder) -> None:
        """Update an existing PurchaseOrder."""
        ...

    def remove(self, entity_id: str) -> None:
        """Remove a PurchaseOrder."""
        ...

    def list_all(self) -> list[PurchaseOrder]:
        """List all PurchaseOrders."""
        ...

    def get_by_number(self, po_number: str) -> PurchaseOrder | None:
        """Get PurchaseOrder by number."""
        ...

    def list_by_supplier(self, supplier_id: str) -> list[PurchaseOrder]:
        """List PurchaseOrders for a supplier."""
        ...

    def list_by_state(self, state: PurchaseOrderState) -> list[PurchaseOrder]:
        """List PurchaseOrders by state."""
        ...

    def get_by_rfq(self, rfq_id: str) -> PurchaseOrder | None:
        """Get PurchaseOrder created from RFQ."""
        ...


class IGoodsReceiptNoteRepository(Protocol):
    """Repository for GoodsReceiptNote aggregate."""

    def add(self, entity: GoodsReceiptNote) -> None:
        """Add a new GoodsReceiptNote."""
        ...

    def get_by_id(self, entity_id: str) -> GoodsReceiptNote | None:
        """Get GoodsReceiptNote by ID."""
        ...

    def update(self, entity: GoodsReceiptNote) -> None:
        """Update an existing GoodsReceiptNote."""
        ...

    def remove(self, entity_id: str) -> None:
        """Remove a GoodsReceiptNote."""
        ...

    def list_all(self) -> list[GoodsReceiptNote]:
        """List all GoodsReceiptNotes."""
        ...

    def get_by_number(self, grn_number: str) -> GoodsReceiptNote | None:
        """Get GoodsReceiptNote by number."""
        ...

    def list_by_purchase_order(self, purchase_order_id: str) -> list[GoodsReceiptNote]:
        """List GoodsReceiptNotes for a purchase order."""
        ...


class IPurchaseAgreementRepository(Protocol):
    """Repository for PurchaseAgreement aggregate."""

    def add(self, entity: PurchaseAgreement) -> None:
        """Add a new PurchaseAgreement."""
        ...

    def get_by_id(self, entity_id: str) -> PurchaseAgreement | None:
        """Get PurchaseAgreement by ID."""
        ...

    def update(self, entity: PurchaseAgreement) -> None:
        """Update an existing PurchaseAgreement."""
        ...

    def remove(self, entity_id: str) -> None:
        """Remove a PurchaseAgreement."""
        ...

    def list_all(self) -> list[PurchaseAgreement]:
        """List all PurchaseAgreements."""
        ...

    def get_by_number(self, agreement_number: str) -> PurchaseAgreement | None:
        """Get PurchaseAgreement by number."""
        ...

    def list_by_supplier(self, supplier_id: str) -> list[PurchaseAgreement]:
        """List PurchaseAgreements for a supplier."""
        ...

    def list_active(self) -> list[PurchaseAgreement]:
        """List active PurchaseAgreements."""
        ...
