"""Application services for Procurement module."""

from serp_core.application.events import EventBus
from serp_crm.domain import Money

from serp_procurement.application.dto import (
    RFQDTO,
    AgreementLineResponseDTO,
    ConvertRFQToPODTO,
    GoodsReceiptNoteCreateDTO,
    GoodsReceiptNoteDTO,
    GRNLineResponseDTO,
    PurchaseAgreementCreateDTO,
    PurchaseAgreementDTO,
    PurchaseAgreementUpdateDTO,
    PurchaseOrderCreateDTO,
    PurchaseOrderDTO,
    PurchaseOrderLineResponseDTO,
    PurchaseOrderUpdateDTO,
    QualityCheckDTO,
    RFQCreateDTO,
    RFQLineWithQuotesDTO,
    RFQQuoteDTO,
    RFQUpdateDTO,
)
from serp_procurement.domain.entities import (
    RFQ,
    AgreementLine,
    GoodsReceiptNote,
    GRNLine,
    PurchaseAgreement,
    PurchaseOrder,
    PurchaseOrderLine,
    RFQLine,
)
from serp_procurement.domain.events import (
    GoodsReceiptNoteCreated,
    GoodsReceiptQualityFailed,
    GoodsReceiptQualityPassed,
    PurchaseAgreementActivated,
    PurchaseAgreementCreated,
    PurchaseAgreementDeactivated,
    PurchaseAgreementUpdated,
    PurchaseOrderCancelled,
    PurchaseOrderConfirmed,
    PurchaseOrderCreated,
    PurchaseOrderReceived,
    RFQAccepted,
    RFQCancelled,
    RFQCreated,
    RFQQuoted,
    RFQSent,
)
from serp_procurement.domain.repositories import (
    IGoodsReceiptNoteRepository,
    IPurchaseAgreementRepository,
    IPurchaseOrderRepository,
    IRFQRepository,
)
from serp_procurement.domain.value_objects import (
    GRNNumber,
    PaymentTerms,
    PurchaseOrderNumber,
    PurchaseOrderState,
    RFQNumber,
    RFQState,
)


class RFQService:
    """Application service for RFQ operations."""

    def __init__(self, repository: IRFQRepository, event_bus: EventBus):
        self._repository = repository
        self._event_bus = event_bus

    def create_rfq(self, dto: RFQCreateDTO) -> RFQDTO:
        """Create a new RFQ."""
        # Generate RFQ number (simplified - should use sequence)
        rfq_number = RFQNumber(f"RFQ{len(self._repository.list_all()) + 1:06d}")

        # Create RFQ
        rfq = RFQ.create(
            rfq_number=rfq_number,
            title=dto.title,
            requester_id=dto.requester_id,
            request_date=dto.request_date,
            validity_date=dto.validity_date,
            supplier_ids=dto.supplier_ids,
            notes=dto.notes,
        )

        # Add lines
        for line_dto in dto.lines:
            line = RFQLine(
                product_id=line_dto.product_id,
                product_code=line_dto.product_code,
                description=line_dto.description,
                quantity=line_dto.quantity,
                uom_id=line_dto.uom_id,
                required_delivery_date=line_dto.required_delivery_date,
                notes=line_dto.notes,
            )
            rfq.add_line(line)

        self._repository.add(rfq)
        self._event_bus.publish(RFQCreated(aggregate_id=rfq.id))

        return self._map_rfq_to_dto(rfq)

    def update_rfq(self, rfq_id: str, dto: RFQUpdateDTO) -> RFQDTO:
        """Update RFQ."""
        rfq = self._repository.get_by_id(rfq_id)
        if not rfq:
            raise ValueError(f"RFQ {rfq_id} not found")

        if dto.title is not None:
            rfq.title = dto.title
        if dto.validity_date is not None:
            rfq.validity_date = dto.validity_date
        if dto.notes is not None:
            rfq.notes = dto.notes

        self._repository.update(rfq)
        return self._map_rfq_to_dto(rfq)

    def send_rfq(self, rfq_id: str) -> RFQDTO:
        """Send RFQ to suppliers."""
        rfq = self._repository.get_by_id(rfq_id)
        if not rfq:
            raise ValueError(f"RFQ {rfq_id} not found")

        rfq.send()
        self._repository.update(rfq)
        self._event_bus.publish(RFQSent(aggregate_id=rfq.id))

        return self._map_rfq_to_dto(rfq)

    def add_quote(self, rfq_id: str, dto: RFQQuoteDTO) -> RFQDTO:
        """Add supplier quote to RFQ line."""
        rfq = self._repository.get_by_id(rfq_id)
        if not rfq:
            raise ValueError(f"RFQ {rfq_id} not found")

        line = next((ln for ln in rfq.lines if ln.id == dto.line_id), None)
        if not line:
            raise ValueError(f"Line {dto.line_id} not found")

        line.add_quote(dto.supplier_id, Money(dto.quoted_price, dto.currency))

        self._repository.update(rfq)
        self._event_bus.publish(RFQQuoted(aggregate_id=rfq.id))

        return self._map_rfq_to_dto(rfq)

    def accept_rfq(self, rfq_id: str) -> RFQDTO:
        """Accept RFQ."""
        rfq = self._repository.get_by_id(rfq_id)
        if not rfq:
            raise ValueError(f"RFQ {rfq_id} not found")

        rfq.accept()
        self._repository.update(rfq)
        self._event_bus.publish(RFQAccepted(aggregate_id=rfq.id))

        return self._map_rfq_to_dto(rfq)

    def cancel_rfq(self, rfq_id: str) -> RFQDTO:
        """Cancel RFQ."""
        rfq = self._repository.get_by_id(rfq_id)
        if not rfq:
            raise ValueError(f"RFQ {rfq_id} not found")

        rfq.cancel()
        self._repository.update(rfq)
        self._event_bus.publish(RFQCancelled(aggregate_id=rfq.id))

        return self._map_rfq_to_dto(rfq)

    def get_rfq(self, rfq_id: str) -> RFQDTO | None:
        """Get RFQ by ID."""
        rfq = self._repository.get_by_id(rfq_id)
        return self._map_rfq_to_dto(rfq) if rfq else None

    def list_rfqs(self, state: RFQState | None = None) -> list[RFQDTO]:
        """List RFQs."""
        if state:
            rfqs = self._repository.list_by_state(state)
        else:
            rfqs = self._repository.list_all()
        return [self._map_rfq_to_dto(rfq) for rfq in rfqs]

    def _map_rfq_to_dto(self, rfq: RFQ) -> RFQDTO:
        """Map RFQ to DTO."""
        return RFQDTO(
            id=rfq.id,
            rfq_number=rfq.rfq_number.value,
            title=rfq.title,
            requester_id=rfq.requester_id,
            request_date=rfq.request_date,
            validity_date=rfq.validity_date,
            supplier_ids=rfq.supplier_ids,
            lines=[
                RFQLineWithQuotesDTO(
                    id=line.id,
                    product_id=line.product_id,
                    product_code=line.product_code,
                    description=line.description,
                    quantity=line.quantity,
                    uom_id=line.uom_id,
                    required_delivery_date=line.required_delivery_date,
                    notes=line.notes,
                    supplier_quotes={
                        sid: price.amount for sid, price in line.supplier_quotes.items()
                    },
                )
                for line in rfq.lines
            ],
            state=rfq.state,
            notes=rfq.notes,
            sent_date=rfq.sent_date,
            created_at=rfq.created_at,
            updated_at=rfq.updated_at,
        )


class PurchaseOrderService:
    """Application service for Purchase Order operations."""

    def __init__(
        self,
        repository: IPurchaseOrderRepository,
        rfq_repository: IRFQRepository,
        event_bus: EventBus,
    ):
        self._repository = repository
        self._rfq_repository = rfq_repository
        self._event_bus = event_bus

    def create_purchase_order(self, dto: PurchaseOrderCreateDTO) -> PurchaseOrderDTO:
        """Create a new purchase order."""
        # Generate PO number (simplified)
        po_number = PurchaseOrderNumber(f"PO{len(self._repository.list_all()) + 1:06d}")

        # Create payment terms
        payment_terms = PaymentTerms(
            code=dto.payment_terms_code,
            days=dto.payment_terms_days,
        )

        # Create PO
        po = PurchaseOrder.create(
            po_number=po_number,
            supplier_id=dto.supplier_id,
            order_date=dto.order_date,
            expected_delivery_date=dto.expected_delivery_date,
            payment_terms=payment_terms,
            delivery_terms=dto.delivery_terms,
            requester_id=dto.requester_id,
            delivery_address=dto.delivery_address,
            notes=dto.notes,
            rfq_id=dto.rfq_id,
        )

        # Add lines
        for line_dto in dto.lines:
            line = PurchaseOrderLine(
                product_id=line_dto.product_id,
                product_code=line_dto.product_code,
                description=line_dto.description,
                quantity=line_dto.quantity,
                uom_id=line_dto.uom_id,
                unit_price=Money(line_dto.unit_price, line_dto.currency),
                discount_percent=line_dto.discount_percent,
                expected_delivery_date=line_dto.expected_delivery_date,
                notes=line_dto.notes,
                rfq_line_id=line_dto.rfq_line_id,
            )
            po.add_line(line)

        self._repository.add(po)
        self._event_bus.publish(PurchaseOrderCreated(aggregate_id=po.id))

        return self._map_po_to_dto(po)

    def convert_rfq_to_po(self, dto: ConvertRFQToPODTO) -> PurchaseOrderDTO:
        """Convert RFQ to Purchase Order."""
        rfq = self._rfq_repository.get_by_id(dto.rfq_id)
        if not rfq:
            raise ValueError(f"RFQ {dto.rfq_id} not found")

        if rfq.state not in (RFQState.QUOTED, RFQState.ACCEPTED):
            raise ValueError("RFQ must be quoted or accepted to convert to PO")

        # Generate PO number
        po_number = PurchaseOrderNumber(f"PO{len(self._repository.list_all()) + 1:06d}")

        # Create payment terms
        payment_terms = PaymentTerms(
            code=dto.payment_terms_code,
            days=dto.payment_terms_days,
        )

        # Create PO
        po = PurchaseOrder.create(
            po_number=po_number,
            supplier_id=dto.supplier_id,
            order_date=dto.order_date,
            expected_delivery_date=dto.expected_delivery_date,
            payment_terms=payment_terms,
            delivery_terms=dto.delivery_terms,
            delivery_address=dto.delivery_address,
            notes=dto.notes,
            rfq_id=rfq.id,
        )

        # Add lines from RFQ with supplier's quotes
        for rfq_line in rfq.lines:
            # Get supplier's quote
            supplier_quote = rfq_line.supplier_quotes.get(dto.supplier_id)
            if not supplier_quote:
                continue  # Skip lines without supplier quote

            line = PurchaseOrderLine(
                product_id=rfq_line.product_id,
                product_code=rfq_line.product_code,
                description=rfq_line.description,
                quantity=rfq_line.quantity,
                uom_id=rfq_line.uom_id,
                unit_price=supplier_quote,
                expected_delivery_date=rfq_line.required_delivery_date,
                notes=rfq_line.notes,
                rfq_line_id=rfq_line.id,
            )
            po.add_line(line)

        self._repository.add(po)
        self._event_bus.publish(PurchaseOrderCreated(aggregate_id=po.id))

        return self._map_po_to_dto(po)

    def update_purchase_order(
        self, po_id: str, dto: PurchaseOrderUpdateDTO
    ) -> PurchaseOrderDTO:
        """Update purchase order."""
        po = self._repository.get_by_id(po_id)
        if not po:
            raise ValueError(f"Purchase order {po_id} not found")

        if dto.expected_delivery_date is not None:
            po.expected_delivery_date = dto.expected_delivery_date
        if dto.delivery_address is not None:
            po.delivery_address = dto.delivery_address
        if dto.notes is not None:
            po.notes = dto.notes

        self._repository.update(po)
        return self._map_po_to_dto(po)

    def confirm_purchase_order(self, po_id: str) -> PurchaseOrderDTO:
        """Confirm purchase order."""
        po = self._repository.get_by_id(po_id)
        if not po:
            raise ValueError(f"Purchase order {po_id} not found")

        po.confirm()
        self._repository.update(po)
        self._event_bus.publish(PurchaseOrderConfirmed(aggregate_id=po.id))

        return self._map_po_to_dto(po)

    def cancel_purchase_order(self, po_id: str) -> PurchaseOrderDTO:
        """Cancel purchase order."""
        po = self._repository.get_by_id(po_id)
        if not po:
            raise ValueError(f"Purchase order {po_id} not found")

        po.cancel()
        self._repository.update(po)
        self._event_bus.publish(PurchaseOrderCancelled(aggregate_id=po.id))

        return self._map_po_to_dto(po)

    def get_purchase_order(self, po_id: str) -> PurchaseOrderDTO | None:
        """Get purchase order by ID."""
        po = self._repository.get_by_id(po_id)
        return self._map_po_to_dto(po) if po else None

    def list_purchase_orders(
        self,
        supplier_id: str | None = None,
        state: PurchaseOrderState | None = None,
    ) -> list[PurchaseOrderDTO]:
        """List purchase orders."""
        if supplier_id:
            pos = self._repository.list_by_supplier(supplier_id)
        elif state:
            pos = self._repository.list_by_state(state)
        else:
            pos = self._repository.list_all()
        return [self._map_po_to_dto(po) for po in pos]

    def _map_po_to_dto(self, po: PurchaseOrder) -> PurchaseOrderDTO:
        """Map PO to DTO."""
        return PurchaseOrderDTO(
            id=po.id,
            po_number=po.po_number.value,
            supplier_id=po.supplier_id,
            order_date=po.order_date,
            expected_delivery_date=po.expected_delivery_date,
            payment_terms=po.payment_terms.code,
            delivery_terms=po.delivery_terms,
            lines=[
                PurchaseOrderLineResponseDTO(
                    id=line.id,
                    product_id=line.product_id,
                    product_code=line.product_code,
                    description=line.description,
                    quantity=line.quantity,
                    uom_id=line.uom_id,
                    unit_price=line.unit_price.amount,
                    currency=line.unit_price.currency,
                    discount_percent=line.discount_percent,
                    expected_delivery_date=line.expected_delivery_date,
                    notes=line.notes,
                    rfq_line_id=line.rfq_line_id,
                    ordered_quantity=line.quantity,
                    received_quantity=line.received_quantity,
                    pending_quantity=line.pending_quantity,
                    is_fully_received=line.is_fully_received,
                    subtotal=line.subtotal.amount,
                    discount_amount=line.discount_amount.amount,
                    total=line.total.amount,
                )
                for line in po.lines
            ],
            state=po.state,
            receipt_status=po.receipt_status,
            requester_id=po.requester_id,
            delivery_address=po.delivery_address,
            notes=po.notes,
            rfq_id=po.rfq_id,
            confirmed_date=po.confirmed_date,
            cancelled_date=po.cancelled_date,
            subtotal=po.subtotal.amount,
            total=po.total.amount,
            currency=po.lines[0].unit_price.currency if po.lines else "USD",
            created_at=po.created_at,
            updated_at=po.updated_at,
        )


class GoodsReceiptService:
    """Application service for Goods Receipt operations."""

    def __init__(
        self,
        repository: IGoodsReceiptNoteRepository,
        po_repository: IPurchaseOrderRepository,
        event_bus: EventBus,
    ):
        self._repository = repository
        self._po_repository = po_repository
        self._event_bus = event_bus

    def create_receipt(self, dto: GoodsReceiptNoteCreateDTO) -> GoodsReceiptNoteDTO:
        """Create goods receipt note."""
        # Validate PO exists and is confirmed
        po = self._po_repository.get_by_id(dto.purchase_order_id)
        if not po:
            raise ValueError(f"Purchase order {dto.purchase_order_id} not found")
        if po.state != PurchaseOrderState.CONFIRMED:
            raise ValueError("Can only receive confirmed purchase orders")

        # Generate GRN number
        grn_number = GRNNumber(f"GRN{len(self._repository.list_all()) + 1:06d}")

        # Create GRN
        grn = GoodsReceiptNote.create(
            grn_number=grn_number,
            purchase_order_id=dto.purchase_order_id,
            receipt_date=dto.receipt_date,
            received_by=dto.received_by,
            carrier=dto.carrier,
            tracking_number=dto.tracking_number,
            notes=dto.notes,
        )

        # Add lines and update PO quantities
        for line_dto in dto.lines:
            line = GRNLine(
                po_line_id=line_dto.po_line_id,
                product_id=line_dto.product_id,
                product_code=line_dto.product_code,
                received_quantity=line_dto.received_quantity,
                uom_id=line_dto.uom_id,
                notes=line_dto.notes,
            )
            grn.add_line(line)

            # Update PO line received quantity
            po.receive_line(line_dto.po_line_id, line_dto.received_quantity)

        self._repository.add(grn)
        self._po_repository.update(po)
        self._event_bus.publish(GoodsReceiptNoteCreated(aggregate_id=grn.id))

        # Check if PO fully received
        if po.state == PurchaseOrderState.RECEIVED:
            self._event_bus.publish(PurchaseOrderReceived(aggregate_id=po.id))

        return self._map_grn_to_dto(grn)

    def quality_check(
        self, grn_id: str, checks: list[QualityCheckDTO]
    ) -> GoodsReceiptNoteDTO:
        """Perform quality check on receipt."""
        grn = self._repository.get_by_id(grn_id)
        if not grn:
            raise ValueError(f"GRN {grn_id} not found")

        for check in checks:
            line = next((ln for ln in grn.lines if ln.id == check.line_id), None)
            if not line:
                raise ValueError(f"Line {check.line_id} not found")

            if check.passed:
                line.pass_quality()
                self._event_bus.publish(GoodsReceiptQualityPassed(aggregate_id=grn.id))
            else:
                line.fail_quality(check.rejected_quantity)
                self._event_bus.publish(GoodsReceiptQualityFailed(aggregate_id=grn.id))

        self._repository.update(grn)
        return self._map_grn_to_dto(grn)

    def get_receipt(self, grn_id: str) -> GoodsReceiptNoteDTO | None:
        """Get goods receipt note by ID."""
        grn = self._repository.get_by_id(grn_id)
        return self._map_grn_to_dto(grn) if grn else None

    def list_receipts(
        self, purchase_order_id: str | None = None
    ) -> list[GoodsReceiptNoteDTO]:
        """List goods receipt notes."""
        if purchase_order_id:
            grns = self._repository.list_by_purchase_order(purchase_order_id)
        else:
            grns = self._repository.list_all()
        return [self._map_grn_to_dto(grn) for grn in grns]

    def _map_grn_to_dto(self, grn: GoodsReceiptNote) -> GoodsReceiptNoteDTO:
        """Map GRN to DTO."""
        return GoodsReceiptNoteDTO(
            id=grn.id,
            grn_number=grn.grn_number.value,
            purchase_order_id=grn.purchase_order_id,
            receipt_date=grn.receipt_date,
            received_by=grn.received_by,
            lines=[
                GRNLineResponseDTO(
                    id=line.id,
                    po_line_id=line.po_line_id,
                    product_id=line.product_id,
                    product_code=line.product_code,
                    received_quantity=line.received_quantity,
                    uom_id=line.uom_id,
                    notes=line.notes,
                    quality_status=line.quality_status,
                    rejected_quantity=line.rejected_quantity,
                    accepted_quantity=line.accepted_quantity,
                )
                for line in grn.lines
            ],
            carrier=grn.carrier,
            tracking_number=grn.tracking_number,
            notes=grn.notes,
            overall_quality_status=grn.overall_quality_status,
            created_at=grn.created_at,
            updated_at=grn.updated_at,
        )


class PurchaseAgreementService:
    """Application service for Purchase Agreement operations."""

    def __init__(self, repository: IPurchaseAgreementRepository, event_bus: EventBus):
        self._repository = repository
        self._event_bus = event_bus

    def create_agreement(self, dto: PurchaseAgreementCreateDTO) -> PurchaseAgreementDTO:
        """Create purchase agreement."""
        # Generate agreement number
        agreement_number = f"AGR{len(self._repository.list_all()) + 1:06d}"

        # Create payment terms
        payment_terms = PaymentTerms(
            code=dto.payment_terms_code,
            days=dto.payment_terms_days,
        )

        # Create agreement
        agreement = PurchaseAgreement.create(
            agreement_number=agreement_number,
            supplier_id=dto.supplier_id,
            valid_from=dto.valid_from,
            valid_to=dto.valid_to,
            payment_terms=payment_terms,
            notes=dto.notes,
        )

        # Add lines
        for line_dto in dto.lines:
            line = AgreementLine(
                product_id=line_dto.product_id,
                product_code=line_dto.product_code,
                description=line_dto.description,
                committed_quantity=line_dto.committed_quantity,
                uom_id=line_dto.uom_id,
                unit_price=Money(line_dto.unit_price, line_dto.currency),
                discount_percent=line_dto.discount_percent,
            )
            agreement.add_line(line)

        self._repository.add(agreement)
        self._event_bus.publish(PurchaseAgreementCreated(aggregate_id=agreement.id))

        return self._map_agreement_to_dto(agreement)

    def update_agreement(
        self, agreement_id: str, dto: PurchaseAgreementUpdateDTO
    ) -> PurchaseAgreementDTO:
        """Update purchase agreement."""
        agreement = self._repository.get_by_id(agreement_id)
        if not agreement:
            raise ValueError(f"Agreement {agreement_id} not found")

        if dto.valid_to is not None:
            agreement.valid_to = dto.valid_to
        if dto.notes is not None:
            agreement.notes = dto.notes

        self._repository.update(agreement)
        self._event_bus.publish(PurchaseAgreementUpdated(aggregate_id=agreement.id))

        return self._map_agreement_to_dto(agreement)

    def activate_agreement(self, agreement_id: str) -> PurchaseAgreementDTO:
        """Activate agreement."""
        agreement = self._repository.get_by_id(agreement_id)
        if not agreement:
            raise ValueError(f"Agreement {agreement_id} not found")

        agreement.activate()
        self._repository.update(agreement)
        self._event_bus.publish(PurchaseAgreementActivated(aggregate_id=agreement.id))

        return self._map_agreement_to_dto(agreement)

    def deactivate_agreement(self, agreement_id: str) -> PurchaseAgreementDTO:
        """Deactivate agreement."""
        agreement = self._repository.get_by_id(agreement_id)
        if not agreement:
            raise ValueError(f"Agreement {agreement_id} not found")

        agreement.deactivate()
        self._repository.update(agreement)
        self._event_bus.publish(PurchaseAgreementDeactivated(aggregate_id=agreement.id))

        return self._map_agreement_to_dto(agreement)

    def get_agreement(self, agreement_id: str) -> PurchaseAgreementDTO | None:
        """Get agreement by ID."""
        agreement = self._repository.get_by_id(agreement_id)
        return self._map_agreement_to_dto(agreement) if agreement else None

    def list_agreements(
        self, supplier_id: str | None = None, active_only: bool = False
    ) -> list[PurchaseAgreementDTO]:
        """List agreements."""
        if active_only:
            agreements = self._repository.list_active()
        elif supplier_id:
            agreements = self._repository.list_by_supplier(supplier_id)
        else:
            agreements = self._repository.list_all()
        return [self._map_agreement_to_dto(agr) for agr in agreements]

    def _map_agreement_to_dto(
        self, agreement: PurchaseAgreement
    ) -> PurchaseAgreementDTO:
        """Map agreement to DTO."""
        return PurchaseAgreementDTO(
            id=agreement.id,
            agreement_number=agreement.agreement_number,
            supplier_id=agreement.supplier_id,
            valid_from=agreement.valid_from,
            valid_to=agreement.valid_to,
            payment_terms=agreement.payment_terms.code,
            lines=[
                AgreementLineResponseDTO(
                    id=line.id,
                    product_id=line.product_id,
                    product_code=line.product_code,
                    description=line.description,
                    committed_quantity=line.committed_quantity,
                    uom_id=line.uom_id,
                    unit_price=line.unit_price.amount,
                    currency=line.unit_price.currency,
                    discount_percent=line.discount_percent,
                    called_off_quantity=line.called_off_quantity,
                    remaining_quantity=line.remaining_quantity,
                )
                for line in agreement.lines
            ],
            is_active=agreement.is_active,
            notes=agreement.notes,
            created_at=agreement.created_at,
            updated_at=agreement.updated_at,
        )
