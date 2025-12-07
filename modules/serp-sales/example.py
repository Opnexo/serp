"""
Example usage of the Sales module.

This script demonstrates:
- Creating quotes with line items
- Sending and accepting quotes
- Converting quotes to sales orders
- Order fulfillment workflow
- Shipping and delivery tracking
"""

from datetime import date, timedelta
from decimal import Decimal

from serp_sales.application.dto import (
    OrderLineDTO,
    QuoteCreateDTO,
    QuoteLineDTO,
    SalesOrderCreateDTO,
    ShippingInfoDTO,
)
from serp_sales.application.services import QuoteService, SalesOrderService
from serp_sales.domain.services import (
    ExpiredQuoteService,
    OrderNumberGenerator,
    QuoteNumberGenerator,
    QuoteToOrderConverter,
)
from serp_sales.infrastructure.repositories import (
    InMemoryQuoteRepository,
    InMemorySalesOrderRepository,
)


def main():
    """Run example workflow."""
    # Initialize repositories
    quote_repo = InMemoryQuoteRepository()
    order_repo = InMemorySalesOrderRepository()

    # Initialize domain services
    quote_number_gen = QuoteNumberGenerator(quote_repo)
    order_number_gen = OrderNumberGenerator(order_repo)
    quote_to_order = QuoteToOrderConverter(quote_repo, order_repo, order_number_gen)
    expired_quote_service = ExpiredQuoteService(quote_repo)

    # Initialize application services
    quote_service = QuoteService(quote_repo, quote_number_gen)
    order_service = SalesOrderService(
        order_repo, quote_repo, order_number_gen, quote_to_order
    )

    print("=" * 60)
    print("SALES MODULE - EXAMPLE WORKFLOW")
    print("=" * 60)

    # 1. Create quote
    print("\n1. Creating sales quote...")
    quote_dto = QuoteCreateDTO(
        partner_id="partner-123",
        quote_date=date.today(),
        valid_until=date.today() + timedelta(days=30),
        currency="USD",
        lines=[
            QuoteLineDTO(
                product_code="PRD-001",
                description="Enterprise Software License",
                quantity=Decimal("10"),
                unit_price=Decimal("499.00"),
                discount_percent=Decimal("15"),  # 15% volume discount
                tax_rate=Decimal("0.08"),
            ),
            QuoteLineDTO(
                product_code="SVC-001",
                description="Implementation Services",
                quantity=Decimal("40"),  # hours
                unit_price=Decimal("150.00"),
                tax_rate=Decimal("0.08"),
            ),
        ],
        notes="Annual license with implementation support",
    )

    quote = quote_service.create_quote(quote_dto)
    print(f"  ✓ Quote created: {quote.quote_number}")
    print(f"    Subtotal: ${quote.subtotal:.2f}")
    print(f"    Discount: -${quote.discount_amount:.2f}")
    print(f"    Tax: ${quote.tax_amount:.2f}")
    print(f"    Total: ${quote.total_amount:.2f}")
    print(f"    Valid until: {quote.valid_until}")

    # 2. Send quote
    print(f"\n2. Sending quote {quote.quote_number}...")
    sent_quote = quote_service.send_quote(quote.id)
    print(f"  ✓ Quote sent on {sent_quote.sent_at}")

    # 3. Accept quote
    print(f"\n3. Customer accepts quote {quote.quote_number}...")
    accepted_quote = quote_service.accept_quote(quote.id)
    print(f"  ✓ Quote accepted on {accepted_quote.accepted_at}")

    # 4. Convert quote to sales order
    print("\n4. Converting quote to sales order...")
    order = order_service.create_order_from_quote(quote.id)
    print(f"  ✓ Sales order created: {order.order_number}")
    print(f"    From quote: {quote.quote_number}")
    print(f"    Total: ${order.total_amount:.2f}")
    print(f"    Status: {order.status}")

    # 5. Confirm order
    print(f"\n5. Confirming order {order.order_number}...")
    confirmed = order_service.confirm_order(order.id)
    print(f"  ✓ Order confirmed on {confirmed.confirmed_at}")

    # 6. Start processing
    print("\n6. Starting order processing...")
    processing = order_service.start_processing(order.id)
    print(f"  ✓ Order status: {processing.status}")

    # 7. Ship order
    print("\n7. Shipping order...")
    shipping_info = ShippingInfoDTO(
        carrier="FedEx",
        tracking_number="1234567890",
        shipping_method="Express",
    )
    shipped = order_service.ship_order(order.id, shipping_info)
    print(f"  ✓ Order shipped on {shipped.shipped_at}")
    print(f"    Carrier: {shipped.shipping_info.carrier}")
    print(f"    Tracking: {shipped.shipping_info.tracking_number}")

    # 8. Deliver order
    print("\n8. Marking order as delivered...")
    delivered = order_service.deliver_order(order.id)
    print(f"  ✓ Order delivered on {delivered.delivered_at}")

    # 9. Create standalone order (without quote)
    print("\n9. Creating standalone sales order...")
    standalone_dto = SalesOrderCreateDTO(
        partner_id="partner-456",
        order_date=date.today(),
        currency="USD",
        lines=[
            OrderLineDTO(
                product_code="PRD-002",
                description="Professional Services",
                quantity=Decimal("20"),
                unit_price=Decimal("200.00"),
                discount_percent=Decimal("10"),
                tax_rate=Decimal("0.10"),
            )
        ],
        requested_delivery_date=date.today() + timedelta(days=7),
    )

    standalone_order = order_service.create_order(standalone_dto)
    print(f"  ✓ Order created: {standalone_order.order_number}")
    print(f"    Total: ${standalone_order.total_amount:.2f}")

    # 10. Create and reject another quote
    print("\n10. Creating and rejecting a quote...")
    quote2_dto = QuoteCreateDTO(
        partner_id="partner-789",
        quote_date=date.today(),
        valid_until=date.today() + timedelta(days=15),
        currency="USD",
        lines=[
            QuoteLineDTO(
                product_code="PRD-003",
                description="Basic Plan",
                quantity=Decimal("5"),
                unit_price=Decimal("99.00"),
                tax_rate=Decimal("0.08"),
            )
        ],
    )

    quote2 = quote_service.create_quote(quote2_dto)
    quote_service.send_quote(quote2.id)
    rejected = quote_service.reject_quote(quote2.id, "Budget constraints")
    print(f"  ✓ Quote {rejected.quote_number} rejected")

    # 11. Get summaries
    print("\n11. Getting summary statistics...")
    quote_summary = quote_service.get_quote_summary()
    print("  Quotes:")
    print(f"    Total: {quote_summary.total_count}")
    print(f"    Sent: {quote_summary.sent_count}")
    print(f"    Accepted: {quote_summary.accepted_count}")
    print(f"    Rejected: {quote_summary.rejected_count}")
    print(f"    Total value: ${quote_summary.total_amount:.2f}")
    print(f"    Accepted value: ${quote_summary.accepted_amount:.2f}")

    order_summary = order_service.get_order_summary()
    print("  Orders:")
    print(f"    Total: {order_summary.total_count}")
    print(f"    Confirmed: {order_summary.confirmed_count}")
    print(f"    Delivered: {order_summary.delivered_count}")
    print(f"    Total value: ${order_summary.total_amount:.2f}")
    print(f"    Delivered value: ${order_summary.delivered_amount:.2f}")

    # 12. List all orders
    print("\n12. Listing all orders...")
    orders_list = order_service.list_orders(skip=0, limit=10)
    for ord in orders_list.items:
        print(f"    - {ord.order_number}: ${ord.total_amount:.2f} [{ord.status}]")

    print("\n" + "=" * 60)
    print("EXAMPLE COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    main()
