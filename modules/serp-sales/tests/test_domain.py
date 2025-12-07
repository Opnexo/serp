"""
Tests for Quote and SalesOrder entities.
"""

from datetime import date, timedelta
from decimal import Decimal

import pytest
from serp_crm.domain.value_objects import Money

from serp_sales.domain.entities import OrderLine, Quote, QuoteLine, SalesOrder
from serp_sales.domain.value_objects import (
    OrderNumber,
    OrderStatus,
    QuoteNumber,
    QuoteStatus,
    ShippingInfo,
)


def test_create_quote_line():
    """Test creating a quote line item."""
    line = QuoteLine(
        product_code="PRD-001",
        description="Software License",
        quantity=Decimal("5"),
        unit_price=Money(Decimal("299.00"), "USD"),
        discount_percent=Decimal("10"),
        tax_rate=Decimal("0.08"),
    )

    assert line.product_code == "PRD-001"
    assert line.line_subtotal.amount == Decimal("1495.00")  # 5 × 299
    assert line.discount_amount.amount == Decimal("149.50")  # 10% of 1495
    assert line.line_total_before_tax.amount == Decimal("1345.50")  # 1495 - 149.50
    assert line.tax_amount.amount == Decimal("107.64")  # 8% of 1345.50
    assert line.line_total.amount == Decimal("1453.14")  # 1345.50 + 107.64


def test_create_quote():
    """Test creating a quote."""
    line = QuoteLine(
        product_code="PRD-001",
        description="Consulting Services",
        quantity=Decimal("10"),
        unit_price=Money(Decimal("150.00"), "USD"),
        tax_rate=Decimal("0.10"),
    )

    quote = Quote(
        quote_number=QuoteNumber("QT-2025-0001"),
        partner_id="partner-123",
        quote_date=date.today(),
        valid_until=date.today() + timedelta(days=30),
        currency="USD",
        lines=[line],
    )

    assert str(quote.quote_number) == "QT-2025-0001"
    assert quote.status == QuoteStatus.DRAFT
    assert quote.subtotal.amount == Decimal("1500.00")
    assert quote.tax_amount.amount == Decimal("150.00")
    assert quote.total_amount.amount == Decimal("1650.00")


def test_quote_status_transitions():
    """Test quote status transitions."""
    line = QuoteLine(
        product_code="PRD-001",
        description="Service",
        quantity=Decimal("1"),
        unit_price=Money(Decimal("500.00"), "USD"),
    )

    quote = Quote(
        quote_number=QuoteNumber("QT-2025-0002"),
        partner_id="partner-456",
        quote_date=date.today(),
        valid_until=date.today() + timedelta(days=30),
        currency="USD",
        lines=[line],
    )

    # Initial status
    assert quote.status == QuoteStatus.DRAFT

    # Send quote
    quote.send()
    assert quote.status == QuoteStatus.SENT
    assert quote.sent_at is not None

    # Accept quote
    quote.accept()
    assert quote.status == QuoteStatus.ACCEPTED
    assert quote.accepted_at is not None


def test_cannot_modify_sent_quote():
    """Test that sent quotes cannot be modified."""
    line = QuoteLine(
        product_code="PRD-001",
        description="Service",
        quantity=Decimal("1"),
        unit_price=Money(Decimal("500.00"), "USD"),
    )

    quote = Quote(
        quote_number=QuoteNumber("QT-2025-0003"),
        partner_id="partner-789",
        quote_date=date.today(),
        valid_until=date.today() + timedelta(days=30),
        currency="USD",
        lines=[line],
    )

    quote.send()

    # Cannot add lines to sent quote
    new_line = QuoteLine(
        product_code="PRD-002",
        description="Another service",
        quantity=Decimal("1"),
        unit_price=Money(Decimal("100.00"), "USD"),
    )

    with pytest.raises(ValueError, match="draft"):
        quote.add_line(new_line)


def test_quote_expiration():
    """Test quote expiration detection."""
    line = QuoteLine(
        product_code="PRD-001",
        description="Service",
        quantity=Decimal("1"),
        unit_price=Money(Decimal("500.00"), "USD"),
    )

    # Create quote with past valid_until date
    quote = Quote(
        quote_number=QuoteNumber("QT-2025-0004"),
        partner_id="partner-abc",
        quote_date=date.today() - timedelta(days=60),
        valid_until=date.today() - timedelta(days=30),
        currency="USD",
        lines=[line],
        status=QuoteStatus.SENT,
    )

    assert quote.is_expired is True


def test_create_sales_order():
    """Test creating a sales order."""
    line = OrderLine(
        product_code="PRD-001",
        description="Product",
        quantity=Decimal("3"),
        unit_price=Money(Decimal("200.00"), "USD"),
        tax_rate=Decimal("0.10"),
    )

    order = SalesOrder(
        order_number=OrderNumber("SO-2025-0001"),
        partner_id="partner-123",
        order_date=date.today(),
        currency="USD",
        lines=[line],
    )

    assert str(order.order_number) == "SO-2025-0001"
    assert order.status == OrderStatus.DRAFT
    assert order.subtotal.amount == Decimal("600.00")
    assert order.tax_amount.amount == Decimal("60.00")
    assert order.total_amount.amount == Decimal("660.00")


def test_order_fulfillment_workflow():
    """Test complete order fulfillment workflow."""
    line = OrderLine(
        product_code="PRD-001",
        description="Product",
        quantity=Decimal("5"),
        unit_price=Money(Decimal("100.00"), "USD"),
    )

    order = SalesOrder(
        order_number=OrderNumber("SO-2025-0002"),
        partner_id="partner-456",
        order_date=date.today(),
        currency="USD",
        lines=[line],
    )

    # Confirm order
    order.confirm()
    assert order.status == OrderStatus.CONFIRMED
    assert order.confirmed_at is not None

    # Start processing
    order.start_processing()
    assert order.status == OrderStatus.PROCESSING

    # Ship order
    shipping = ShippingInfo(
        carrier="FedEx", tracking_number="123456789", shipping_method="Ground"
    )
    order.ship(shipping)
    assert order.status == OrderStatus.SHIPPED
    assert order.shipped_at is not None
    assert order.shipping_info is not None

    # Deliver order
    order.deliver()
    assert order.status == OrderStatus.DELIVERED
    assert order.delivered_at is not None


def test_order_with_discount():
    """Test order with line-item discounts."""
    line = OrderLine(
        product_code="PRD-001",
        description="Product",
        quantity=Decimal("10"),
        unit_price=Money(Decimal("100.00"), "USD"),
        discount_percent=Decimal("20"),  # 20% discount
        tax_rate=Decimal("0.10"),
    )

    order = SalesOrder(
        order_number=OrderNumber("SO-2025-0003"),
        partner_id="partner-789",
        order_date=date.today(),
        currency="USD",
        lines=[line],
    )

    # Subtotal: 10 × 100 = 1000
    assert order.subtotal.amount == Decimal("1000.00")
    # Discount: 20% of 1000 = 200
    assert order.discount_amount.amount == Decimal("200.00")
    # After discount: 1000 - 200 = 800
    assert order.total_before_tax.amount == Decimal("800.00")
    # Tax: 10% of 800 = 80
    assert order.tax_amount.amount == Decimal("80.00")
    # Total: 800 + 80 = 880
    assert order.total_amount.amount == Decimal("880.00")


def test_cannot_cancel_delivered_order():
    """Test that delivered orders cannot be cancelled."""
    line = OrderLine(
        product_code="PRD-001",
        description="Product",
        quantity=Decimal("1"),
        unit_price=Money(Decimal("100.00"), "USD"),
    )

    order = SalesOrder(
        order_number=OrderNumber("SO-2025-0004"),
        partner_id="partner-abc",
        order_date=date.today(),
        currency="USD",
        lines=[line],
    )

    order.confirm()
    order.start_processing()
    order.ship(ShippingInfo(carrier="UPS"))
    order.deliver()

    with pytest.raises(ValueError, match="Cannot cancel"):
        order.cancel()
