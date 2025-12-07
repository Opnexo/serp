"""In-memory repository implementations for Procurement."""

from serp_procurement.domain.entities import (
    RFQ,
    GoodsReceiptNote,
    PurchaseAgreement,
    PurchaseOrder,
)
from serp_procurement.domain.repositories import (
    IGoodsReceiptNoteRepository,
    IPurchaseAgreementRepository,
    IPurchaseOrderRepository,
    IRFQRepository,
)
from serp_procurement.domain.value_objects import PurchaseOrderState, RFQState


class InMemoryRFQRepository(IRFQRepository):
    """In-memory implementation of RFQRepository."""

    def __init__(self):
        self._storage: dict[str, RFQ] = {}

    def add(self, entity: RFQ) -> None:
        """Add a new RFQ."""
        self._storage[entity.id] = entity

    def get_by_id(self, entity_id: str) -> RFQ | None:
        """Get RFQ by ID."""
        return self._storage.get(entity_id)

    def update(self, entity: RFQ) -> None:
        """Update an existing RFQ."""
        if entity.id in self._storage:
            self._storage[entity.id] = entity

    def remove(self, entity_id: str) -> None:
        """Remove an RFQ."""
        self._storage.pop(entity_id, None)

    def list_all(self) -> list[RFQ]:
        """List all RFQs."""
        return list(self._storage.values())

    def get_by_number(self, rfq_number: str) -> RFQ | None:
        """Get RFQ by number."""
        for rfq in self._storage.values():
            if rfq.rfq_number.value == rfq_number:
                return rfq
        return None

    def list_by_state(self, state: RFQState) -> list[RFQ]:
        """List RFQs by state."""
        return [rfq for rfq in self._storage.values() if rfq.state == state]

    def list_by_supplier(self, supplier_id: str) -> list[RFQ]:
        """List RFQs for a supplier."""
        return [
            rfq for rfq in self._storage.values() if supplier_id in rfq.supplier_ids
        ]


class InMemoryPurchaseOrderRepository(IPurchaseOrderRepository):
    """In-memory implementation of PurchaseOrderRepository."""

    def __init__(self):
        self._storage: dict[str, PurchaseOrder] = {}

    def add(self, entity: PurchaseOrder) -> None:
        """Add a new PurchaseOrder."""
        self._storage[entity.id] = entity

    def get_by_id(self, entity_id: str) -> PurchaseOrder | None:
        """Get PurchaseOrder by ID."""
        return self._storage.get(entity_id)

    def update(self, entity: PurchaseOrder) -> None:
        """Update an existing PurchaseOrder."""
        if entity.id in self._storage:
            self._storage[entity.id] = entity

    def remove(self, entity_id: str) -> None:
        """Remove a PurchaseOrder."""
        self._storage.pop(entity_id, None)

    def list_all(self) -> list[PurchaseOrder]:
        """List all PurchaseOrders."""
        return list(self._storage.values())

    def get_by_number(self, po_number: str) -> PurchaseOrder | None:
        """Get PurchaseOrder by number."""
        for po in self._storage.values():
            if po.po_number.value == po_number:
                return po
        return None

    def list_by_supplier(self, supplier_id: str) -> list[PurchaseOrder]:
        """List PurchaseOrders for a supplier."""
        return [po for po in self._storage.values() if po.supplier_id == supplier_id]

    def list_by_state(self, state: PurchaseOrderState) -> list[PurchaseOrder]:
        """List PurchaseOrders by state."""
        return [po for po in self._storage.values() if po.state == state]

    def get_by_rfq(self, rfq_id: str) -> PurchaseOrder | None:
        """Get PurchaseOrder created from RFQ."""
        for po in self._storage.values():
            if po.rfq_id == rfq_id:
                return po
        return None


class InMemoryGoodsReceiptNoteRepository(IGoodsReceiptNoteRepository):
    """In-memory implementation of GoodsReceiptNoteRepository."""

    def __init__(self):
        self._storage: dict[str, GoodsReceiptNote] = {}

    def add(self, entity: GoodsReceiptNote) -> None:
        """Add a new GoodsReceiptNote."""
        self._storage[entity.id] = entity

    def get_by_id(self, entity_id: str) -> GoodsReceiptNote | None:
        """Get GoodsReceiptNote by ID."""
        return self._storage.get(entity_id)

    def update(self, entity: GoodsReceiptNote) -> None:
        """Update an existing GoodsReceiptNote."""
        if entity.id in self._storage:
            self._storage[entity.id] = entity

    def remove(self, entity_id: str) -> None:
        """Remove a GoodsReceiptNote."""
        self._storage.pop(entity_id, None)

    def list_all(self) -> list[GoodsReceiptNote]:
        """List all GoodsReceiptNotes."""
        return list(self._storage.values())

    def get_by_number(self, grn_number: str) -> GoodsReceiptNote | None:
        """Get GoodsReceiptNote by number."""
        for grn in self._storage.values():
            if grn.grn_number.value == grn_number:
                return grn
        return None

    def list_by_purchase_order(self, purchase_order_id: str) -> list[GoodsReceiptNote]:
        """List GoodsReceiptNotes for a purchase order."""
        return [
            grn
            for grn in self._storage.values()
            if grn.purchase_order_id == purchase_order_id
        ]


class InMemoryPurchaseAgreementRepository(IPurchaseAgreementRepository):
    """In-memory implementation of PurchaseAgreementRepository."""

    def __init__(self):
        self._storage: dict[str, PurchaseAgreement] = {}

    def add(self, entity: PurchaseAgreement) -> None:
        """Add a new PurchaseAgreement."""
        self._storage[entity.id] = entity

    def get_by_id(self, entity_id: str) -> PurchaseAgreement | None:
        """Get PurchaseAgreement by ID."""
        return self._storage.get(entity_id)

    def update(self, entity: PurchaseAgreement) -> None:
        """Update an existing PurchaseAgreement."""
        if entity.id in self._storage:
            self._storage[entity.id] = entity

    def remove(self, entity_id: str) -> None:
        """Remove a PurchaseAgreement."""
        self._storage.pop(entity_id, None)

    def list_all(self) -> list[PurchaseAgreement]:
        """List all PurchaseAgreements."""
        return list(self._storage.values())

    def get_by_number(self, agreement_number: str) -> PurchaseAgreement | None:
        """Get PurchaseAgreement by number."""
        for agr in self._storage.values():
            if agr.agreement_number == agreement_number:
                return agr
        return None

    def list_by_supplier(self, supplier_id: str) -> list[PurchaseAgreement]:
        """List PurchaseAgreements for a supplier."""
        return [agr for agr in self._storage.values() if agr.supplier_id == supplier_id]

    def list_active(self) -> list[PurchaseAgreement]:
        """List active PurchaseAgreements."""
        return [agr for agr in self._storage.values() if agr.is_active]
