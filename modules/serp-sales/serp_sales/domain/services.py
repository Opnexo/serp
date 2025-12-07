"""
Domain services for Sales module.
"""

from datetime import date

from serp_sales.domain.entities import OrderLine, Quote, SalesOrder
from serp_sales.domain.repositories import IQuoteRepository, ISalesOrderRepository
from serp_sales.domain.value_objects import OrderNumber, QuoteNumber, QuoteStatus


class QuoteNumberGenerator:
    """Generate sequential quote numbers."""

    def __init__(self, quote_repository: IQuoteRepository):
        self._repository = quote_repository

    def generate_quote_number(
        self, year: int | None = None, prefix: str = "QT"
    ) -> QuoteNumber:
        """Generate next quote number for the given year."""
        if year is None:
            year = date.today().year

        sequence = self._repository.get_next_sequence_number(year)
        return QuoteNumber.generate(year, sequence, prefix)


class OrderNumberGenerator:
    """Generate sequential order numbers."""

    def __init__(self, order_repository: ISalesOrderRepository):
        self._repository = order_repository

    def generate_order_number(
        self, year: int | None = None, prefix: str = "SO"
    ) -> OrderNumber:
        """Generate next order number for the given year."""
        if year is None:
            year = date.today().year

        sequence = self._repository.get_next_sequence_number(year)
        return OrderNumber.generate(year, sequence, prefix)


class QuoteToOrderConverter:
    """Convert quotes to sales orders."""

    def __init__(
        self,
        quote_repository: IQuoteRepository,
        order_repository: ISalesOrderRepository,
        order_number_generator: OrderNumberGenerator,
    ):
        self._quote_repository = quote_repository
        self._order_repository = order_repository
        self._order_number_generator = order_number_generator

    def convert_quote_to_order(self, quote: Quote) -> SalesOrder:
        """Convert an accepted quote to a sales order."""
        if quote.status != QuoteStatus.ACCEPTED:
            raise ValueError("Can only convert accepted quotes")

        # Check if order already exists
        existing_order = self._order_repository.get_by_quote(quote.id)
        if existing_order:
            raise ValueError(f"Order already exists for quote {quote.quote_number}")

        # Generate order number
        order_number = self._order_number_generator.generate_order_number()

        # Convert quote lines to order lines
        order_lines = [
            OrderLine(
                product_code=line.product_code,
                description=line.description,
                quantity=line.quantity,
                unit_price=line.unit_price,
                discount_percent=line.discount.percent,
                tax_rate=line.tax_rate.rate,
            )
            for line in quote.lines
        ]

        # Create sales order
        order = SalesOrder(
            order_number=order_number,
            partner_id=quote.partner_id,
            order_date=date.today(),
            currency=quote.currency,
            lines=order_lines,
            quote_id=quote.id,
            notes=f"Created from quote {quote.quote_number}",
        )

        return order


class ExpiredQuoteService:
    """Service to handle expired quotes."""

    def __init__(self, quote_repository: IQuoteRepository):
        self._repository = quote_repository

    def mark_expired_quotes(self) -> int:
        """Mark all expired quotes and return count."""
        quotes = self._repository.list_all()
        expired_count = 0

        for quote in quotes:
            if quote.is_expired and quote.status == QuoteStatus.SENT:
                quote.mark_expired()
                self._repository.save(quote)
                expired_count += 1

        return expired_count
