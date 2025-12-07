"""
Entity-Model mappers for serp-common module.

Mappers convert between domain entities and SQLAlchemy models.
"""

from serp_common.domain.entities import AddressEntity, AddressType
from serp_common.infrastructure.persistence.models import AddressModel


class AddressMapper:
    """Mapper between AddressEntity and AddressModel."""

    @staticmethod
    def to_model(entity: AddressEntity) -> AddressModel:
        """Convert domain entity to SQLAlchemy model."""
        return AddressModel(
            id=entity.id,
            label=entity.label,
            street=entity.street,
            city=entity.city,
            country=entity.country,
            state=entity.state,
            postal_code=entity.postal_code,
            address_type=entity.address_type.value,
            owner_type=entity.owner_type,
            owner_id=entity.owner_id,
            is_primary=entity.is_primary,
            is_active=entity.is_active,
            notes=entity.notes,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )

    @staticmethod
    def to_entity(model: AddressModel) -> AddressEntity:
        """Convert SQLAlchemy model to domain entity."""
        entity = object.__new__(AddressEntity)
        entity.id = model.id
        entity.label = model.label
        entity.street = model.street
        entity.city = model.city
        entity.country = model.country
        entity.state = model.state
        entity.postal_code = model.postal_code
        entity.address_type = AddressType(model.address_type)
        entity.owner_type = model.owner_type
        entity.owner_id = model.owner_id
        entity.is_primary = model.is_primary
        entity.is_active = model.is_active
        entity.notes = model.notes
        entity.created_at = model.created_at
        entity.updated_at = model.updated_at
        return entity

    @staticmethod
    def update_model(model: AddressModel, entity: AddressEntity) -> AddressModel:
        """Update model from entity (for existing records)."""
        model.label = entity.label
        model.street = entity.street
        model.city = entity.city
        model.country = entity.country
        model.state = entity.state
        model.postal_code = entity.postal_code
        model.address_type = entity.address_type.value
        model.owner_type = entity.owner_type
        model.owner_id = entity.owner_id
        model.is_primary = entity.is_primary
        model.is_active = entity.is_active
        model.notes = entity.notes
        model.updated_at = entity.updated_at
        return model
