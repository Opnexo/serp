"""
Application services for Sales module.
"""

from decimal import Decimal

from serp_crm.domain.value_objects import Money

from serp_sales.application.dto import (
    OrderLineDTO,
    QuoteCreateDTO,
    QuoteDTO,
    QuoteLineDTO,
    QuoteListDTO,
    QuoteSummaryDTO,
    QuoteUpdateDTO,
    SalesOrderCreateDTO,
    SalesOrderDTO,
    SalesOrderListDTO,
    SalesOrderSummaryDTO,
    SalesOrderUpdateDTO,
    ShippingInfoDTO,
)
from serp_sales.domain.entities import OrderLine, Quote, QuoteLine, SalesOrder
from serp_sales.domain.repositories import IQuoteRepository, ISalesOrderRepository
from serp_sales.domain.services import (
    OrderNumberGenerator,
    QuoteNumberGenerator,
    QuoteToOrderConverter,
)
from serp_sales.domain.value_objects import (
    OrderStatus,
    QuoteStatus,
    ShippingInfo,
)


class QuoteService:
    """Application service for Quote operations."""

    def __init__(
        self,
        quote_repository: IQuoteRepository,
        quote_number_generator: QuoteNumberGenerator,
    ):
        self._repository = quote_repository
        self._number_generator = quote_number_generator

    def create_quote(self, dto: QuoteCreateDTO) -> QuoteDTO:
        """Create a new quote."""
        # Generate quote number
        quote_number = self._number_generator.generate_quote_number()

        # Convert lines
        lines = [
            QuoteLine(
                product_code=line.product_code,
                description=line.description,
                quantity=line.quantity,
                unit_price=Money(line.unit_price, dto.currency),
                discount_percent=line.discount_percent,
                tax_rate=line.tax_rate,
            )
            for line in dto.lines
        ]

        # Create quote
        quote = Quote(
            quote_number=quote_number,
            partner_id=dto.partner_id,
            quote_date=dto.quote_date,
            valid_until=dto.valid_until,
            currency=dto.currency,
            lines=lines,
            notes=dto.notes,
        )

        self._repository.save(quote)
        return self._to_dto(quote)

    def get_quote(self, quote_id: str) -> QuoteDTO:
        """Get a quote by ID."""
        quote = self._repository.get_by_id(quote_id)
        if not quote:
            raise ValueError(f"Quote {quote_id} not found")
        return self._to_dto(quote)

    def list_quotes(
        self, skip: int = 0, limit: int = 100, status: str | None = None
    ) -> QuoteListDTO:
        """List quotes with pagination."""
        quotes = self._repository.list_all(skip, limit)

        # Filter by status if provided
        if status:
            quotes = [q for q in quotes if q.status == status]

        return QuoteListDTO(
            items=[self._to_dto(q) for q in quotes],
            total=len(quotes),
            skip=skip,
            limit=limit,
        )

    def get_partner_quotes(self, partner_id: str) -> list[QuoteDTO]:
        """Get all quotes for a partner."""
        quotes = self._repository.get_by_partner(partner_id)
        return [self._to_dto(q) for q in quotes]

    def update_quote(self, quote_id: str, dto: QuoteUpdateDTO) -> QuoteDTO:
        """Update a quote (draft only)."""
        quote = self._repository.get_by_id(quote_id)
        if not quote:
            raise ValueError(f"Quote {quote_id} not found")

        if quote.status != QuoteStatus.DRAFT:
            raise ValueError("Can only update draft quotes")

        # Update lines if provided
        if dto.lines is not None:
            quote.lines = [
                QuoteLine(
                    product_code=line.product_code,
                    description=line.description,
                    quantity=line.quantity,
                    unit_price=Money(line.unit_price, quote.currency),
                    discount_percent=line.discount_percent,
                    tax_rate=line.tax_rate,
                )
                for line in dto.lines
            ]

        # Update other fields
        if dto.notes is not None:
            quote.notes = dto.notes
        if dto.valid_until is not None:
            quote.valid_until = dto.valid_until

        self._repository.save(quote)
        return self._to_dto(quote)

    def send_quote(self, quote_id: str) -> QuoteDTO:
        """Send quote to customer."""
        quote = self._repository.get_by_id(quote_id)
        if not quote:
            raise ValueError(f"Quote {quote_id} not found")

        quote.send()
        self._repository.save(quote)
        return self._to_dto(quote)

    def accept_quote(self, quote_id: str) -> QuoteDTO:
        """Accept a quote."""
        quote = self._repository.get_by_id(quote_id)
        if not quote:
            raise ValueError(f"Quote {quote_id} not found")

        quote.accept()
        self._repository.save(quote)
        return self._to_dto(quote)

    def reject_quote(self, quote_id: str, reason: str | None = None) -> QuoteDTO:
        """Reject a quote."""
        quote = self._repository.get_by_id(quote_id)
        if not quote:
            raise ValueError(f"Quote {quote_id} not found")

        quote.reject(reason)
        self._repository.save(quote)
        return self._to_dto(quote)

    def delete_quote(self, quote_id: str) -> None:
        """Delete a quote (draft only)."""
        quote = self._repository.get_by_id(quote_id)
        if not quote:
            raise ValueError(f"Quote {quote_id} not found")

        if quote.status != QuoteStatus.DRAFT:
            raise ValueError("Can only delete draft quotes")

        self._repository.delete(quote_id)

    def get_quote_summary(self) -> QuoteSummaryDTO:
        """Get quote summary statistics."""
        quotes = self._repository.list_all()

        total_count = len(quotes)
        draft_count = sum(1 for q in quotes if q.status == QuoteStatus.DRAFT)
        sent_count = sum(1 for q in quotes if q.status == QuoteStatus.SENT)
        accepted_count = sum(1 for q in quotes if q.status == QuoteStatus.ACCEPTED)
        rejected_count = sum(1 for q in quotes if q.status == QuoteStatus.REJECTED)
        expired_count = sum(1 for q in quotes if q.status == QuoteStatus.EXPIRED)

        total_amount = sum((q.total_amount.amount for q in quotes), Decimal("0"))
        accepted_amount = sum(
            (q.total_amount.amount for q in quotes if q.status == QuoteStatus.ACCEPTED),
            Decimal("0"),
        )

        return QuoteSummaryDTO(
            total_count=total_count,
            draft_count=draft_count,
            sent_count=sent_count,
            accepted_count=accepted_count,
            rejected_count=rejected_count,
            expired_count=expired_count,
            total_amount=total_amount,
            accepted_amount=accepted_amount,
        )

    def _to_dto(self, quote: Quote) -> QuoteDTO:
        """Convert quote entity to DTO."""
        return QuoteDTO(
            id=quote.id,
            quote_number=str(quote.quote_number),
            partner_id=quote.partner_id,
            quote_date=quote.quote_date,
            valid_until=quote.valid_until,
            currency=quote.currency,
            lines=[self._line_to_dto(line) for line in quote.lines],
            status=quote.status.value,
            notes=quote.notes,
            subtotal=quote.subtotal.amount,
            discount_amount=quote.discount_amount.amount,
            total_before_tax=quote.total_before_tax.amount,
            tax_amount=quote.tax_amount.amount,
            total_amount=quote.total_amount.amount,
            is_expired=quote.is_expired,
            sent_at=quote.sent_at.isoformat() if quote.sent_at else None,
            accepted_at=quote.accepted_at.isoformat() if quote.accepted_at else None,
            rejected_at=quote.rejected_at.isoformat() if quote.rejected_at else None,
            created_at=quote.created_at.isoformat(),
            updated_at=quote.updated_at.isoformat(),
        )

    def _line_to_dto(self, line: QuoteLine) -> QuoteLineDTO:
        """Convert quote line to DTO."""
        return QuoteLineDTO(
            id=line.id,
            product_code=line.product_code,
            description=line.description,
            quantity=line.quantity,
            unit_price=line.unit_price.amount,
            discount_percent=line.discount.percent,
            tax_rate=line.tax_rate.rate,
            line_subtotal=line.line_subtotal.amount,
            discount_amount=line.discount_amount.amount,
            line_total_before_tax=line.line_total_before_tax.amount,
            tax_amount=line.tax_amount.amount,
            line_total=line.line_total.amount,
        )


class SalesOrderService:
    """Application service for Sales Order operations."""

    def __init__(
        self,
        order_repository: ISalesOrderRepository,
        quote_repository: IQuoteRepository,
        order_number_generator: OrderNumberGenerator,
        quote_to_order_converter: QuoteToOrderConverter,
    ):
        self._repository = order_repository
        self._quote_repository = quote_repository
        self._number_generator = order_number_generator
        self._converter = quote_to_order_converter

    def create_order(self, dto: SalesOrderCreateDTO) -> SalesOrderDTO:
        """Create a new sales order."""
        # Generate order number
        order_number = self._number_generator.generate_order_number()

        # Convert lines
        lines = [
            OrderLine(
                product_code=line.product_code,
                description=line.description,
                quantity=line.quantity,
                unit_price=Money(line.unit_price, dto.currency),
                discount_percent=line.discount_percent,
                tax_rate=line.tax_rate,
            )
            for line in dto.lines
        ]

        # Create order
        order = SalesOrder(
            order_number=order_number,
            partner_id=dto.partner_id,
            order_date=dto.order_date,
            currency=dto.currency,
            lines=lines,
            requested_delivery_date=dto.requested_delivery_date,
            notes=dto.notes,
        )

        self._repository.save(order)
        return self._to_dto(order)

    def create_order_from_quote(self, quote_id: str) -> SalesOrderDTO:
        """Create a sales order from an accepted quote."""
        quote = self._quote_repository.get_by_id(quote_id)
        if not quote:
            raise ValueError(f"Quote {quote_id} not found")

        order = self._converter.convert_quote_to_order(quote)
        self._repository.save(order)
        return self._to_dto(order)

    def get_order(self, order_id: str) -> SalesOrderDTO:
        """Get an order by ID."""
        order = self._repository.get_by_id(order_id)
        if not order:
            raise ValueError(f"Order {order_id} not found")
        return self._to_dto(order)

    def list_orders(
        self, skip: int = 0, limit: int = 100, status: str | None = None
    ) -> SalesOrderListDTO:
        """List orders with pagination."""
        orders = self._repository.list_all(skip, limit)

        # Filter by status if provided
        if status:
            orders = [o for o in orders if o.status == status]

        return SalesOrderListDTO(
            items=[self._to_dto(o) for o in orders],
            total=len(orders),
            skip=skip,
            limit=limit,
        )

    def get_partner_orders(self, partner_id: str) -> list[SalesOrderDTO]:
        """Get all orders for a partner."""
        orders = self._repository.get_by_partner(partner_id)
        return [self._to_dto(o) for o in orders]

    def update_order(self, order_id: str, dto: SalesOrderUpdateDTO) -> SalesOrderDTO:
        """Update an order (draft only)."""
        order = self._repository.get_by_id(order_id)
        if not order:
            raise ValueError(f"Order {order_id} not found")

        if order.status != OrderStatus.DRAFT:
            raise ValueError("Can only update draft orders")

        # Update lines if provided
        if dto.lines is not None:
            order.lines = [
                OrderLine(
                    product_code=line.product_code,
                    description=line.description,
                    quantity=line.quantity,
                    unit_price=Money(line.unit_price, order.currency),
                    discount_percent=line.discount_percent,
                    tax_rate=line.tax_rate,
                )
                for line in dto.lines
            ]

        # Update other fields
        if dto.notes is not None:
            order.notes = dto.notes
        if dto.requested_delivery_date is not None:
            order.requested_delivery_date = dto.requested_delivery_date

        self._repository.save(order)
        return self._to_dto(order)

    def confirm_order(self, order_id: str) -> SalesOrderDTO:
        """Confirm an order."""
        order = self._repository.get_by_id(order_id)
        if not order:
            raise ValueError(f"Order {order_id} not found")

        order.confirm()
        self._repository.save(order)
        return self._to_dto(order)

    def start_processing(self, order_id: str) -> SalesOrderDTO:
        """Start processing an order."""
        order = self._repository.get_by_id(order_id)
        if not order:
            raise ValueError(f"Order {order_id} not found")

        order.start_processing()
        self._repository.save(order)
        return self._to_dto(order)

    def ship_order(
        self, order_id: str, shipping_info: ShippingInfoDTO
    ) -> SalesOrderDTO:
        """Ship an order."""
        order = self._repository.get_by_id(order_id)
        if not order:
            raise ValueError(f"Order {order_id} not found")

        ship_info = ShippingInfo(
            carrier=shipping_info.carrier,
            tracking_number=shipping_info.tracking_number,
            shipping_method=shipping_info.shipping_method,
        )

        order.ship(ship_info)
        self._repository.save(order)
        return self._to_dto(order)

    def deliver_order(self, order_id: str) -> SalesOrderDTO:
        """Deliver an order."""
        order = self._repository.get_by_id(order_id)
        if not order:
            raise ValueError(f"Order {order_id} not found")

        order.deliver()
        self._repository.save(order)
        return self._to_dto(order)

    def cancel_order(self, order_id: str, reason: str | None = None) -> SalesOrderDTO:
        """Cancel an order."""
        order = self._repository.get_by_id(order_id)
        if not order:
            raise ValueError(f"Order {order_id} not found")

        order.cancel(reason)
        self._repository.save(order)
        return self._to_dto(order)

    def delete_order(self, order_id: str) -> None:
        """Delete an order (draft only)."""
        order = self._repository.get_by_id(order_id)
        if not order:
            raise ValueError(f"Order {order_id} not found")

        if order.status != OrderStatus.DRAFT:
            raise ValueError("Can only delete draft orders")

        self._repository.delete(order_id)

    def get_order_summary(self) -> SalesOrderSummaryDTO:
        """Get order summary statistics."""
        orders = self._repository.list_all()

        total_count = len(orders)
        draft_count = sum(1 for o in orders if o.status == OrderStatus.DRAFT)
        confirmed_count = sum(1 for o in orders if o.status == OrderStatus.CONFIRMED)
        processing_count = sum(1 for o in orders if o.status == OrderStatus.PROCESSING)
        shipped_count = sum(1 for o in orders if o.status == OrderStatus.SHIPPED)
        delivered_count = sum(1 for o in orders if o.status == OrderStatus.DELIVERED)
        cancelled_count = sum(1 for o in orders if o.status == OrderStatus.CANCELLED)

        total_amount = sum((o.total_amount.amount for o in orders), Decimal("0"))
        delivered_amount = sum(
            (
                o.total_amount.amount
                for o in orders
                if o.status == OrderStatus.DELIVERED
            ),
            Decimal("0"),
        )

        return SalesOrderSummaryDTO(
            total_count=total_count,
            draft_count=draft_count,
            confirmed_count=confirmed_count,
            processing_count=processing_count,
            shipped_count=shipped_count,
            delivered_count=delivered_count,
            cancelled_count=cancelled_count,
            total_amount=total_amount,
            delivered_amount=delivered_amount,
        )

    def _to_dto(self, order: SalesOrder) -> SalesOrderDTO:
        """Convert order entity to DTO."""
        return SalesOrderDTO(
            id=order.id,
            order_number=str(order.order_number),
            partner_id=order.partner_id,
            order_date=order.order_date,
            currency=order.currency,
            lines=[self._line_to_dto(line) for line in order.lines],
            status=order.status.value,
            quote_id=order.quote_id,
            requested_delivery_date=order.requested_delivery_date,
            shipping_info=(
                ShippingInfoDTO(
                    carrier=order.shipping_info.carrier,
                    tracking_number=order.shipping_info.tracking_number,
                    shipping_method=order.shipping_info.shipping_method,
                )
                if order.shipping_info
                else None
            ),
            notes=order.notes,
            subtotal=order.subtotal.amount,
            discount_amount=order.discount_amount.amount,
            total_before_tax=order.total_before_tax.amount,
            tax_amount=order.tax_amount.amount,
            total_amount=order.total_amount.amount,
            is_fully_delivered=order.is_fully_delivered,
            confirmed_at=order.confirmed_at.isoformat() if order.confirmed_at else None,
            shipped_at=order.shipped_at.isoformat() if order.shipped_at else None,
            delivered_at=order.delivered_at.isoformat() if order.delivered_at else None,
            cancelled_at=order.cancelled_at.isoformat() if order.cancelled_at else None,
            created_at=order.created_at.isoformat(),
            updated_at=order.updated_at.isoformat(),
        )

    def _line_to_dto(self, line: OrderLine) -> OrderLineDTO:
        """Convert order line to DTO."""
        return OrderLineDTO(
            id=line.id,
            product_code=line.product_code,
            description=line.description,
            quantity=line.quantity,
            unit_price=line.unit_price.amount,
            discount_percent=line.discount.percent,
            tax_rate=line.tax_rate.rate,
            quantity_delivered=line.quantity_delivered,
            line_subtotal=line.line_subtotal.amount,
            discount_amount=line.discount_amount.amount,
            line_total_before_tax=line.line_total_before_tax.amount,
            tax_amount=line.tax_amount.amount,
            line_total=line.line_total.amount,
            is_fully_delivered=line.is_fully_delivered,
        )
