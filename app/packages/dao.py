from app.dao.base import BaseDAO
from app.packages.models import Package
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload
from app.database import async_session_maker

from app.packages.models import PackageType

class PackagesDAO(BaseDAO):
    model = Package
    model_pt = PackageType

    @classmethod
    async def find_all(cls, user_session_id, page: int, page_size: int, **filter):
        async with async_session_maker() as session:
            filter_dict = {}
            for k, v in filter.items():
                filter_dict[k] = v

            query = select(cls.model).options(joinedload(cls.model.package_type)).filter_by(user_session_id=user_session_id)

            if filter_dict.get("package_type") is not None:
                ft = await session.execute(select(cls.model_pt).filter_by(name=filter_dict.get("package_type")))
                ft = ft.scalars().one()
                query = query.filter(cls.model.package_type_id == ft.id)

                if filter_dict.get("is_price_count") is not None:
                    query = query.filter(
                        cls.model.price != None if filter_dict.get("is_price_count") is True else cls.model.price == None
                    )

            elif filter_dict.get("package_type") is None and filter_dict.get("is_price_count") is not None:
                query = query.filter(
                    cls.model.price != None if filter_dict.get("is_price_count") is True else cls.model.price == None
                )

            else:
                query = query.filter()

            query = query.limit(page_size)
            if page:
                query = query.offset((page * page_size) - page_size)

            result = await session.execute(query)
            return result.scalars().all()

    @classmethod
    async def find_with_no_price(cls):
        async with async_session_maker() as session:
            query = select(cls.model).filter_by(price=None)
            result = await session.execute(query)
            return result.scalars().all()

class PackageTypesDAO(BaseDAO):
    model = PackageType
