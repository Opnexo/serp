"""
Data Transfer Objects for Sales module.
"""

from datetime import date
from decimal import Decimal

from pydantic import BaseModel, Field

# Quote DTOs


class QuoteLineDTO(BaseModel):
    """Quote line DTO."""

    id: str | None = None
    product_code: str
    description: str
    quantity: Decimal = Field(gt=0)
    unit_price: Decimal = Field(ge=0)
    discount_percent: Decimal = Field(default=Decimal("0"), ge=0, le=100)
    tax_rate: Decimal = Field(default=Decimal("0"), ge=0, le=1)
    line_subtotal: Decimal | None = None
    discount_amount: Decimal | None = None
    line_total_before_tax: Decimal | None = None
    tax_amount: Decimal | None = None
    line_total: Decimal | None = None


class QuoteCreateDTO(BaseModel):
    """Create quote DTO."""

    partner_id: str
    quote_date: date
    valid_until: date
    currency: str = "USD"
    lines: list[QuoteLineDTO]
    notes: str | None = None


class QuoteUpdateDTO(BaseModel):
    """Update quote DTO."""

    lines: list[QuoteLineDTO] | None = None
    notes: str | None = None
    valid_until: date | None = None


class QuoteDTO(BaseModel):
    """Quote DTO."""

    id: str
    quote_number: str
    partner_id: str
    quote_date: date
    valid_until: date
    currency: str
    lines: list[QuoteLineDTO]
    status: str
    notes: str | None = None
    subtotal: Decimal
    discount_amount: Decimal
    total_before_tax: Decimal
    tax_amount: Decimal
    total_amount: Decimal
    is_expired: bool
    sent_at: str | None = None
    accepted_at: str | None = None
    rejected_at: str | None = None
    created_at: str
    updated_at: str


class QuoteListDTO(BaseModel):
    """Quote list response DTO."""

    items: list[QuoteDTO]
    total: int
    skip: int
    limit: int


class QuoteSummaryDTO(BaseModel):
    """Quote summary statistics DTO."""

    total_count: int
    draft_count: int
    sent_count: int
    accepted_count: int
    rejected_count: int
    expired_count: int
    total_amount: Decimal
    accepted_amount: Decimal


# Sales Order DTOs


class OrderLineDTO(BaseModel):
    """Order line DTO."""

    id: str | None = None
    product_code: str
    description: str
    quantity: Decimal = Field(gt=0)
    unit_price: Decimal = Field(ge=0)
    discount_percent: Decimal = Field(default=Decimal("0"), ge=0, le=100)
    tax_rate: Decimal = Field(default=Decimal("0"), ge=0, le=1)
    quantity_delivered: Decimal = Field(default=Decimal("0"), ge=0)
    line_subtotal: Decimal | None = None
    discount_amount: Decimal | None = None
    line_total_before_tax: Decimal | None = None
    tax_amount: Decimal | None = None
    line_total: Decimal | None = None
    is_fully_delivered: bool | None = None


class ShippingInfoDTO(BaseModel):
    """Shipping information DTO."""

    carrier: str
    tracking_number: str | None = None
    shipping_method: str | None = None


class SalesOrderCreateDTO(BaseModel):
    """Create sales order DTO."""

    partner_id: str
    order_date: date
    currency: str = "USD"
    lines: list[OrderLineDTO]
    requested_delivery_date: date | None = None
    notes: str | None = None


class SalesOrderUpdateDTO(BaseModel):
    """Update sales order DTO."""

    lines: list[OrderLineDTO] | None = None
    notes: str | None = None
    requested_delivery_date: date | None = None


class SalesOrderDTO(BaseModel):
    """Sales order DTO."""

    id: str
    order_number: str
    partner_id: str
    order_date: date
    currency: str
    lines: list[OrderLineDTO]
    status: str
    quote_id: str | None = None
    requested_delivery_date: date | None = None
    shipping_info: ShippingInfoDTO | None = None
    notes: str | None = None
    subtotal: Decimal
    discount_amount: Decimal
    total_before_tax: Decimal
    tax_amount: Decimal
    total_amount: Decimal
    is_fully_delivered: bool
    confirmed_at: str | None = None
    shipped_at: str | None = None
    delivered_at: str | None = None
    cancelled_at: str | None = None
    created_at: str
    updated_at: str


class SalesOrderListDTO(BaseModel):
    """Sales order list response DTO."""

    items: list[SalesOrderDTO]
    total: int
    skip: int
    limit: int


class SalesOrderSummaryDTO(BaseModel):
    """Sales order summary statistics DTO."""

    total_count: int
    draft_count: int
    confirmed_count: int
    processing_count: int
    shipped_count: int
    delivered_count: int
    cancelled_count: int
    total_amount: Decimal
    delivered_amount: Decimal
