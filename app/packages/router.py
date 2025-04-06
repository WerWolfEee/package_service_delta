from fastapi import APIRouter, Depends, HTTPException
from app import redis
from app.packages.dao import PackagesDAO, PackageTypesDAO
from app.packages.schemas import SPackage, SPackageNew, SPackageType, SPackageTypeNew, PackageFilters
from app.packages.dependencies import get_session, get_redis


router = APIRouter(prefix='/packages', tags=['Посылки'])

@router.post("/types", summary="Добавить тип посылки")
async def create_package_type(package_type: SPackageTypeNew) -> dict:
    res = await PackageTypesDAO.add(**package_type.model_dump())
    if not res :
        raise HTTPException(status_code=500, detail=f"Ошибка при добавлении типа посылки!")
    return {"message": "Тип посылки успешно добавлен!", "package_type": package_type}


@router.get("/types/list", summary="Получить список типов посылок")
async def get_package_types_list() -> list[SPackageType] | dict:
    res = await PackageTypesDAO.find_all()
    if not res:
        raise HTTPException(status_code=404, detail=f'Типы посылок не найдены')
    return res


@router.post("/packages", summary="Добавить посылку")
async def create_package(package: SPackageNew, session: str = Depends(get_session)) -> dict:
    res = await PackagesDAO.add(**package.model_dump(), user_session_id=session)
    if not res :
        raise HTTPException(status_code=500, detail=f"Ошибка при добавлении посылки!")
    return {"message": "Посылка успешно добавлена!", "package_id": res.id}


@router.get("/packages", summary="Получить список посылок с фильтрами", response_model=list[SPackage])
async def get_packages(
        filters: PackageFilters = Depends(),
        session: str = Depends(get_session),
) -> list[SPackage] | dict:
    res = await PackagesDAO.find_all(user_session_id=session, **filters.to_dict())
    if not res:
        raise HTTPException(status_code=404, detail=f'Посылки с указанными вами параметрами не найдены!')
    res_models = []
    for i in res:
        res_models.append(SPackage.model_validate(i))
    return res_models

@router.get("/price_calculation", summary="Запустить принудительный расчет стоимости доставки", response_model=None)
async def start_price_calculation(conn = Depends(get_redis)) -> dict:
    await redis.publish(conn, 'start_sync', True)
    return {'msg': 'Принудительный расчет стоимости доставки запущен'}
