"""
REST API routes for Sales module.
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status

from serp_sales.application.dto import (
    QuoteCreateDTO,
    QuoteDTO,
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

router = APIRouter(prefix="/api/sales", tags=["sales"])

# Dependency injection (simplified - in production use proper DI container)
_quote_repo = InMemoryQuoteRepository()
_order_repo = InMemorySalesOrderRepository()
_quote_number_gen = QuoteNumberGenerator(_quote_repo)
_order_number_gen = OrderNumberGenerator(_order_repo)
_quote_to_order = QuoteToOrderConverter(_quote_repo, _order_repo, _order_number_gen)


def get_quote_service() -> QuoteService:
    """Get quote service instance."""
    return QuoteService(_quote_repo, _quote_number_gen)


def get_order_service() -> SalesOrderService:
    """Get sales order service instance."""
    return SalesOrderService(
        _order_repo, _quote_repo, _order_number_gen, _quote_to_order
    )


# Quote endpoints


@router.post("/quotes", response_model=QuoteDTO, status_code=status.HTTP_201_CREATED)
def create_quote(
    dto: QuoteCreateDTO,
    service: Annotated[QuoteService, Depends(get_quote_service)],
) -> QuoteDTO:
    """Create a new quote."""
    try:
        return service.create_quote(dto)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/quotes", response_model=QuoteListDTO)
def list_quotes(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status_filter: str | None = Query(None, alias="status"),
    service: Annotated[QuoteService, Depends(get_quote_service)] = None,
) -> QuoteListDTO:
    """List all quotes."""
    return service.list_quotes(skip, limit, status_filter)


@router.get("/quotes/{quote_id}", response_model=QuoteDTO)
def get_quote(
    quote_id: str,
    service: Annotated[QuoteService, Depends(get_quote_service)],
) -> QuoteDTO:
    """Get a quote by ID."""
    try:
        return service.get_quote(quote_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("/partners/{partner_id}/quotes", response_model=list[QuoteDTO])
def get_partner_quotes(
    partner_id: str,
    service: Annotated[QuoteService, Depends(get_quote_service)],
) -> list[QuoteDTO]:
    """Get all quotes for a partner."""
    return service.get_partner_quotes(partner_id)


@router.put("/quotes/{quote_id}", response_model=QuoteDTO)
def update_quote(
    quote_id: str,
    dto: QuoteUpdateDTO,
    service: Annotated[QuoteService, Depends(get_quote_service)],
) -> QuoteDTO:
    """Update a quote (draft only)."""
    try:
        return service.update_quote(quote_id, dto)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/quotes/{quote_id}/send", response_model=QuoteDTO)
def send_quote(
    quote_id: str,
    service: Annotated[QuoteService, Depends(get_quote_service)],
) -> QuoteDTO:
    """Send quote to customer."""
    try:
        return service.send_quote(quote_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/quotes/{quote_id}/accept", response_model=QuoteDTO)
def accept_quote(
    quote_id: str,
    service: Annotated[QuoteService, Depends(get_quote_service)],
) -> QuoteDTO:
    """Accept a quote."""
    try:
        return service.accept_quote(quote_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/quotes/{quote_id}/reject", response_model=QuoteDTO)
def reject_quote(
    quote_id: str,
    reason: str | None = None,
    service: Annotated[QuoteService, Depends(get_quote_service)] = None,
) -> QuoteDTO:
    """Reject a quote."""
    try:
        return service.reject_quote(quote_id, reason)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.delete("/quotes/{quote_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_quote(
    quote_id: str,
    service: Annotated[QuoteService, Depends(get_quote_service)],
) -> None:
    """Delete a quote (draft only)."""
    try:
        service.delete_quote(quote_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/quotes/summary/statistics", response_model=QuoteSummaryDTO)
def get_quote_summary(
    service: Annotated[QuoteService, Depends(get_quote_service)],
) -> QuoteSummaryDTO:
    """Get quote summary statistics."""
    return service.get_quote_summary()


# Sales Order endpoints


@router.post(
    "/orders", response_model=SalesOrderDTO, status_code=status.HTTP_201_CREATED
)
def create_order(
    dto: SalesOrderCreateDTO,
    service: Annotated[SalesOrderService, Depends(get_order_service)],
) -> SalesOrderDTO:
    """Create a new sales order."""
    try:
        return service.create_order(dto)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post(
    "/orders/from-quote/{quote_id}",
    response_model=SalesOrderDTO,
    status_code=status.HTTP_201_CREATED,
)
def create_order_from_quote(
    quote_id: str,
    service: Annotated[SalesOrderService, Depends(get_order_service)],
) -> SalesOrderDTO:
    """Create a sales order from an accepted quote."""
    try:
        return service.create_order_from_quote(quote_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/orders", response_model=SalesOrderListDTO)
def list_orders(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status_filter: str | None = Query(None, alias="status"),
    service: Annotated[SalesOrderService, Depends(get_order_service)] = None,
) -> SalesOrderListDTO:
    """List all orders."""
    return service.list_orders(skip, limit, status_filter)


@router.get("/orders/{order_id}", response_model=SalesOrderDTO)
def get_order(
    order_id: str,
    service: Annotated[SalesOrderService, Depends(get_order_service)],
) -> SalesOrderDTO:
    """Get an order by ID."""
    try:
        return service.get_order(order_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("/partners/{partner_id}/orders", response_model=list[SalesOrderDTO])
def get_partner_orders(
    partner_id: str,
    service: Annotated[SalesOrderService, Depends(get_order_service)],
) -> list[SalesOrderDTO]:
    """Get all orders for a partner."""
    return service.get_partner_orders(partner_id)


@router.put("/orders/{order_id}", response_model=SalesOrderDTO)
def update_order(
    order_id: str,
    dto: SalesOrderUpdateDTO,
    service: Annotated[SalesOrderService, Depends(get_order_service)],
) -> SalesOrderDTO:
    """Update an order (draft only)."""
    try:
        return service.update_order(order_id, dto)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/orders/{order_id}/confirm", response_model=SalesOrderDTO)
def confirm_order(
    order_id: str,
    service: Annotated[SalesOrderService, Depends(get_order_service)],
) -> SalesOrderDTO:
    """Confirm an order."""
    try:
        return service.confirm_order(order_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/orders/{order_id}/process", response_model=SalesOrderDTO)
def start_processing_order(
    order_id: str,
    service: Annotated[SalesOrderService, Depends(get_order_service)],
) -> SalesOrderDTO:
    """Start processing an order."""
    try:
        return service.start_processing(order_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/orders/{order_id}/ship", response_model=SalesOrderDTO)
def ship_order(
    order_id: str,
    shipping_info: ShippingInfoDTO,
    service: Annotated[SalesOrderService, Depends(get_order_service)],
) -> SalesOrderDTO:
    """Ship an order."""
    try:
        return service.ship_order(order_id, shipping_info)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/orders/{order_id}/deliver", response_model=SalesOrderDTO)
def deliver_order(
    order_id: str,
    service: Annotated[SalesOrderService, Depends(get_order_service)],
) -> SalesOrderDTO:
    """Deliver an order."""
    try:
        return service.deliver_order(order_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/orders/{order_id}/cancel", response_model=SalesOrderDTO)
def cancel_order(
    order_id: str,
    reason: str | None = None,
    service: Annotated[SalesOrderService, Depends(get_order_service)] = None,
) -> SalesOrderDTO:
    """Cancel an order."""
    try:
        return service.cancel_order(order_id, reason)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.delete("/orders/{order_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_order(
    order_id: str,
    service: Annotated[SalesOrderService, Depends(get_order_service)],
) -> None:
    """Delete an order (draft only)."""
    try:
        service.delete_order(order_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/orders/summary/statistics", response_model=SalesOrderSummaryDTO)
def get_order_summary(
    service: Annotated[SalesOrderService, Depends(get_order_service)],
) -> SalesOrderSummaryDTO:
    """Get order summary statistics."""
    return service.get_order_summary()


# Maintenance endpoints


@router.post("/maintenance/expire-quotes", status_code=status.HTTP_200_OK)
def expire_quotes() -> dict[str, int]:
    """Mark expired quotes (maintenance task)."""
    service = ExpiredQuoteService(_quote_repo)
    count = service.mark_expired_quotes()
    return {"expired_count": count}
