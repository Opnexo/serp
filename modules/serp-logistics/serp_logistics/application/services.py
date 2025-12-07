"""Application services for logistics module."""

from uuid import UUID

from serp_core.domain import DomainEventPublisher

from ..domain import (
    Address,
    Carrier,
    DeliveryRoute,
    ICarrierRepository,
    IDeliveryRouteRepository,
    IPackingOperationRepository,
    IPickingOperationRepository,
    IReturnAuthorizationRepository,
    IShipmentRepository,
    PackageDimensions,
    PackingOperation,
    PickingOperation,
    ReturnAuthorization,
    Shipment,
    Weight,
)
from .dto import (
    RMADTO,
    AddressDTO,
    CarrierCreateDTO,
    CarrierDTO,
    CarrierUpdateDTO,
    PackageCreateDTO,
    PackageItemAddDTO,
    PackingCreateDTO,
    PackingDTO,
    PickingAssignDTO,
    PickingCreateDTO,
    PickingDTO,
    PickingPickDTO,
    RMAApproveDTO,
    RMACreateDTO,
    RMAProcessDTO,
    RMARejectDTO,
    RMAShipDTO,
    RouteCompleteStopDTO,
    RouteCreateDTO,
    RouteDTO,
    RouteStopCreateDTO,
    ShipmentConfirmDTO,
    ShipmentCreateDTO,
    ShipmentDTO,
    ShipmentUpdateStatusDTO,
)


def _address_from_dto(dto: AddressDTO) -> Address:
    """Convert address DTO to value object."""
    return Address(
        name=dto.name,
        street1=dto.street1,
        street2=dto.street2,
        city=dto.city,
        state=dto.state,
        postal_code=dto.postal_code,
        country=dto.country,
        phone=dto.phone,
        email=dto.email,
        is_residential=dto.is_residential,
    )


def _address_to_dto(address: Address) -> AddressDTO:
    """Convert address value object to DTO."""
    return AddressDTO(
        name=address.name,
        street1=address.street1,
        street2=address.street2,
        city=address.city,
        state=address.state,
        postal_code=address.postal_code,
        country=address.country,
        phone=address.phone,
        email=address.email,
        is_residential=address.is_residential,
    )


class PickingService:
    """Service for managing picking operations."""

    def __init__(
        self,
        picking_repo: IPickingOperationRepository,
        event_publisher: DomainEventPublisher,
    ) -> None:
        self._picking_repo = picking_repo
        self._event_publisher = event_publisher

    def create_picking(self, dto: PickingCreateDTO) -> PickingDTO:
        """Create new picking operation."""
        picking = PickingOperation.create(
            strategy=dto.strategy,
            source_document_type=dto.source_document_type,
            source_document_id=dto.source_document_id,
        )

        for line_dto in dto.lines:
            picking.add_line(
                product_id=line_dto.product_id,
                product_code=line_dto.product_code,
                product_name=line_dto.product_name,
                quantity=line_dto.quantity,
                source_location_id=line_dto.source_location_id,
            )

        self._picking_repo.add(picking)
        for event in picking.domain_events:
            self._event_publisher.publish(event)
        picking.clear_events()

        return self._to_dto(picking)

    def assign_picker(self, picking_id: UUID, dto: PickingAssignDTO) -> PickingDTO:
        """Assign picker to operation."""
        picking = self._picking_repo.get(picking_id)
        picking.assign(dto.picker_id)
        self._picking_repo.update(picking)

        for event in picking.domain_events:
            self._event_publisher.publish(event)
        picking.clear_events()

        return self._to_dto(picking)

    def start_picking(self, picking_id: UUID) -> PickingDTO:
        """Start picking operation."""
        picking = self._picking_repo.get(picking_id)
        picking.start()
        self._picking_repo.update(picking)

        for event in picking.domain_events:
            self._event_publisher.publish(event)
        picking.clear_events()

        return self._to_dto(picking)

    def pick_line(self, picking_id: UUID, dto: PickingPickDTO) -> PickingDTO:
        """Pick line quantity."""
        picking = self._picking_repo.get(picking_id)
        for line in picking.lines:
            if line.id == dto.line_id:
                line.pick(dto.quantity, dto.lot_serial_id)
                break

        self._picking_repo.update(picking)
        return self._to_dto(picking)

    def complete_picking(self, picking_id: UUID) -> PickingDTO:
        """Complete picking operation."""
        picking = self._picking_repo.get(picking_id)
        picking.complete()
        self._picking_repo.update(picking)

        for event in picking.domain_events:
            self._event_publisher.publish(event)
        picking.clear_events()

        return self._to_dto(picking)

    def cancel_picking(self, picking_id: UUID) -> PickingDTO:
        """Cancel picking operation."""
        picking = self._picking_repo.get(picking_id)
        picking.cancel()
        self._picking_repo.update(picking)

        for event in picking.domain_events:
            self._event_publisher.publish(event)
        picking.clear_events()

        return self._to_dto(picking)

    def get_picking(self, picking_id: UUID) -> PickingDTO:
        """Get picking operation."""
        picking = self._picking_repo.get(picking_id)
        return self._to_dto(picking)

    def _to_dto(self, picking: PickingOperation) -> PickingDTO:
        """Convert picking to DTO."""
        from .dto import PickingLineDTO

        return PickingDTO(
            id=picking.id,
            picking_number=picking.picking_number.value,
            strategy=picking.strategy,
            source_document_type=picking.source_document_type,
            source_document_id=picking.source_document_id,
            lines=[
                PickingLineDTO(
                    id=line.id,
                    product_id=line.product_id,
                    product_code=line.product_code,
                    product_name=line.product_name,
                    quantity_ordered=line.quantity_ordered,
                    quantity_picked=line.quantity_picked,
                    quantity_remaining=line.quantity_remaining,
                    source_location_id=line.source_location_id,
                    lot_serial_id=line.lot_serial_id,
                    is_fully_picked=line.is_fully_picked,
                    quantity=line.quantity_ordered,
                )
                for line in picking.lines
            ],
            assigned_picker_id=picking.assigned_picker_id,
            assigned_at=picking.assigned_at,
            started_at=picking.started_at,
            completed_at=picking.completed_at,
            state=picking.state,
            created_at=picking.created_at,
            updated_at=picking.updated_at,
        )


class PackingService:
    """Service for managing packing operations."""

    def __init__(
        self,
        packing_repo: IPackingOperationRepository,
        event_publisher: DomainEventPublisher,
    ) -> None:
        self._packing_repo = packing_repo
        self._event_publisher = event_publisher

    def create_packing(self, dto: PackingCreateDTO) -> PackingDTO:
        """Create new packing operation."""
        packing = PackingOperation.create(
            picking_operation_id=dto.picking_operation_id,
            packer_id=dto.packer_id,
        )

        self._packing_repo.add(packing)
        for event in packing.domain_events:
            self._event_publisher.publish(event)
        packing.clear_events()

        return self._to_dto(packing)

    def add_package(self, packing_id: UUID, dto: PackageCreateDTO) -> PackingDTO:
        """Add package to packing operation."""
        packing = self._packing_repo.get(packing_id)
        dimensions = PackageDimensions(
            length_cm=dto.length_cm,
            width_cm=dto.width_cm,
            height_cm=dto.height_cm,
        )
        weight = Weight(kg=dto.weight_kg)

        packing.add_package(
            box_type=dto.box_type,
            dimensions=dimensions,
            weight=weight,
        )

        self._packing_repo.update(packing)
        return self._to_dto(packing)

    def add_item_to_package(
        self,
        packing_id: UUID,
        package_id: UUID,
        dto: PackageItemAddDTO,
    ) -> PackingDTO:
        """Add item to package."""
        packing = self._packing_repo.get(packing_id)
        for package in packing.packages:
            if package.id == package_id:
                package.add_item(
                    product_id=dto.product_id,
                    product_code=dto.product_code,
                    product_name=dto.product_name,
                    quantity=dto.quantity,
                    lot_serial_id=dto.lot_serial_id,
                )
                break

        self._packing_repo.update(packing)
        return self._to_dto(packing)

    def start_packing(self, packing_id: UUID) -> PackingDTO:
        """Start packing operation."""
        packing = self._packing_repo.get(packing_id)
        packing.start()
        self._packing_repo.update(packing)

        for event in packing.domain_events:
            self._event_publisher.publish(event)
        packing.clear_events()

        return self._to_dto(packing)

    def complete_packing(self, packing_id: UUID) -> PackingDTO:
        """Complete packing operation."""
        packing = self._packing_repo.get(packing_id)
        packing.complete()
        self._packing_repo.update(packing)

        for event in packing.domain_events:
            self._event_publisher.publish(event)
        packing.clear_events()

        return self._to_dto(packing)

    def mark_shipped(self, packing_id: UUID) -> PackingDTO:
        """Mark packing as shipped."""
        packing = self._packing_repo.get(packing_id)
        packing.mark_shipped()
        self._packing_repo.update(packing)

        for event in packing.domain_events:
            self._event_publisher.publish(event)
        packing.clear_events()

        return self._to_dto(packing)

    def get_packing(self, packing_id: UUID) -> PackingDTO:
        """Get packing operation."""
        packing = self._packing_repo.get(packing_id)
        return self._to_dto(packing)

    def _to_dto(self, packing: PackingOperation) -> PackingDTO:
        """Convert packing to DTO."""
        from .dto import PackageDimensionsDTO, PackageDTO, PackageItemDTO

        return PackingDTO(
            id=packing.id,
            packing_number=packing.packing_number.value,
            picking_operation_id=packing.picking_operation_id,
            packages=[
                PackageDTO(
                    id=pkg.id,
                    box_type=pkg.box_type,
                    dimensions=PackageDimensionsDTO(
                        length_cm=pkg.dimensions.length_cm,
                        width_cm=pkg.dimensions.width_cm,
                        height_cm=pkg.dimensions.height_cm,
                        volume_cm3=pkg.dimensions.volume_cm3,
                    ),
                    weight_kg=pkg.weight.kg,
                    items=[
                        PackageItemDTO(
                            id=item.id,
                            product_id=item.product_id,
                            product_code=item.product_code,
                            product_name=item.product_name,
                            quantity=item.quantity,
                            lot_serial_id=item.lot_serial_id,
                        )
                        for item in pkg.items
                    ],
                    tracking_number=pkg.tracking_number.value
                    if pkg.tracking_number
                    else None,
                    total_weight=pkg.total_weight.kg,
                    dimensional_weight=pkg.dimensional_weight.kg,
                    billable_weight=pkg.billable_weight.kg,
                )
                for pkg in packing.packages
            ],
            packer_id=packing.packer_id,
            started_at=packing.started_at,
            completed_at=packing.completed_at,
            state=packing.state,
            created_at=packing.created_at,
            updated_at=packing.updated_at,
        )


class ShipmentService:
    """Service for managing shipments."""

    def __init__(
        self,
        shipment_repo: IShipmentRepository,
        event_publisher: DomainEventPublisher,
    ) -> None:
        self._shipment_repo = shipment_repo
        self._event_publisher = event_publisher

    def create_shipment(self, dto: ShipmentCreateDTO) -> ShipmentDTO:
        """Create new shipment."""
        shipment = Shipment.create(
            packing_operation_id=dto.packing_operation_id,
            carrier_id=dto.carrier_id,
            service_level=dto.service_level,
            delivery_address=_address_from_dto(dto.delivery_address),
            insurance_value=dto.insurance_value,
            require_signature=dto.require_signature,
        )

        self._shipment_repo.add(shipment)
        for event in shipment.domain_events:
            self._event_publisher.publish(event)
        shipment.clear_events()

        return self._to_dto(shipment)

    def confirm_shipment(
        self, shipment_id: UUID, dto: ShipmentConfirmDTO
    ) -> ShipmentDTO:
        """Confirm shipment with tracking."""
        from serp_crm.domain import Money

        from ..domain import TrackingNumber

        shipment = self._shipment_repo.get(shipment_id)
        shipment.confirm(
            tracking_number=TrackingNumber(dto.tracking_number),
            shipping_cost=Money(dto.shipping_cost, dto.currency),
        )
        self._shipment_repo.update(shipment)

        for event in shipment.domain_events:
            self._event_publisher.publish(event)
        shipment.clear_events()

        return self._to_dto(shipment)

    def mark_picked_up(self, shipment_id: UUID) -> ShipmentDTO:
        """Mark shipment picked up."""
        shipment = self._shipment_repo.get(shipment_id)
        shipment.mark_picked_up()
        self._shipment_repo.update(shipment)

        for event in shipment.domain_events:
            self._event_publisher.publish(event)
        shipment.clear_events()

        return self._to_dto(shipment)

    def update_status(
        self, shipment_id: UUID, dto: ShipmentUpdateStatusDTO
    ) -> ShipmentDTO:
        """Update shipment tracking status."""
        shipment = self._shipment_repo.get(shipment_id)
        shipment.update_tracking_status(dto.new_state, dto.delivery_proof)
        self._shipment_repo.update(shipment)

        for event in shipment.domain_events:
            self._event_publisher.publish(event)
        shipment.clear_events()

        return self._to_dto(shipment)

    def cancel_shipment(self, shipment_id: UUID) -> ShipmentDTO:
        """Cancel shipment."""
        shipment = self._shipment_repo.get(shipment_id)
        shipment.cancel()
        self._shipment_repo.update(shipment)

        for event in shipment.domain_events:
            self._event_publisher.publish(event)
        shipment.clear_events()

        return self._to_dto(shipment)

    def get_shipment(self, shipment_id: UUID) -> ShipmentDTO:
        """Get shipment."""
        shipment = self._shipment_repo.get(shipment_id)
        return self._to_dto(shipment)

    def _to_dto(self, shipment: Shipment) -> ShipmentDTO:
        """Convert shipment to DTO."""
        return ShipmentDTO(
            id=shipment.id,
            shipment_number=shipment.shipment_number.value,
            packing_operation_id=shipment.packing_operation_id,
            carrier_id=shipment.carrier_id,
            service_level=shipment.service_level,
            delivery_address=_address_to_dto(shipment.delivery_address),
            tracking_number=shipment.tracking_number.value
            if shipment.tracking_number
            else None,
            shipping_cost=shipment.shipping_cost,
            insurance_value=shipment.insurance_value,
            require_signature=shipment.require_signature,
            confirmed_at=shipment.confirmed_at,
            picked_up_at=shipment.picked_up_at,
            delivered_at=shipment.delivered_at,
            delivery_proof=shipment.delivery_proof,
            state=shipment.state,
            created_at=shipment.created_at,
            updated_at=shipment.updated_at,
        )


class CarrierService:
    """Service for managing carriers."""

    def __init__(self, carrier_repo: ICarrierRepository) -> None:
        self._carrier_repo = carrier_repo

    def create_carrier(self, dto: CarrierCreateDTO) -> CarrierDTO:
        """Create new carrier."""
        carrier = Carrier.create(
            code=dto.code,
            name=dto.name,
            api_endpoint=dto.api_endpoint,
            api_key=dto.api_key,
            account_number=dto.account_number,
            tracking_url_template=dto.tracking_url_template,
            supports_labels=dto.supports_labels,
            supports_tracking=dto.supports_tracking,
        )

        self._carrier_repo.add(carrier)
        return self._to_dto(carrier)

    def update_carrier(self, carrier_id: UUID, dto: CarrierUpdateDTO) -> CarrierDTO:
        """Update carrier."""
        carrier = self._carrier_repo.get(carrier_id)

        if dto.name is not None:
            carrier.name = dto.name
        if dto.api_endpoint is not None:
            carrier.api_endpoint = dto.api_endpoint
        if dto.api_key is not None:
            carrier.api_key = dto.api_key
        if dto.account_number is not None:
            carrier.account_number = dto.account_number
        if dto.tracking_url_template is not None:
            carrier.tracking_url_template = dto.tracking_url_template
        if dto.supports_labels is not None:
            carrier.supports_labels = dto.supports_labels
        if dto.supports_tracking is not None:
            carrier.supports_tracking = dto.supports_tracking
        if dto.is_active is not None:
            carrier.is_active = dto.is_active

        self._carrier_repo.update(carrier)
        return self._to_dto(carrier)

    def get_carrier(self, carrier_id: UUID) -> CarrierDTO:
        """Get carrier."""
        carrier = self._carrier_repo.get(carrier_id)
        return self._to_dto(carrier)

    def list_active_carriers(self) -> list[CarrierDTO]:
        """List active carriers."""
        carriers = self._carrier_repo.list_active()
        return [self._to_dto(carrier) for carrier in carriers]

    def _to_dto(self, carrier: Carrier) -> CarrierDTO:
        """Convert carrier to DTO."""
        return CarrierDTO(
            id=carrier.id,
            code=carrier.code,
            name=carrier.name,
            is_active=carrier.is_active,
            api_endpoint=carrier.api_endpoint,
            api_key=carrier.api_key,
            account_number=carrier.account_number,
            tracking_url_template=carrier.tracking_url_template,
            supports_labels=carrier.supports_labels,
            supports_tracking=carrier.supports_tracking,
            created_at=carrier.created_at,
            updated_at=carrier.updated_at,
        )


class RouteService:
    """Service for managing delivery routes."""

    def __init__(
        self,
        route_repo: IDeliveryRouteRepository,
        event_publisher: DomainEventPublisher,
    ) -> None:
        self._route_repo = route_repo
        self._event_publisher = event_publisher

    def create_route(self, dto: RouteCreateDTO) -> RouteDTO:
        """Create new delivery route."""
        route = DeliveryRoute.create(
            route_date=dto.route_date,
            driver_id=dto.driver_id,
            vehicle_id=dto.vehicle_id,
        )

        for stop_dto in dto.stops:
            route.add_stop(
                shipment_id=stop_dto.shipment_id,
                delivery_address=_address_from_dto(stop_dto.delivery_address),
                estimated_arrival=stop_dto.estimated_arrival,
            )

        self._route_repo.add(route)
        for event in route.domain_events:
            self._event_publisher.publish(event)
        route.clear_events()

        return self._to_dto(route)

    def add_stop(self, route_id: UUID, dto: RouteStopCreateDTO) -> RouteDTO:
        """Add stop to route."""
        route = self._route_repo.get(route_id)
        route.add_stop(
            shipment_id=dto.shipment_id,
            delivery_address=_address_from_dto(dto.delivery_address),
            estimated_arrival=dto.estimated_arrival,
        )

        self._route_repo.update(route)
        return self._to_dto(route)

    def start_route(self, route_id: UUID) -> RouteDTO:
        """Start delivery route."""
        route = self._route_repo.get(route_id)
        route.start()
        self._route_repo.update(route)

        for event in route.domain_events:
            self._event_publisher.publish(event)
        route.clear_events()

        return self._to_dto(route)

    def complete_stop(
        self, route_id: UUID, stop_id: UUID, dto: RouteCompleteStopDTO
    ) -> RouteDTO:
        """Complete route stop."""
        route = self._route_repo.get(route_id)
        route.complete_stop(stop_id, dto.notes)
        self._route_repo.update(route)

        for event in route.domain_events:
            self._event_publisher.publish(event)
        route.clear_events()

        return self._to_dto(route)

    def complete_route(self, route_id: UUID) -> RouteDTO:
        """Complete delivery route."""
        route = self._route_repo.get(route_id)
        route.complete()
        self._route_repo.update(route)

        for event in route.domain_events:
            self._event_publisher.publish(event)
        route.clear_events()

        return self._to_dto(route)

    def get_route(self, route_id: UUID) -> RouteDTO:
        """Get delivery route."""
        route = self._route_repo.get(route_id)
        return self._to_dto(route)

    def _to_dto(self, route: DeliveryRoute) -> RouteDTO:
        """Convert route to DTO."""
        from .dto import RouteStopDTO

        return RouteDTO(
            id=route.id,
            route_number=route.route_number.value,
            route_date=route.route_date,
            driver_id=route.driver_id,
            vehicle_id=route.vehicle_id,
            stops=[
                RouteStopDTO(
                    id=stop.id,
                    shipment_id=stop.shipment_id,
                    delivery_address=_address_to_dto(stop.delivery_address),
                    sequence=stop.sequence,
                    estimated_arrival=stop.estimated_arrival,
                    actual_arrival=stop.actual_arrival,
                    completed=stop.completed,
                    notes=stop.notes,
                )
                for stop in route.stops
            ],
            started_at=route.started_at,
            completed_at=route.completed_at,
            state=route.state,
            created_at=route.created_at,
            updated_at=route.updated_at,
        )


class RMAService:
    """Service for managing return authorizations."""

    def __init__(
        self,
        rma_repo: IReturnAuthorizationRepository,
        event_publisher: DomainEventPublisher,
    ) -> None:
        self._rma_repo = rma_repo
        self._event_publisher = event_publisher

    def create_rma(self, dto: RMACreateDTO) -> RMADTO:
        """Create new return authorization."""
        rma = ReturnAuthorization.create(
            original_shipment_id=dto.original_shipment_id,
            customer_id=dto.customer_id,
            action=dto.action,
        )

        for line_dto in dto.lines:
            rma.add_line(
                product_id=line_dto.product_id,
                product_code=line_dto.product_code,
                product_name=line_dto.product_name,
                quantity=line_dto.quantity,
                reason=line_dto.reason,
                condition=line_dto.condition,
            )

        self._rma_repo.add(rma)
        for event in rma.domain_events:
            self._event_publisher.publish(event)
        rma.clear_events()

        return self._to_dto(rma)

    def approve_rma(self, rma_id: UUID, dto: RMAApproveDTO) -> RMADTO:
        """Approve return authorization."""
        rma = self._rma_repo.get(rma_id)
        rma.approve(_address_from_dto(dto.return_address))
        self._rma_repo.update(rma)

        for event in rma.domain_events:
            self._event_publisher.publish(event)
        rma.clear_events()

        return self._to_dto(rma)

    def reject_rma(self, rma_id: UUID, dto: RMARejectDTO) -> RMADTO:
        """Reject return authorization."""
        rma = self._rma_repo.get(rma_id)
        rma.reject(dto.reason)
        self._rma_repo.update(rma)

        for event in rma.domain_events:
            self._event_publisher.publish(event)
        rma.clear_events()

        return self._to_dto(rma)

    def mark_rma_shipped(self, rma_id: UUID, dto: RMAShipDTO) -> RMADTO:
        """Mark RMA shipped by customer."""
        from ..domain import TrackingNumber

        rma = self._rma_repo.get(rma_id)
        rma.mark_shipped(TrackingNumber(dto.tracking_number))
        self._rma_repo.update(rma)

        for event in rma.domain_events:
            self._event_publisher.publish(event)
        rma.clear_events()

        return self._to_dto(rma)

    def receive_rma(self, rma_id: UUID) -> RMADTO:
        """Receive return shipment."""
        rma = self._rma_repo.get(rma_id)
        rma.receive()
        self._rma_repo.update(rma)

        for event in rma.domain_events:
            self._event_publisher.publish(event)
        rma.clear_events()

        return self._to_dto(rma)

    def process_rma(self, rma_id: UUID, dto: RMAProcessDTO) -> RMADTO:
        """Process return (refund/exchange)."""
        from serp_crm.domain import Money

        rma = self._rma_repo.get(rma_id)
        rma.process(Money(dto.refund_amount, dto.currency))
        self._rma_repo.update(rma)

        for event in rma.domain_events:
            self._event_publisher.publish(event)
        rma.clear_events()

        return self._to_dto(rma)

    def get_rma(self, rma_id: UUID) -> RMADTO:
        """Get return authorization."""
        rma = self._rma_repo.get(rma_id)
        return self._to_dto(rma)

    def _to_dto(self, rma: ReturnAuthorization) -> RMADTO:
        """Convert RMA to DTO."""
        from .dto import RMALineDTO

        return RMADTO(
            id=rma.id,
            rma_number=rma.rma_number.value,
            original_shipment_id=rma.original_shipment_id,
            customer_id=rma.customer_id,
            action=rma.action,
            lines=[
                RMALineDTO(
                    id=line.id,
                    product_id=line.product_id,
                    product_code=line.product_code,
                    product_name=line.product_name,
                    quantity=line.quantity,
                    reason=line.reason,
                    condition=line.condition,
                )
                for line in rma.lines
            ],
            return_address=_address_to_dto(rma.return_address)
            if rma.return_address
            else None,
            return_tracking_number=rma.return_tracking_number.value
            if rma.return_tracking_number
            else None,
            requested_at=rma.requested_at,
            approved_at=rma.approved_at,
            rejected_at=rma.rejected_at,
            shipped_at=rma.shipped_at,
            received_at=rma.received_at,
            processed_at=rma.processed_at,
            refund_amount=rma.refund_amount,
            state=rma.state,
            created_at=rma.created_at,
            updated_at=rma.updated_at,
        )
