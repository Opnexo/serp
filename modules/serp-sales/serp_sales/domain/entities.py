"""
Domain entities for Sales module.
"""

from datetime import date, datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from serp_core.domain.entities import AggregateRoot, Entity
from serp_crm.domain.value_objects import Money

from serp_sales.domain.value_objects import (
    Discount,
    OrderNumber,
    OrderStatus,
    QuoteNumber,
    QuoteStatus,
    ShippingInfo,
    TaxRate,
)

if TYPE_CHECKING:
    pass


class QuoteLine(Entity):
    """Quote line item (owned by Quote)."""

    def __init__(
        self,
        product_code: str,
        description: str,
        quantity: Decimal,
        unit_price: Money,
        discount_percent: Decimal = Decimal("0"),
        tax_rate: Decimal = Decimal("0"),
        id: str | None = None,
    ):
        super().__init__(id)
        if quantity <= 0:
            raise ValueError("Quantity must be positive")
        if unit_price.amount < 0:
            raise ValueError("Unit price cannot be negative")

        self.product_code = product_code
        self.description = description
        self.quantity = quantity
        self.unit_price = unit_price
        self.discount = Discount(discount_percent)
        self.tax_rate = TaxRate(tax_rate)

    @property
    def line_subtotal(self) -> Money:
        """Calculate line subtotal (quantity × unit_price)."""
        return Money(self.quantity * self.unit_price.amount, self.unit_price.currency)

    @property
    def discount_amount(self) -> Money:
        """Calculate discount amount."""
        discount_value = self.line_subtotal.amount - self.discount.apply(
            self.line_subtotal.amount
        )
        return Money(discount_value, self.unit_price.currency)

    @property
    def line_total_before_tax(self) -> Money:
        """Calculate line total after discount, before tax."""
        return Money(
            self.discount.apply(self.line_subtotal.amount), self.unit_price.currency
        )

    @property
    def tax_amount(self) -> Money:
        """Calculate tax amount."""
        return Money(
            self.tax_rate.apply(self.line_total_before_tax.amount),
            self.unit_price.currency,
        )

    @property
    def line_total(self) -> Money:
        """Calculate final line total (after discount and tax)."""
        return Money(
            self.line_total_before_tax.amount + self.tax_amount.amount,
            self.unit_price.currency,
        )


class Quote(AggregateRoot):
    """Quote aggregate root."""

    def __init__(
        self,
        quote_number: QuoteNumber,
        partner_id: str,
        quote_date: date,
        valid_until: date,
        currency: str,
        lines: list[QuoteLine] | None = None,
        status: QuoteStatus = QuoteStatus.DRAFT,
        notes: str | None = None,
        sent_at: datetime | None = None,
        accepted_at: datetime | None = None,
        rejected_at: datetime | None = None,
        id: str | None = None,
    ):
        super().__init__(id)
        if valid_until <= quote_date:
            raise ValueError("Valid until must be after quote date")

        self.quote_number = quote_number
        self.partner_id = partner_id
        self.quote_date = quote_date
        self.valid_until = valid_until
        self.currency = currency
        self.lines = lines or []
        self.status = status
        self.notes = notes
        self.sent_at = sent_at
        self.accepted_at = accepted_at
        self.rejected_at = rejected_at

    @property
    def subtotal(self) -> Money:
        """Calculate quote subtotal."""
        total = sum((line.line_subtotal.amount for line in self.lines), Decimal("0"))
        return Money(total, self.currency)

    @property
    def discount_amount(self) -> Money:
        """Calculate total discount amount."""
        total = sum((line.discount_amount.amount for line in self.lines), Decimal("0"))
        return Money(total, self.currency)

    @property
    def total_before_tax(self) -> Money:
        """Calculate total before tax."""
        total = sum(
            (line.line_total_before_tax.amount for line in self.lines), Decimal("0")
        )
        return Money(total, self.currency)

    @property
    def tax_amount(self) -> Money:
        """Calculate total tax amount."""
        total = sum((line.tax_amount.amount for line in self.lines), Decimal("0"))
        return Money(total, self.currency)

    @property
    def total_amount(self) -> Money:
        """Calculate quote total."""
        total = sum((line.line_total.amount for line in self.lines), Decimal("0"))
        return Money(total, self.currency)

    @property
    def is_expired(self) -> bool:
        """Check if quote has expired."""
        return date.today() > self.valid_until and self.status == QuoteStatus.SENT

    def add_line(self, line: QuoteLine) -> None:
        """Add a line to the quote."""
        if self.status != QuoteStatus.DRAFT:
            raise ValueError("Can only modify draft quotes")
        self.lines.append(line)
        self._add_event("QuoteUpdated", {"quote_id": self.id})

    def remove_line(self, line_id: str) -> None:
        """Remove a line from the quote."""
        if self.status != QuoteStatus.DRAFT:
            raise ValueError("Can only modify draft quotes")
        self.lines = [line for line in self.lines if line.id != line_id]
        self._add_event("QuoteUpdated", {"quote_id": self.id})

    def send(self) -> None:
        """Send quote to customer."""
        if self.status != QuoteStatus.DRAFT:
            raise ValueError("Can only send draft quotes")
        if not self.lines:
            raise ValueError("Cannot send quote without lines")
        self.status = QuoteStatus.SENT
        self.sent_at = datetime.now()
        self._add_event("QuoteSent", {"quote_id": self.id})

    def accept(self) -> None:
        """Accept the quote."""
        if self.status != QuoteStatus.SENT:
            raise ValueError("Can only accept sent quotes")
        if self.is_expired:
            raise ValueError("Cannot accept expired quote")
        self.status = QuoteStatus.ACCEPTED
        self.accepted_at = datetime.now()
        self._add_event("QuoteAccepted", {"quote_id": self.id})

    def reject(self, reason: str | None = None) -> None:
        """Reject the quote."""
        if self.status != QuoteStatus.SENT:
            raise ValueError("Can only reject sent quotes")
        self.status = QuoteStatus.REJECTED
        self.rejected_at = datetime.now()
        self._add_event("QuoteRejected", {"quote_id": self.id, "reason": reason or ""})

    def mark_expired(self) -> None:
        """Mark quote as expired."""
        if self.status != QuoteStatus.SENT:
            raise ValueError("Can only expire sent quotes")
        self.status = QuoteStatus.EXPIRED
        self._add_event("QuoteExpired", {"quote_id": self.id})


class OrderLine(Entity):
    """Sales order line item (owned by SalesOrder)."""

    def __init__(
        self,
        product_code: str,
        description: str,
        quantity: Decimal,
        unit_price: Money,
        discount_percent: Decimal = Decimal("0"),
        tax_rate: Decimal = Decimal("0"),
        quantity_delivered: Decimal = Decimal("0"),
        id: str | None = None,
    ):
        super().__init__(id)
        if quantity <= 0:
            raise ValueError("Quantity must be positive")
        if unit_price.amount < 0:
            raise ValueError("Unit price cannot be negative")
        if quantity_delivered < 0 or quantity_delivered > quantity:
            raise ValueError("Invalid quantity delivered")

        self.product_code = product_code
        self.description = description
        self.quantity = quantity
        self.unit_price = unit_price
        self.discount = Discount(discount_percent)
        self.tax_rate = TaxRate(tax_rate)
        self.quantity_delivered = quantity_delivered

    @property
    def line_subtotal(self) -> Money:
        """Calculate line subtotal."""
        return Money(self.quantity * self.unit_price.amount, self.unit_price.currency)

    @property
    def discount_amount(self) -> Money:
        """Calculate discount amount."""
        discount_value = self.line_subtotal.amount - self.discount.apply(
            self.line_subtotal.amount
        )
        return Money(discount_value, self.unit_price.currency)

    @property
    def line_total_before_tax(self) -> Money:
        """Calculate line total after discount, before tax."""
        return Money(
            self.discount.apply(self.line_subtotal.amount), self.unit_price.currency
        )

    @property
    def tax_amount(self) -> Money:
        """Calculate tax amount."""
        return Money(
            self.tax_rate.apply(self.line_total_before_tax.amount),
            self.unit_price.currency,
        )

    @property
    def line_total(self) -> Money:
        """Calculate final line total."""
        return Money(
            self.line_total_before_tax.amount + self.tax_amount.amount,
            self.unit_price.currency,
        )

    @property
    def is_fully_delivered(self) -> bool:
        """Check if line is fully delivered."""
        return self.quantity_delivered >= self.quantity


class SalesOrder(AggregateRoot):
    """Sales order aggregate root."""

    def __init__(
        self,
        order_number: OrderNumber,
        partner_id: str,
        order_date: date,
        currency: str,
        lines: list[OrderLine] | None = None,
        status: OrderStatus = OrderStatus.DRAFT,
        quote_id: str | None = None,
        requested_delivery_date: date | None = None,
        shipping_info: ShippingInfo | None = None,
        notes: str | None = None,
        confirmed_at: datetime | None = None,
        shipped_at: datetime | None = None,
        delivered_at: datetime | None = None,
        cancelled_at: datetime | None = None,
        id: str | None = None,
    ):
        super().__init__(id)
        self.order_number = order_number
        self.partner_id = partner_id
        self.order_date = order_date
        self.currency = currency
        self.lines = lines or []
        self.status = status
        self.quote_id = quote_id
        self.requested_delivery_date = requested_delivery_date
        self.shipping_info = shipping_info
        self.notes = notes
        self.confirmed_at = confirmed_at
        self.shipped_at = shipped_at
        self.delivered_at = delivered_at
        self.cancelled_at = cancelled_at

    @property
    def subtotal(self) -> Money:
        """Calculate order subtotal."""
        total = sum((line.line_subtotal.amount for line in self.lines), Decimal("0"))
        return Money(total, self.currency)

    @property
    def discount_amount(self) -> Money:
        """Calculate total discount amount."""
        total = sum((line.discount_amount.amount for line in self.lines), Decimal("0"))
        return Money(total, self.currency)

    @property
    def total_before_tax(self) -> Money:
        """Calculate total before tax."""
        total = sum(
            (line.line_total_before_tax.amount for line in self.lines), Decimal("0")
        )
        return Money(total, self.currency)

    @property
    def tax_amount(self) -> Money:
        """Calculate total tax amount."""
        total = sum((line.tax_amount.amount for line in self.lines), Decimal("0"))
        return Money(total, self.currency)

    @property
    def total_amount(self) -> Money:
        """Calculate order total."""
        total = sum((line.line_total.amount for line in self.lines), Decimal("0"))
        return Money(total, self.currency)

    @property
    def is_fully_delivered(self) -> bool:
        """Check if order is fully delivered."""
        return all(line.is_fully_delivered for line in self.lines)

    def add_line(self, line: OrderLine) -> None:
        """Add a line to the order."""
        if self.status != OrderStatus.DRAFT:
            raise ValueError("Can only modify draft orders")
        self.lines.append(line)
        self._add_event("SalesOrderUpdated", {"order_id": self.id})

    def remove_line(self, line_id: str) -> None:
        """Remove a line from the order."""
        if self.status != OrderStatus.DRAFT:
            raise ValueError("Can only modify draft orders")
        self.lines = [line for line in self.lines if line.id != line_id]
        self._add_event("SalesOrderUpdated", {"order_id": self.id})

    def confirm(self) -> None:
        """Confirm the order."""
        if self.status != OrderStatus.DRAFT:
            raise ValueError("Can only confirm draft orders")
        if not self.lines:
            raise ValueError("Cannot confirm order without lines")
        self.status = OrderStatus.CONFIRMED
        self.confirmed_at = datetime.now()
        self._add_event("SalesOrderConfirmed", {"order_id": self.id})

    def start_processing(self) -> None:
        """Start processing the order."""
        if self.status != OrderStatus.CONFIRMED:
            raise ValueError("Can only process confirmed orders")
        self.status = OrderStatus.PROCESSING
        self._add_event("SalesOrderProcessing", {"order_id": self.id})

    def ship(self, shipping_info: ShippingInfo) -> None:
        """Mark order as shipped."""
        if self.status != OrderStatus.PROCESSING:
            raise ValueError("Can only ship orders that are being processed")
        self.status = OrderStatus.SHIPPED
        self.shipping_info = shipping_info
        self.shipped_at = datetime.now()
        self._add_event("SalesOrderShipped", {"order_id": self.id})

    def deliver(self) -> None:
        """Mark order as delivered."""
        if self.status != OrderStatus.SHIPPED:
            raise ValueError("Can only deliver shipped orders")
        self.status = OrderStatus.DELIVERED
        self.delivered_at = datetime.now()
        self._add_event("SalesOrderDelivered", {"order_id": self.id})

    def cancel(self, reason: str | None = None) -> None:
        """Cancel the order."""
        if self.status in (OrderStatus.DELIVERED, OrderStatus.CANCELLED):
            raise ValueError(f"Cannot cancel {self.status.value.lower()} order")
        self.status = OrderStatus.CANCELLED
        self.cancelled_at = datetime.now()
        self._add_event(
            "SalesOrderCancelled", {"order_id": self.id, "reason": reason or ""}
        )
