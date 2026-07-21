from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import exists, func, or_, select

from app.models.master import (
    AssetCategory,
    AssetSubcategory,
    Manufacturer,
    ManufacturerAssetScope,
    LocationTemplate,
    PositionTemplate,
    PositionTemplateNode,
    PositionType,
    SpecificationDefinition,
)
from app.repositories.master import MasterRepository


class MasterService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def list_lookups(
        self,
        model: type[LocationTemplate] | type[PositionTemplate] | type[SpecificationDefinition],
        offset: int = 0,
        limit: int = 100,
        filters: dict[str, int] | None = None,
    ) -> tuple[list[Any], int]:
        repo = MasterRepository(model, self.session)
        items = await repo.list(offset=offset, limit=limit, filters=filters)
        total = await repo.count(filters=filters)
        return items, total

    async def get_lookup(self, model: type[Any], entity_id: int) -> Any:
        repo = MasterRepository(model, self.session)
        item = await repo.get_by_id(entity_id)
        return item

    async def list_manufacturers_for_asset(
        self, *, category_id: int | None, subcategory_id: int | None, offset: int, limit: int,
    ) -> tuple[list[Manufacturer], int]:
        query = select(Manufacturer).where(Manufacturer.is_active.is_(True))
        if category_id is not None:
            has_scope = exists(select(ManufacturerAssetScope.id).where(ManufacturerAssetScope.manufacturer_id == Manufacturer.id, ManufacturerAssetScope.is_active.is_(True)))
            matching_scope = exists(select(ManufacturerAssetScope.id).where(
                ManufacturerAssetScope.manufacturer_id == Manufacturer.id,
                ManufacturerAssetScope.asset_category_id == category_id,
                ManufacturerAssetScope.is_active.is_(True),
                or_(ManufacturerAssetScope.asset_subcategory_id.is_(None), ManufacturerAssetScope.asset_subcategory_id == subcategory_id),
            ))
            query = query.where(or_(~has_scope, matching_scope))
        query = query.order_by(Manufacturer.display_order, Manufacturer.name)
        items = (await self.session.execute(query.offset(offset).limit(limit))).scalars().all()
        total = await self.session.scalar(select(func.count()).select_from(query.subquery()))
        return items, total or 0

    async def create_lookup(self, model: type[Any], values: dict[str, Any]) -> Any:
        entity = model(**values)
        repo = MasterRepository(model, self.session)
        return await repo.create(entity)

    async def update_lookup(self, model: type[Any], entity_id: int, values: dict[str, Any]) -> Any:
        repo = MasterRepository(model, self.session)
        entity = await repo.get_by_id(entity_id)
        if not entity:
            return None
        return await repo.update(entity, values)

    async def list_specification_definitions(
        self,
        *,
        offset: int,
        limit: int,
        category_id: int | None = None,
        subcategory_id: int | None = None,
    ) -> tuple[list[dict[str, Any]], int]:
        query = (
            select(
                SpecificationDefinition,
                AssetCategory.name.label("category_name"),
                AssetSubcategory.name.label("subcategory_name"),
            )
            .outerjoin(AssetCategory, AssetCategory.id == SpecificationDefinition.asset_category_id)
            .outerjoin(AssetSubcategory, AssetSubcategory.id == SpecificationDefinition.asset_subcategory_id)
        )
        count_query = select(func.count()).select_from(SpecificationDefinition)
        if category_id is not None:
            query = query.where(SpecificationDefinition.asset_category_id == category_id)
            count_query = count_query.where(SpecificationDefinition.asset_category_id == category_id)
        if subcategory_id is not None:
            query = query.where(SpecificationDefinition.asset_subcategory_id == subcategory_id)
            count_query = count_query.where(SpecificationDefinition.asset_subcategory_id == subcategory_id)
        rows = (await self.session.execute(
            query.order_by(SpecificationDefinition.display_order, SpecificationDefinition.name).offset(offset).limit(limit),
        )).all()
        total = (await self.session.execute(count_query)).scalar_one()
        return [
            {
                **{column.name: getattr(definition, column.name) for column in SpecificationDefinition.__table__.columns},
                "category_name": category_name,
                "subcategory_name": subcategory_name,
            }
            for definition, category_name, subcategory_name in rows
        ], total

    async def create_specification_definition(self, values: dict[str, Any]) -> SpecificationDefinition:
        await self._validate_specification_scope(values)
        definition = SpecificationDefinition(**values)
        self.session.add(definition)
        await self.session.flush()
        return definition

    async def update_specification_definition(self, definition_id: int, values: dict[str, Any]) -> SpecificationDefinition | None:
        definition = await self.session.get(SpecificationDefinition, definition_id)
        if not definition:
            return None
        merged_values = {
            "asset_category_id": values.get("asset_category_id", definition.asset_category_id),
            "asset_subcategory_id": values.get("asset_subcategory_id", definition.asset_subcategory_id),
        }
        await self._validate_specification_scope(merged_values)
        for key, value in values.items():
            setattr(definition, key, value)
        await self.session.flush()
        return definition

    async def _validate_specification_scope(self, values: dict[str, Any]) -> None:
        subcategory_id = values.get("asset_subcategory_id")
        category_id = values.get("asset_category_id")
        if subcategory_id is None:
            return
        subcategory = await self.session.get(AssetSubcategory, subcategory_id)
        if not subcategory or (category_id is not None and subcategory.asset_category_id != category_id):
            raise ValueError("Selected subcategory does not belong to the selected category.")

    # ─── Position Template Management ─────────────────────────────────────────

    async def list_position_templates(self, offset: int = 0, limit: int = 100) -> tuple[list[dict[str, Any]], int]:
        """List all position templates with node counts."""
        templates = (
            await self.session.execute(
                select(PositionTemplate)
                .order_by(PositionTemplate.display_order, PositionTemplate.name)
                .offset(offset)
                .limit(limit)
            )
        ).scalars().all()
        total = await self.session.scalar(select(func.count()).select_from(PositionTemplate))

        result = []
        for tmpl in templates:
            node_count = await self.session.scalar(
                select(func.count()).where(PositionTemplateNode.position_template_id == tmpl.id)
            )
            result.append({"template": tmpl, "node_count": node_count or 0})
        return result, total or 0

    async def get_position_template_with_nodes(self, template_id: int) -> dict[str, Any] | None:
        """Get a single position template with all its nodes and position type names."""
        template = await self.session.get(PositionTemplate, template_id)
        if not template:
            return None
        rows = (
            await self.session.execute(
                select(PositionTemplateNode, PositionType.name.label("position_type_name"))
                .join(PositionType, PositionType.id == PositionTemplateNode.position_type_id)
                .where(PositionTemplateNode.position_template_id == template_id)
                .order_by(PositionTemplateNode.node_order, PositionTemplateNode.position_number)
            )
        ).all()
        nodes = [
            {
                **{col.name: getattr(node, col.name) for col in PositionTemplateNode.__table__.columns},
                "position_type_name": type_name,
            }
            for node, type_name in rows
        ]
        return {"template": template, "nodes": nodes, "node_count": len(nodes)}

    async def create_position_template(self, values: dict[str, Any]) -> PositionTemplate:
        template = PositionTemplate(**values)
        self.session.add(template)
        await self.session.flush()
        return template

    async def update_position_template(self, template_id: int, values: dict[str, Any]) -> PositionTemplate | None:
        template = await self.session.get(PositionTemplate, template_id)
        if not template:
            return None
        for key, value in values.items():
            setattr(template, key, value)
        await self.session.flush()
        return template

    async def get_template_nodes(self, template_id: int) -> list[dict[str, Any]]:
        """Return all nodes of a template with their position type names."""
        rows = (
            await self.session.execute(
                select(PositionTemplateNode, PositionType.name.label("position_type_name"))
                .join(PositionType, PositionType.id == PositionTemplateNode.position_type_id)
                .where(PositionTemplateNode.position_template_id == template_id)
                .order_by(PositionTemplateNode.node_order, PositionTemplateNode.position_number)
            )
        ).all()
        return [
            {
                **{col.name: getattr(node, col.name) for col in PositionTemplateNode.__table__.columns},
                "position_type_name": type_name,
            }
            for node, type_name in rows
        ]

    async def add_template_node(self, template_id: int, values: dict[str, Any]) -> dict[str, Any]:
        values["position_template_id"] = template_id
        node = PositionTemplateNode(**values)
        self.session.add(node)
        await self.session.flush()
        # Return with type name
        row = (
            await self.session.execute(
                select(PositionTemplateNode, PositionType.name.label("position_type_name"))
                .join(PositionType, PositionType.id == PositionTemplateNode.position_type_id)
                .where(PositionTemplateNode.id == node.id)
            )
        ).first()
        node_obj, type_name = row
        return {
            **{col.name: getattr(node_obj, col.name) for col in PositionTemplateNode.__table__.columns},
            "position_type_name": type_name,
        }

    async def update_template_node(self, node_id: int, values: dict[str, Any]) -> dict[str, Any] | None:
        node = await self.session.get(PositionTemplateNode, node_id)
        if not node:
            return None
        for key, value in values.items():
            if value is not None:
                setattr(node, key, value)
        await self.session.flush()
        row = (
            await self.session.execute(
                select(PositionTemplateNode, PositionType.name.label("position_type_name"))
                .join(PositionType, PositionType.id == PositionTemplateNode.position_type_id)
                .where(PositionTemplateNode.id == node_id)
            )
        ).first()
        node_obj, type_name = row
        return {
            **{col.name: getattr(node_obj, col.name) for col in PositionTemplateNode.__table__.columns},
            "position_type_name": type_name,
        }

    async def delete_template_node(self, node_id: int) -> bool:
        node = await self.session.get(PositionTemplateNode, node_id)
        if not node:
            return False
        await self.session.delete(node)
        await self.session.flush()
        return True
