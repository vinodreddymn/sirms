import asyncio
from uuid import UUID
from app.db.database import async_session_factory
from app.services.asset_service import AssetService
from app.api.v1.asset.router import _build_asset_details

async def main():
    async with async_session_factory() as session:
        service = AssetService(session)
        try:
            asset_id = UUID('88888888-8888-8888-8888-888888888882')
            details = await service.get_asset_details(asset_id)
            if details:
                res = _build_asset_details(details)
                print(res)
            else:
                print('Not found')
        except Exception as e:
            import traceback
            traceback.print_exc()

if __name__ == '__main__':
    asyncio.run(main())
