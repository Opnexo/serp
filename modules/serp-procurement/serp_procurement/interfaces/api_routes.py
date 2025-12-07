"""REST API routes for Procurement module."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from serp_procurement.application import (
    RFQDTO,
    ConvertRFQToPODTO,
    GoodsReceiptNoteCreateDTO,
    GoodsReceiptNoteDTO,
    GoodsReceiptService,
    PurchaseAgreementCreateDTO,
    PurchaseAgreementDTO,
    PurchaseAgreementService,
    PurchaseAgreementUpdateDTO,
    PurchaseOrderCreateDTO,
    PurchaseOrderDTO,
    PurchaseOrderService,
    PurchaseOrderUpdateDTO,
    QualityCheckDTO,
    RFQCreateDTO,
    RFQQuoteDTO,
    RFQService,
    RFQUpdateDTO,
)

# Service dependencies (placeholders - injected by serp-shell)
RFQServiceDep = Annotated["RFQService", Depends(lambda: None)]
POServiceDep = Annotated["PurchaseOrderService", Depends(lambda: None)]
GRNServiceDep = Annotated["GoodsReceiptService", Depends(lambda: None)]
AgreementServiceDep = Annotated["PurchaseAgreementService", Depends(lambda: None)]

router = APIRouter(prefix="/api/v1/procurement", tags=["procurement"])


# RFQ Routes
@router.post("/rfqs", response_model=RFQDTO, status_code=status.HTTP_201_CREATED)
async def create_rfq(dto: RFQCreateDTO, service: RFQServiceDep) -> RFQDTO:
    """Create a new RFQ."""
    try:
        return service.create_rfq(dto)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/rfqs/{rfq_id}", response_model=RFQDTO)
async def get_rfq(rfq_id: str, service: RFQServiceDep) -> RFQDTO:
    """Get RFQ by ID."""
    rfq = service.get_rfq(rfq_id)
    if not rfq:
        raise HTTPException(status_code=404, detail="RFQ not found")
    return rfq


@router.put("/rfqs/{rfq_id}", response_model=RFQDTO)
async def update_rfq(rfq_id: str, dto: RFQUpdateDTO, service: RFQServiceDep) -> RFQDTO:
    """Update RFQ."""
    try:
        return service.update_rfq(rfq_id, dto)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/rfqs/{rfq_id}/send", response_model=RFQDTO)
async def send_rfq(rfq_id: str, service: RFQServiceDep) -> RFQDTO:
    """Send RFQ to suppliers."""
    try:
        return service.send_rfq(rfq_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/rfqs/{rfq_id}/quote", response_model=RFQDTO)
async def add_quote(rfq_id: str, dto: RFQQuoteDTO, service: RFQServiceDep) -> RFQDTO:
    """Add supplier quote to RFQ."""
    try:
        return service.add_quote(rfq_id, dto)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/rfqs/{rfq_id}/accept", response_model=RFQDTO)
async def accept_rfq(rfq_id: str, service: RFQServiceDep) -> RFQDTO:
    """Accept RFQ."""
    try:
        return service.accept_rfq(rfq_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/rfqs/{rfq_id}/cancel", response_model=RFQDTO)
async def cancel_rfq(rfq_id: str, service: RFQServiceDep) -> RFQDTO:
    """Cancel RFQ."""
    try:
        return service.cancel_rfq(rfq_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/rfqs", response_model=list[RFQDTO])
async def list_rfqs(
    state: str | None = None, service: RFQServiceDep = None
) -> list[RFQDTO]:
    """List RFQs."""
    from serp_procurement.domain.value_objects import RFQState

    rfq_state = RFQState(state) if state else None
    return service.list_rfqs(rfq_state)


# Purchase Order Routes
@router.post(
    "/pos", response_model=PurchaseOrderDTO, status_code=status.HTTP_201_CREATED
)
async def create_purchase_order(
    dto: PurchaseOrderCreateDTO, service: POServiceDep
) -> PurchaseOrderDTO:
    """Create a new purchase order."""
    try:
        return service.create_purchase_order(dto)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/pos/convert", response_model=PurchaseOrderDTO)
async def convert_rfq_to_po(
    dto: ConvertRFQToPODTO, service: POServiceDep
) -> PurchaseOrderDTO:
    """Convert RFQ to Purchase Order."""
    try:
        return service.convert_rfq_to_po(dto)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/pos/{po_id}", response_model=PurchaseOrderDTO)
async def get_purchase_order(po_id: str, service: POServiceDep) -> PurchaseOrderDTO:
    """Get purchase order by ID."""
    po = service.get_purchase_order(po_id)
    if not po:
        raise HTTPException(status_code=404, detail="Purchase order not found")
    return po


@router.put("/pos/{po_id}", response_model=PurchaseOrderDTO)
async def update_purchase_order(
    po_id: str, dto: PurchaseOrderUpdateDTO, service: POServiceDep
) -> PurchaseOrderDTO:
    """Update purchase order."""
    try:
        return service.update_purchase_order(po_id, dto)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/pos/{po_id}/confirm", response_model=PurchaseOrderDTO)
async def confirm_purchase_order(po_id: str, service: POServiceDep) -> PurchaseOrderDTO:
    """Confirm purchase order."""
    try:
        return service.confirm_purchase_order(po_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/pos/{po_id}/cancel", response_model=PurchaseOrderDTO)
async def cancel_purchase_order(po_id: str, service: POServiceDep) -> PurchaseOrderDTO:
    """Cancel purchase order."""
    try:
        return service.cancel_purchase_order(po_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/pos", response_model=list[PurchaseOrderDTO])
async def list_purchase_orders(
    supplier_id: str | None = None,
    state: str | None = None,
    service: POServiceDep = None,
) -> list[PurchaseOrderDTO]:
    """List purchase orders."""
    from serp_procurement.domain.value_objects import PurchaseOrderState

    po_state = PurchaseOrderState(state) if state else None
    return service.list_purchase_orders(supplier_id, po_state)


# Goods Receipt Note Routes
@router.post(
    "/grns", response_model=GoodsReceiptNoteDTO, status_code=status.HTTP_201_CREATED
)
async def create_receipt(
    dto: GoodsReceiptNoteCreateDTO, service: GRNServiceDep
) -> GoodsReceiptNoteDTO:
    """Create goods receipt note."""
    try:
        return service.create_receipt(dto)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/grns/{grn_id}", response_model=GoodsReceiptNoteDTO)
async def get_receipt(grn_id: str, service: GRNServiceDep) -> GoodsReceiptNoteDTO:
    """Get goods receipt note by ID."""
    grn = service.get_receipt(grn_id)
    if not grn:
        raise HTTPException(status_code=404, detail="GRN not found")
    return grn


@router.post("/grns/{grn_id}/quality-check", response_model=GoodsReceiptNoteDTO)
async def quality_check(
    grn_id: str, checks: list[QualityCheckDTO], service: GRNServiceDep
) -> GoodsReceiptNoteDTO:
    """Perform quality check on receipt."""
    try:
        return service.quality_check(grn_id, checks)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/grns", response_model=list[GoodsReceiptNoteDTO])
async def list_receipts(
    purchase_order_id: str | None = None, service: GRNServiceDep = None
) -> list[GoodsReceiptNoteDTO]:
    """List goods receipt notes."""
    return service.list_receipts(purchase_order_id)


# Purchase Agreement Routes
@router.post(
    "/agreements",
    response_model=PurchaseAgreementDTO,
    status_code=status.HTTP_201_CREATED,
)
async def create_agreement(
    dto: PurchaseAgreementCreateDTO, service: AgreementServiceDep
) -> PurchaseAgreementDTO:
    """Create purchase agreement."""
    try:
        return service.create_agreement(dto)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/agreements/{agreement_id}", response_model=PurchaseAgreementDTO)
async def get_agreement(
    agreement_id: str, service: AgreementServiceDep
) -> PurchaseAgreementDTO:
    """Get purchase agreement by ID."""
    agreement = service.get_agreement(agreement_id)
    if not agreement:
        raise HTTPException(status_code=404, detail="Agreement not found")
    return agreement


@router.put("/agreements/{agreement_id}", response_model=PurchaseAgreementDTO)
async def update_agreement(
    agreement_id: str,
    dto: PurchaseAgreementUpdateDTO,
    service: AgreementServiceDep,
) -> PurchaseAgreementDTO:
    """Update purchase agreement."""
    try:
        return service.update_agreement(agreement_id, dto)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/agreements/{agreement_id}/activate", response_model=PurchaseAgreementDTO)
async def activate_agreement(
    agreement_id: str, service: AgreementServiceDep
) -> PurchaseAgreementDTO:
    """Activate purchase agreement."""
    try:
        return service.activate_agreement(agreement_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post(
    "/agreements/{agreement_id}/deactivate", response_model=PurchaseAgreementDTO
)
async def deactivate_agreement(
    agreement_id: str, service: AgreementServiceDep
) -> PurchaseAgreementDTO:
    """Deactivate purchase agreement."""
    try:
        return service.deactivate_agreement(agreement_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/agreements", response_model=list[PurchaseAgreementDTO])
async def list_agreements(
    supplier_id: str | None = None,
    active_only: bool = False,
    service: AgreementServiceDep = None,
) -> list[PurchaseAgreementDTO]:
    """List purchase agreements."""
    return service.list_agreements(supplier_id, active_only)
