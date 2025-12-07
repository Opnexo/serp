"""
FastAPI routes for Invoicing module.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status

from serp_invoicing.application.dto import (
    InvoiceBalanceDTO,
    InvoiceCreateDTO,
    InvoiceDTO,
    InvoiceListDTO,
    InvoiceSummaryDTO,
    InvoiceUpdateDTO,
    PaymentCreateDTO,
    PaymentDTO,
    PaymentListDTO,
)
from serp_invoicing.application.services import InvoiceService, PaymentService
from serp_invoicing.infrastructure.repositories import (
    InMemoryInvoiceRepository,
    InMemoryPaymentRepository,
)

# Create router
router = APIRouter(prefix="/api/invoicing", tags=["Invoicing"])

# Repository singletons (in production, use dependency injection)
_invoice_repo = InMemoryInvoiceRepository()
_payment_repo = InMemoryPaymentRepository()


# Dependency injection
def get_invoice_service() -> InvoiceService:
    """Get Invoice service."""
    return InvoiceService(_invoice_repo)


def get_payment_service() -> PaymentService:
    """Get Payment service."""
    return PaymentService(_payment_repo, _invoice_repo)


# ===== INVOICE ROUTES =====


@router.post(
    "/invoices",
    response_model=InvoiceDTO,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new invoice",
)
async def create_invoice(
    dto: InvoiceCreateDTO,
    service: InvoiceService = Depends(get_invoice_service),
) -> InvoiceDTO:
    """Create a new invoice with line items."""
    try:
        return await service.create_invoice(dto)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get(
    "/invoices",
    response_model=InvoiceListDTO,
    summary="List invoices",
)
async def list_invoices(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status: str | None = Query(None, regex="^(DRAFT|SENT|PAID|OVERDUE|CANCELLED)$"),
    partner_id: str | None = None,
    service: InvoiceService = Depends(get_invoice_service),
) -> InvoiceListDTO:
    """List invoices with optional filters."""
    return await service.list_invoices(
        skip=skip, limit=limit, status=status, partner_id=partner_id
    )


@router.get(
    "/invoices/summary",
    response_model=InvoiceSummaryDTO,
    summary="Get invoice summary statistics",
)
async def get_invoice_summary(
    currency: str = Query("USD", regex="^[A-Z]{3}$"),
    service: InvoiceService = Depends(get_invoice_service),
) -> InvoiceSummaryDTO:
    """Get summary statistics for invoices."""
    return await service.get_invoice_summary(currency=currency)


@router.get(
    "/invoices/{invoice_id}",
    response_model=InvoiceDTO,
    summary="Get invoice by ID",
)
async def get_invoice(
    invoice_id: str,
    service: InvoiceService = Depends(get_invoice_service),
) -> InvoiceDTO:
    """Get invoice details by ID."""
    invoice = await service.get_invoice(invoice_id)
    if not invoice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Invoice {invoice_id} not found",
        )
    return invoice


@router.get(
    "/invoices/number/{invoice_number}",
    response_model=InvoiceDTO,
    summary="Get invoice by number",
)
async def get_invoice_by_number(
    invoice_number: str,
    service: InvoiceService = Depends(get_invoice_service),
) -> InvoiceDTO:
    """Get invoice by invoice number."""
    invoice = await service.get_invoice_by_number(invoice_number)
    if not invoice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Invoice {invoice_number} not found",
        )
    return invoice


@router.put(
    "/invoices/{invoice_id}",
    response_model=InvoiceDTO,
    summary="Update invoice",
)
async def update_invoice(
    invoice_id: str,
    dto: InvoiceUpdateDTO,
    service: InvoiceService = Depends(get_invoice_service),
) -> InvoiceDTO:
    """Update a draft invoice."""
    try:
        invoice = await service.update_invoice(invoice_id, dto)
        if not invoice:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Invoice {invoice_id} not found",
            )
        return invoice
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post(
    "/invoices/{invoice_id}/send",
    response_model=InvoiceDTO,
    summary="Mark invoice as sent",
)
async def send_invoice(
    invoice_id: str,
    service: InvoiceService = Depends(get_invoice_service),
) -> InvoiceDTO:
    """Mark an invoice as sent to customer."""
    try:
        invoice = await service.send_invoice(invoice_id)
        if not invoice:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Invoice {invoice_id} not found",
            )
        return invoice
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post(
    "/invoices/{invoice_id}/cancel",
    response_model=InvoiceDTO,
    summary="Cancel invoice",
)
async def cancel_invoice(
    invoice_id: str,
    service: InvoiceService = Depends(get_invoice_service),
) -> InvoiceDTO:
    """Cancel an invoice."""
    try:
        invoice = await service.cancel_invoice(invoice_id)
        if not invoice:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Invoice {invoice_id} not found",
            )
        return invoice
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.delete(
    "/invoices/{invoice_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete invoice",
)
async def delete_invoice(
    invoice_id: str,
    service: InvoiceService = Depends(get_invoice_service),
) -> None:
    """Delete a draft invoice."""
    try:
        deleted = await service.delete_invoice(invoice_id)
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Invoice {invoice_id} not found",
            )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get(
    "/partners/{partner_id}/invoices",
    response_model=InvoiceListDTO,
    summary="Get partner invoices",
)
async def get_partner_invoices(
    partner_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    service: InvoiceService = Depends(get_invoice_service),
) -> InvoiceListDTO:
    """Get all invoices for a specific partner."""
    return await service.get_partner_invoices(partner_id, skip=skip, limit=limit)


@router.get(
    "/invoices/{invoice_id}/balance",
    response_model=InvoiceBalanceDTO,
    summary="Get invoice balance",
)
async def get_invoice_balance(
    invoice_id: str,
    service: PaymentService = Depends(get_payment_service),
) -> InvoiceBalanceDTO:
    """Get balance information for an invoice."""
    balance = await service.get_invoice_balance(invoice_id)
    if not balance:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Invoice {invoice_id} not found",
        )
    return balance


# ===== PAYMENT ROUTES =====


@router.post(
    "/payments",
    response_model=PaymentDTO,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new payment",
)
async def create_payment(
    dto: PaymentCreateDTO,
    service: PaymentService = Depends(get_payment_service),
) -> PaymentDTO:
    """Record a payment for an invoice."""
    try:
        return await service.create_payment(dto)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get(
    "/payments",
    response_model=PaymentListDTO,
    summary="List payments",
)
async def list_payments(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    service: PaymentService = Depends(get_payment_service),
) -> PaymentListDTO:
    """List all payments."""
    return await service.list_payments(skip=skip, limit=limit)


@router.get(
    "/payments/{payment_id}",
    response_model=PaymentDTO,
    summary="Get payment by ID",
)
async def get_payment(
    payment_id: str,
    service: PaymentService = Depends(get_payment_service),
) -> PaymentDTO:
    """Get payment details by ID."""
    payment = await service.get_payment(payment_id)
    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Payment {payment_id} not found",
        )
    return payment


@router.get(
    "/invoices/{invoice_id}/payments",
    response_model=PaymentListDTO,
    summary="Get invoice payments",
)
async def get_invoice_payments(
    invoice_id: str,
    service: PaymentService = Depends(get_payment_service),
) -> PaymentListDTO:
    """Get all payments for an invoice."""
    return await service.get_invoice_payments(invoice_id)


@router.delete(
    "/payments/{payment_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete payment",
)
async def delete_payment(
    payment_id: str,
    service: PaymentService = Depends(get_payment_service),
) -> None:
    """Delete a payment."""
    deleted = await service.delete_payment(payment_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Payment {payment_id} not found",
        )


# ===== MAINTENANCE ROUTES =====


@router.post(
    "/maintenance/update-overdue",
    response_model=list[InvoiceDTO],
    summary="Update overdue invoices",
)
async def update_overdue_invoices(
    service: InvoiceService = Depends(get_invoice_service),
) -> list[InvoiceDTO]:
    """Update status of overdue invoices (maintenance endpoint)."""
    return await service.update_overdue_invoices()
