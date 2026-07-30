from typing import Any
from uuid import UUID

from sqlalchemy import or_, select

from app.models.infrastructure import Location, LocationPosition
from app.models.master import LocationType, PositionTemplate, PositionTemplateNode, PositionType
from app.repositories.infrastructure import InfrastructureRepository
from app.schemas.infrastructure import LocationSearchRead, LocationTreeNode, PositionPreviewItem


class InfrastructureService:
    def __init__(self, session) -> None:
        self.session = session

    async def get_location(self, location_id: UUID) -> Location | None:
        repo = InfrastructureRepository(Location, self.session)
        return await repo.get_by_id(location_id)

    async def list_locations(self, offset: int = 0, limit: int = 100) -> tuple[list[Location], int]:
        repo = InfrastructureRepository(Location, self.session)
        items = await repo.list(offset=offset, limit=limit)
        return items, await repo.count()

    async def search_locations(
        self,
        *,
        search: str,
        project_id: UUID | None,
        location_type_code: str | None = None,
        limit: int,
    ) -> list[LocationSearchRead]:
        import re
        from sqlalchemy import func
        search_clean = re.sub(r'[\s\-]+', '', search)
        if not search_clean:
            search_clean = search
            
        code_clean = func.replace(func.replace(Location.code, ' ', ''), '-', '')
        name_clean = func.replace(func.replace(Location.name, ' ', ''), '-', '')
        
        conditions = [or_(code_clean.ilike(f"%{search_clean}%"), name_clean.ilike(f"%{search_clean}%"))]
        if project_id is not None:
            conditions.append(Location.project_id == project_id)
        if location_type_code is not None:
            conditions.append(LocationType.code == location_type_code)
        result = await self.session.execute(
            select(Location, LocationType.name.label("location_type_name"))
            .join(LocationType, LocationType.id == Location.location_type_id)
            .where(*conditions)
            .order_by(Location.code)
            .limit(limit),
        )
        rows = result.all()

        locations = {location.id: (location, type_name) for location, type_name in rows}
        parent_ids = {location.parent_location_id for location, _ in rows if location.parent_location_id}
        while parent_ids:
            missing_ids = parent_ids - locations.keys()
            if not missing_ids:
                break
            parent_result = await self.session.execute(
                select(Location, LocationType.name.label("location_type_name"))
                .join(LocationType, LocationType.id == Location.location_type_id)
                .where(Location.id.in_(missing_ids)),
            )
            parent_rows = parent_result.all()
            if not parent_rows:
                break
            locations.update({location.id: (location, type_name) for location, type_name in parent_rows})
            parent_ids = {location.parent_location_id for location, _ in parent_rows if location.parent_location_id}

        matches: list[LocationSearchRead] = []
        for location, type_name in rows:
            path_nodes: list[str] = []
            current = location
            visited_ids: set[UUID] = set()
            while current and current.id not in visited_ids:
                visited_ids.add(current.id)
                path_nodes.append(current.name)
                parent = locations.get(current.parent_location_id) if current.parent_location_id else None
                current = parent[0] if parent else None
            matches.append(
                LocationSearchRead(
                    id=location.id,
                    code=location.code,
                    name=location.name,
                    location_type_name=type_name,
                    hierarchy_path=" / ".join(reversed(path_nodes)),
                ),
            )
        return matches

    async def preview_template_positions(self, template_id: int) -> list[PositionPreviewItem]:
        """Return the positions that would be created from the given template, without persisting anything."""
        rows = (
            await self.session.execute(
                select(PositionTemplateNode, PositionType.name.label("position_type_name"))
                .join(PositionType, PositionType.id == PositionTemplateNode.position_type_id)
                .where(PositionTemplateNode.position_template_id == template_id)
                .order_by(PositionTemplateNode.node_order, PositionTemplateNode.position_number)
            )
        ).all()
        return [
            PositionPreviewItem(
                position_type_id=node.position_type_id,
                position_type_name=type_name,
                position_number=node.position_number,
                maximum_capacity=node.maximum_capacity,
                node_order=node.node_order,
                remarks=node.remarks,
            )
            for node, type_name in rows
        ]

    async def create_location(self, values: dict[str, Any]) -> Location:
        # Extract template_id before creating the location (not a DB column)
        template_id: int | None = values.pop("position_template_id", None)

        entity = Location(**values)
        repo = InfrastructureRepository(Location, self.session)
        location = await repo.create(entity)

        # Auto-create positions from template if provided
        if template_id is not None:
            await self._apply_position_template(location.id, template_id)

        return location

    async def _apply_position_template(self, location_id: UUID, template_id: int) -> None:
        """Bulk-create infrastructure.location_positions from a position template's nodes."""
        rows = (
            await self.session.execute(
                select(PositionTemplateNode)
                .where(PositionTemplateNode.position_template_id == template_id)
                .order_by(PositionTemplateNode.node_order, PositionTemplateNode.position_number)
            )
        ).scalars().all()

        for node in rows:
            position = LocationPosition(
                location_id=location_id,
                position_template_node_id=node.id,
                position_type_id=node.position_type_id,
                position_number=node.position_number,
                maximum_capacity=node.maximum_capacity,
                remarks=node.remarks,
            )
            self.session.add(position)

        await self.session.flush()

    async def update_location(self, location_id: UUID, values: dict[str, Any]) -> Location | None:
        repo = InfrastructureRepository(Location, self.session)
        location = await repo.get_by_id(location_id)
        if not location:
            return None
        return await repo.update(location, values)

    async def list_positions(self, location_id: UUID, offset: int = 0, limit: int = 100) -> tuple[list[LocationPosition], int]:
        result = await self.session.execute(
            select(LocationPosition).where(LocationPosition.location_id == location_id).offset(offset).limit(limit)
        )
        items = result.scalars().all()
        total = len(items)
        return items, total

    async def create_position(self, values: dict[str, Any]) -> LocationPosition:
        entity = LocationPosition(**values)
        repo = InfrastructureRepository(LocationPosition, self.session)
        return await repo.create(entity)

    async def update_position(self, position_id: UUID, values: dict[str, Any]) -> LocationPosition | None:
        repo = InfrastructureRepository(LocationPosition, self.session)
        position = await repo.get_by_id(position_id)
        if not position:
            return None
        return await repo.update(position, values)

    async def get_location_tree(self) -> list[LocationTreeNode]:
        # Fetch all locations with their type name in one query
        result = await self.session.execute(
            select(Location, LocationType.name.label("type_name"))
            .join(LocationType, LocationType.id == Location.location_type_id)
            .order_by(Location.code)
        )
        rows = result.all()

        # Build a dict of id -> node
        node_map: dict[UUID, LocationTreeNode] = {}
        for location, type_name in rows:
            node_map[location.id] = LocationTreeNode(
                id=location.id,
                code=location.code,
                name=location.name,
                location_type_id=location.location_type_id,
                location_type_name=type_name,
                parent_location_id=location.parent_location_id,
                latitude=location.latitude,
                longitude=location.longitude,
                remarks=location.remarks,
                children=[],
            )

        # Build tree by assigning children to their parents
        roots: list[LocationTreeNode] = []
        for node in node_map.values():
            if node.parent_location_id and node.parent_location_id in node_map:
                node_map[node.parent_location_id].children.append(node)
            else:
                roots.append(node)

        return roots
