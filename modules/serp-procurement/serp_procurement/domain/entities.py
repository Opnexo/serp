"""Domain entities for Procurement."""

from datetime import date, datetime
from decimal import Decimal

from serp_core.domain.base import AggregateRoot, Entity
from serp_crm.domain import Money

from serp_procurement.domain.value_objects import (
    DeliveryTerms,
    GRNNumber,
    PaymentTerms,
    PurchaseOrderNumber,
    PurchaseOrderState,
    QualityStatus,
    QuantityTracking,
    ReceiptStatus,
    RFQNumber,
    RFQState,
)

# RFQ Entities


class RFQLine(Entity):
    """RFQ line item."""

    def __init__(
        self,
        product_id: str,
        product_code: str,
        description: str,
        quantity: Decimal,
        uom_id: str,
        required_delivery_date: date | None = None,
        notes: str | None = None,
    ):
        super().__init__()
        self.product_id = product_id
        self.product_code = product_code
        self.description = description
        self.quantity = quantity
        self.uom_id = uom_id
        self.required_delivery_date = required_delivery_date
        self.notes = notes

        # Supplier quotes
        self.supplier_quotes: dict[str, Money] = {}  # supplier_id -> quoted_price

    def add_quote(self, supplier_id: str, quoted_price: Money) -> None:
        """Add supplier quote for this line."""
        self.supplier_quotes[supplier_id] = quoted_price

    def get_best_quote(self) -> tuple[str, Money] | None:
        """Get supplier with best (lowest) quote."""
        if not self.supplier_quotes:
            return None
        return min(self.supplier_quotes.items(), key=lambda x: x[1].amount)


class RFQ(AggregateRoot):
    """Request for Quotation aggregate."""

    def __init__(
        self,
        rfq_number: RFQNumber,
        title: str,
        requester_id: str,
        request_date: date,
        validity_date: date,
        supplier_ids: list[str],
        lines: list[RFQLine],
        state: RFQState = RFQState.DRAFT,
        notes: str | None = None,
    ):
        super().__init__()
        self.rfq_number = rfq_number
        self.title = title
        self.requester_id = requester_id
        self.request_date = request_date
        self.validity_date = validity_date
        self.supplier_ids = supplier_ids
        self.lines = lines
        self.state = state
        self.notes = notes
        self.sent_date: datetime | None = None

    @classmethod
    def create(
        cls,
        rfq_number: RFQNumber,
        title: str,
        requester_id: str,
        request_date: date,
        validity_date: date,
        supplier_ids: list[str],
        notes: str | None = None,
    ) -> "RFQ":
        """Create a new RFQ."""
        if not supplier_ids:
            raise ValueError("RFQ must have at least one supplier")
        if validity_date < request_date:
            raise ValueError("Validity date must be after request date")

        return cls(
            rfq_number=rfq_number,
            title=title,
            requester_id=requester_id,
            request_date=request_date,
            validity_date=validity_date,
            supplier_ids=supplier_ids,
            lines=[],
            state=RFQState.DRAFT,
            notes=notes,
        )

    def add_line(self, line: RFQLine) -> None:
        """Add a line to the RFQ."""
        if self.state != RFQState.DRAFT:
            raise ValueError("Cannot add lines to non-draft RFQ")
        self.lines.append(line)

    def send(self) -> None:
        """Send RFQ to suppliers."""
        if self.state != RFQState.DRAFT:
            raise ValueError("Can only send draft RFQs")
        if not self.lines:
            raise ValueError("Cannot send RFQ without lines")

        self.state = RFQState.SENT
        self.sent_date = datetime.now()

    def mark_quoted(self) -> None:
        """Mark RFQ as having received quotes."""
        if self.state != RFQState.SENT:
            raise ValueError("RFQ must be sent to receive quotes")
        self.state = RFQState.QUOTED

    def accept(self) -> None:
        """Accept an RFQ (ready to convert to PO)."""
        if self.state not in (RFQState.SENT, RFQState.QUOTED):
            raise ValueError("RFQ must be sent or quoted to accept")
        self.state = RFQState.ACCEPTED

    def cancel(self) -> None:
        """Cancel the RFQ."""
        if self.state in (RFQState.ACCEPTED, RFQState.CANCELLED):
            raise ValueError(f"Cannot cancel RFQ in {self.state} state")
        self.state = RFQState.CANCELLED


# Purchase Order Entities


class PurchaseOrderLine(Entity):
    """Purchase order line item."""

    def __init__(
        self,
        product_id: str,
        product_code: str,
        description: str,
        quantity: Decimal,
        uom_id: str,
        unit_price: Money,
        discount_percent: Decimal = Decimal("0"),
        expected_delivery_date: date | None = None,
        notes: str | None = None,
        rfq_line_id: str | None = None,
    ):
        super().__init__()
        self.product_id = product_id
        self.product_code = product_code
        self.description = description
        self.uom_id = uom_id
        self.unit_price = unit_price
        self.discount_percent = discount_percent
        self.expected_delivery_date = expected_delivery_date
        self.notes = notes
        self.rfq_line_id = rfq_line_id

        # Quantity tracking
        self.tracking = QuantityTracking(
            ordered_quantity=quantity, received_quantity=Decimal("0")
        )

    @property
    def quantity(self) -> Decimal:
        """Ordered quantity."""
        return self.tracking.ordered_quantity

    @property
    def received_quantity(self) -> Decimal:
        """Received quantity."""
        return self.tracking.received_quantity

    @property
    def pending_quantity(self) -> Decimal:
        """Pending quantity."""
        return self.tracking.pending_quantity

    @property
    def subtotal(self) -> Money:
        """Line subtotal before discount."""
        amount = self.unit_price.amount * self.quantity
        return Money(amount, self.unit_price.currency)

    @property
    def discount_amount(self) -> Money:
        """Discount amount."""
        amount = self.subtotal.amount * (self.discount_percent / Decimal("100"))
        return Money(amount, self.unit_price.currency)

    @property
    def total(self) -> Money:
        """Line total after discount."""
        return self.subtotal - self.discount_amount

    def receive(self, quantity: Decimal) -> None:
        """Record received quantity."""
        self.tracking = self.tracking.receive(quantity)

    @property
    def is_fully_received(self) -> bool:
        """Check if fully received."""
        return self.tracking.is_fully_received


class PurchaseOrder(AggregateRoot):
    """Purchase Order aggregate."""

    def __init__(
        self,
        po_number: PurchaseOrderNumber,
        supplier_id: str,
        order_date: date,
        expected_delivery_date: date | None,
        payment_terms: PaymentTerms,
        delivery_terms: DeliveryTerms,
        lines: list[PurchaseOrderLine],
        state: PurchaseOrderState = PurchaseOrderState.DRAFT,
        requester_id: str | None = None,
        delivery_address: str | None = None,
        notes: str | None = None,
        rfq_id: str | None = None,
    ):
        super().__init__()
        self.po_number = po_number
        self.supplier_id = supplier_id
        self.order_date = order_date
        self.expected_delivery_date = expected_delivery_date
        self.payment_terms = payment_terms
        self.delivery_terms = delivery_terms
        self.lines = lines
        self.state = state
        self.requester_id = requester_id
        self.delivery_address = delivery_address
        self.notes = notes
        self.rfq_id = rfq_id
        self.confirmed_date: datetime | None = None
        self.cancelled_date: datetime | None = None

    @classmethod
    def create(
        cls,
        po_number: PurchaseOrderNumber,
        supplier_id: str,
        order_date: date,
        expected_delivery_date: date | None,
        payment_terms: PaymentTerms,
        delivery_terms: DeliveryTerms,
        requester_id: str | None = None,
        delivery_address: str | None = None,
        notes: str | None = None,
        rfq_id: str | None = None,
    ) -> "PurchaseOrder":
        """Create a new purchase order."""
        return cls(
            po_number=po_number,
            supplier_id=supplier_id,
            order_date=order_date,
            expected_delivery_date=expected_delivery_date,
            payment_terms=payment_terms,
            delivery_terms=delivery_terms,
            lines=[],
            state=PurchaseOrderState.DRAFT,
            requester_id=requester_id,
            delivery_address=delivery_address,
            notes=notes,
            rfq_id=rfq_id,
        )

    def add_line(self, line: PurchaseOrderLine) -> None:
        """Add a line to the purchase order."""
        if self.state != PurchaseOrderState.DRAFT:
            raise ValueError("Cannot add lines to non-draft purchase order")
        self.lines.append(line)

    def confirm(self) -> None:
        """Confirm the purchase order."""
        if self.state != PurchaseOrderState.DRAFT:
            raise ValueError("Can only confirm draft purchase orders")
        if not self.lines:
            raise ValueError("Cannot confirm purchase order without lines")

        self.state = PurchaseOrderState.CONFIRMED
        self.confirmed_date = datetime.now()

    def cancel(self) -> None:
        """Cancel the purchase order."""
        if self.state not in (
            PurchaseOrderState.DRAFT,
            PurchaseOrderState.CONFIRMED,
        ):
            raise ValueError(f"Cannot cancel purchase order in {self.state} state")

        self.state = PurchaseOrderState.CANCELLED
        self.cancelled_date = datetime.now()

    def receive_line(self, line_id: str, quantity: Decimal) -> None:
        """Record received quantity for a line."""
        if self.state != PurchaseOrderState.CONFIRMED:
            raise ValueError("Can only receive confirmed purchase orders")

        line = next((l for l in self.lines if l.id == line_id), None)
        if not line:
            raise ValueError(f"Line {line_id} not found")

        line.receive(quantity)

        # Update order state based on receipt status
        if all(line.is_fully_received for line in self.lines):
            self.state = PurchaseOrderState.RECEIVED

    @property
    def subtotal(self) -> Money:
        """Order subtotal."""
        if not self.lines:
            return Money(Decimal("0"), "USD")
        total = sum((line.total.amount for line in self.lines), Decimal("0"))
        return Money(total, self.lines[0].unit_price.currency)

    @property
    def total(self) -> Money:
        """Order total (same as subtotal, could add taxes/shipping)."""
        return self.subtotal

    @property
    def receipt_status(self) -> ReceiptStatus:
        """Get receipt status."""
        if all(line.tracking.received_quantity == Decimal("0") for line in self.lines):
            return ReceiptStatus.PENDING
        elif all(line.is_fully_received for line in self.lines):
            return ReceiptStatus.COMPLETE
        else:
            return ReceiptStatus.PARTIAL


# Goods Receipt Note Entities


class GRNLine(Entity):
    """Goods receipt note line."""

    def __init__(
        self,
        po_line_id: str,
        product_id: str,
        product_code: str,
        received_quantity: Decimal,
        uom_id: str,
        quality_status: QualityStatus = QualityStatus.PENDING,
        rejected_quantity: Decimal = Decimal("0"),
        notes: str | None = None,
    ):
        super().__init__()
        self.po_line_id = po_line_id
        self.product_id = product_id
        self.product_code = product_code
        self.received_quantity = received_quantity
        self.uom_id = uom_id
        self.quality_status = quality_status
        self.rejected_quantity = rejected_quantity
        self.notes = notes

    @property
    def accepted_quantity(self) -> Decimal:
        """Accepted quantity after quality check."""
        return self.received_quantity - self.rejected_quantity

    def pass_quality(self) -> None:
        """Mark as passed quality check."""
        self.quality_status = QualityStatus.PASSED

    def fail_quality(self, rejected_quantity: Decimal) -> None:
        """Mark as failed quality check."""
        if rejected_quantity > self.received_quantity:
            raise ValueError("Rejected quantity cannot exceed received quantity")
        self.quality_status = QualityStatus.FAILED
        self.rejected_quantity = rejected_quantity

    def waive_quality(self) -> None:
        """Waive quality check."""
        self.quality_status = QualityStatus.WAIVED


class GoodsReceiptNote(AggregateRoot):
    """Goods Receipt Note aggregate."""

    def __init__(
        self,
        grn_number: GRNNumber,
        purchase_order_id: str,
        receipt_date: date,
        received_by: str,
        lines: list[GRNLine],
        carrier: str | None = None,
        tracking_number: str | None = None,
        notes: str | None = None,
    ):
        super().__init__()
        self.grn_number = grn_number
        self.purchase_order_id = purchase_order_id
        self.receipt_date = receipt_date
        self.received_by = received_by
        self.lines = lines
        self.carrier = carrier
        self.tracking_number = tracking_number
        self.notes = notes

    @classmethod
    def create(
        cls,
        grn_number: GRNNumber,
        purchase_order_id: str,
        receipt_date: date,
        received_by: str,
        carrier: str | None = None,
        tracking_number: str | None = None,
        notes: str | None = None,
    ) -> "GoodsReceiptNote":
        """Create a new goods receipt note."""
        return cls(
            grn_number=grn_number,
            purchase_order_id=purchase_order_id,
            receipt_date=receipt_date,
            received_by=received_by,
            lines=[],
            carrier=carrier,
            tracking_number=tracking_number,
            notes=notes,
        )

    def add_line(self, line: GRNLine) -> None:
        """Add a line to the GRN."""
        self.lines.append(line)

    @property
    def overall_quality_status(self) -> QualityStatus:
        """Overall quality status of the receipt."""
        if all(line.quality_status == QualityStatus.PASSED for line in self.lines):
            return QualityStatus.PASSED
        elif any(line.quality_status == QualityStatus.FAILED for line in self.lines):
            return QualityStatus.FAILED
        elif any(line.quality_status == QualityStatus.PENDING for line in self.lines):
            return QualityStatus.PENDING
        else:
            return QualityStatus.WAIVED


# Purchase Agreement Entities


class AgreementLine(Entity):
    """Purchase agreement line."""

    def __init__(
        self,
        product_id: str,
        product_code: str,
        description: str,
        committed_quantity: Decimal,
        uom_id: str,
        unit_price: Money,
        discount_percent: Decimal = Decimal("0"),
    ):
        super().__init__()
        self.product_id = product_id
        self.product_code = product_code
        self.description = description
        self.committed_quantity = committed_quantity
        self.uom_id = uom_id
        self.unit_price = unit_price
        self.discount_percent = discount_percent
        self.called_off_quantity = Decimal("0")

    @property
    def remaining_quantity(self) -> Decimal:
        """Remaining quantity to call off."""
        return self.committed_quantity - self.called_off_quantity

    def call_off(self, quantity: Decimal) -> None:
        """Call off quantity from agreement."""
        if quantity > self.remaining_quantity:
            raise ValueError("Call-off quantity exceeds remaining quantity")
        self.called_off_quantity += quantity


class PurchaseAgreement(AggregateRoot):
    """Purchase Agreement aggregate."""

    def __init__(
        self,
        agreement_number: str,
        supplier_id: str,
        valid_from: date,
        valid_to: date,
        payment_terms: PaymentTerms,
        lines: list[AgreementLine],
        is_active: bool = True,
        notes: str | None = None,
    ):
        super().__init__()
        self.agreement_number = agreement_number
        self.supplier_id = supplier_id
        self.valid_from = valid_from
        self.valid_to = valid_to
        self.payment_terms = payment_terms
        self.lines = lines
        self.is_active = is_active
        self.notes = notes

    @classmethod
    def create(
        cls,
        agreement_number: str,
        supplier_id: str,
        valid_from: date,
        valid_to: date,
        payment_terms: PaymentTerms,
        notes: str | None = None,
    ) -> "PurchaseAgreement":
        """Create a new purchase agreement."""
        if valid_to < valid_from:
            raise ValueError("Valid to date must be after valid from date")

        return cls(
            agreement_number=agreement_number,
            supplier_id=supplier_id,
            valid_from=valid_from,
            valid_to=valid_to,
            payment_terms=payment_terms,
            lines=[],
            is_active=True,
            notes=notes,
        )

    def add_line(self, line: AgreementLine) -> None:
        """Add a line to the agreement."""
        self.lines.append(line)

    def is_valid_on(self, check_date: date) -> bool:
        """Check if agreement is valid on a date."""
        return self.is_active and self.valid_from <= check_date <= self.valid_to

    def activate(self) -> None:
        """Activate the agreement."""
        self.is_active = True

    def deactivate(self) -> None:
        """Deactivate the agreement."""
        self.is_active = False
