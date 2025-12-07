"""Data Transfer Objects for Procurement module."""

from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, Field

from serp_procurement.domain.value_objects import (
    DeliveryTerms,
    PurchaseOrderState,
    QualityStatus,
    ReceiptStatus,
    RFQState,
)

# RFQ DTOs


class RFQLineDTO(BaseModel):
    """RFQ line data."""

    product_id: str
    product_code: str
    description: str
    quantity: Decimal = Field(gt=0)
    uom_id: str
    required_delivery_date: date | None = None
    notes: str | None = None


class RFQLineWithQuotesDTO(RFQLineDTO):
    """RFQ line with supplier quotes."""

    id: str
    supplier_quotes: dict[str, Decimal]  # supplier_id -> quoted_price


class RFQCreateDTO(BaseModel):
    """Create RFQ request."""

    title: str = Field(max_length=200)
    requester_id: str
    request_date: date
    validity_date: date
    supplier_ids: list[str] = Field(min_length=1)
    lines: list[RFQLineDTO] = Field(min_length=1)
    notes: str | None = None


class RFQUpdateDTO(BaseModel):
    """Update RFQ request."""

    title: str | None = Field(default=None, max_length=200)
    validity_date: date | None = None
    notes: str | None = None


class RFQQuoteDTO(BaseModel):
    """Add supplier quote to RFQ line."""

    line_id: str
    supplier_id: str
    quoted_price: Decimal = Field(gt=0)
    currency: str = Field(max_length=3)


class RFQDTO(BaseModel):
    """RFQ response."""

    id: str
    rfq_number: str
    title: str
    requester_id: str
    request_date: date
    validity_date: date
    supplier_ids: list[str]
    lines: list[RFQLineWithQuotesDTO]
    state: RFQState
    notes: str | None
    sent_date: datetime | None
    created_at: datetime
    updated_at: datetime | None


# Purchase Order DTOs


class PurchaseOrderLineDTO(BaseModel):
    """Purchase order line data."""

    product_id: str
    product_code: str
    description: str
    quantity: Decimal = Field(gt=0)
    uom_id: str
    unit_price: Decimal = Field(gt=0)
    currency: str = Field(max_length=3)
    discount_percent: Decimal = Field(default=Decimal("0"), ge=0, le=100)
    expected_delivery_date: date | None = None
    notes: str | None = None
    rfq_line_id: str | None = None


class PurchaseOrderLineResponseDTO(PurchaseOrderLineDTO):
    """Purchase order line with tracking."""

    id: str
    ordered_quantity: Decimal
    received_quantity: Decimal
    pending_quantity: Decimal
    is_fully_received: bool
    subtotal: Decimal
    discount_amount: Decimal
    total: Decimal


class PurchaseOrderCreateDTO(BaseModel):
    """Create purchase order request."""

    supplier_id: str
    order_date: date
    expected_delivery_date: date | None = None
    payment_terms_code: str = Field(default="NET30")
    payment_terms_days: int = Field(default=30, ge=0)
    delivery_terms: DeliveryTerms = DeliveryTerms.FOB
    lines: list[PurchaseOrderLineDTO] = Field(min_length=1)
    requester_id: str | None = None
    delivery_address: str | None = None
    notes: str | None = None
    rfq_id: str | None = None


class PurchaseOrderUpdateDTO(BaseModel):
    """Update purchase order request."""

    expected_delivery_date: date | None = None
    delivery_address: str | None = None
    notes: str | None = None


class PurchaseOrderDTO(BaseModel):
    """Purchase order response."""

    id: str
    po_number: str
    supplier_id: str
    order_date: date
    expected_delivery_date: date | None
    payment_terms: str
    delivery_terms: DeliveryTerms
    lines: list[PurchaseOrderLineResponseDTO]
    state: PurchaseOrderState
    receipt_status: ReceiptStatus
    requester_id: str | None
    delivery_address: str | None
    notes: str | None
    rfq_id: str | None
    confirmed_date: datetime | None
    cancelled_date: datetime | None
    subtotal: Decimal
    total: Decimal
    currency: str
    created_at: datetime
    updated_at: datetime | None


class ConvertRFQToPODTO(BaseModel):
    """Convert RFQ to Purchase Order."""

    rfq_id: str
    supplier_id: str
    order_date: date
    expected_delivery_date: date | None = None
    payment_terms_code: str = Field(default="NET30")
    payment_terms_days: int = Field(default=30, ge=0)
    delivery_terms: DeliveryTerms = DeliveryTerms.FOB
    delivery_address: str | None = None
    notes: str | None = None


# Goods Receipt Note DTOs


class GRNLineDTO(BaseModel):
    """Goods receipt note line data."""

    po_line_id: str
    product_id: str
    product_code: str
    received_quantity: Decimal = Field(gt=0)
    uom_id: str
    notes: str | None = None


class GRNLineResponseDTO(GRNLineDTO):
    """Goods receipt note line with quality."""

    id: str
    quality_status: QualityStatus
    rejected_quantity: Decimal
    accepted_quantity: Decimal


class GoodsReceiptNoteCreateDTO(BaseModel):
    """Create goods receipt note request."""

    purchase_order_id: str
    receipt_date: date
    received_by: str
    lines: list[GRNLineDTO] = Field(min_length=1)
    carrier: str | None = None
    tracking_number: str | None = None
    notes: str | None = None


class GoodsReceiptNoteDTO(BaseModel):
    """Goods receipt note response."""

    id: str
    grn_number: str
    purchase_order_id: str
    receipt_date: date
    received_by: str
    lines: list[GRNLineResponseDTO]
    carrier: str | None
    tracking_number: str | None
    notes: str | None
    overall_quality_status: QualityStatus
    created_at: datetime
    updated_at: datetime | None


class QualityCheckDTO(BaseModel):
    """Quality check result."""

    line_id: str
    passed: bool
    rejected_quantity: Decimal = Field(default=Decimal("0"), ge=0)
    notes: str | None = None


# Purchase Agreement DTOs


class AgreementLineDTO(BaseModel):
    """Purchase agreement line data."""

    product_id: str
    product_code: str
    description: str
    committed_quantity: Decimal = Field(gt=0)
    uom_id: str
    unit_price: Decimal = Field(gt=0)
    currency: str = Field(max_length=3)
    discount_percent: Decimal = Field(default=Decimal("0"), ge=0, le=100)


class AgreementLineResponseDTO(AgreementLineDTO):
    """Purchase agreement line with usage."""

    id: str
    called_off_quantity: Decimal
    remaining_quantity: Decimal


class PurchaseAgreementCreateDTO(BaseModel):
    """Create purchase agreement request."""

    supplier_id: str
    valid_from: date
    valid_to: date
    payment_terms_code: str = Field(default="NET30")
    payment_terms_days: int = Field(default=30, ge=0)
    lines: list[AgreementLineDTO] = Field(min_length=1)
    notes: str | None = None


class PurchaseAgreementUpdateDTO(BaseModel):
    """Update purchase agreement request."""

    valid_to: date | None = None
    notes: str | None = None


class PurchaseAgreementDTO(BaseModel):
    """Purchase agreement response."""

    id: str
    agreement_number: str
    supplier_id: str
    valid_from: date
    valid_to: date
    payment_terms: str
    lines: list[AgreementLineResponseDTO]
    is_active: bool
    notes: str | None
    created_at: datetime
    updated_at: datetime | None
