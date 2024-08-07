from flask import Flask, jsonify, request, Response
from pydantic import ValidationError
from schema import CreateAdvertisement, UpdateAdvertisement
from aiohttp import web

from models import Base, engine, Advertisement, Session
from sqlalchemy.exc import IntegrityError
import json


app = web.Application()


async def orm_context(app: web.Application):
    print('Start')
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()
    print('Shut down')


@web.middleware
async def session_middleware(request: web.Request, handler):
    async with Session() as session:
        request.session = session
        response = await handler(request)
        return response


app.cleanup_ctx.append(orm_context)
app.middlewares.append(session_middleware)


def get_error(error_cls, error_description):
    return error_cls(
            text=json.dumps({"error": error_description}),
            content_type="application/json"
        )


def validate(json_data, schema_cls):
    try:
        return schema_cls(**json_data).dict(exclude_unset=True)
    except ValidationError as err:
        error = err.errors()[0]
        error.pop('ctx', None)
        raise get_error(web.HTTPConflict, error)


async def get_advertisement(advertisement_id: int, session: Session):
    advertisement = await session.get(Advertisement, advertisement_id)
    if advertisement is None:
        raise get_error(web.HTTPNotFound, "advertisement not found")
    return advertisement


async def add_advertisement(advertisement: Advertisement, session: Session):
    session.add(advertisement)
    try:
        await session.commit()
    except IntegrityError:
        error = get_error(web.HTTPConflict, "advertisement already exists")
        raise error
    return advertisement


class AdvertisementView(web.View):
    @property
    def session(self):
        return self.request.session

    @property
    def advertisement_id(self):
        return int(self.request.match_info['advertisement_id'])

    async def get(self):
        advertisement = await get_advertisement(self.advertisement_id, self.session)
        return web.json_response(advertisement.json)

    async def post(self):
        json_data = validate(await self.request.json(), CreateAdvertisement)
        advertisement = Advertisement(**json_data)
        advertisement = await add_advertisement(advertisement, self.session)
        return web.json_response(advertisement.json)

    async def patch(self):
        json_data = validate(await self.request.json(), UpdateAdvertisement)
        advertisement = await get_advertisement(self.advertisement_id, self.session)
        for field, value in json_data.items():
            setattr(advertisement, field, value)
        advertisement = await add_advertisement(advertisement, self.session)
        return web.json_response(advertisement.json)

    async def delete(self):
        advertisement = await get_advertisement(self.advertisement_id, self.session)
        await self.session.delete(advertisement)
        await self.session.commit()
        return jsonify({"status": "deleted"})


app.add_routes([
    web.post('/advertisement/', AdvertisementView),
    web.get('/advertisement/{advertisement_id:\d+}/', AdvertisementView),
    web.patch('/advertisement/{advertisement_id:\d+}/', AdvertisementView),
    web.delete('/advertisement/{advertisement_id:\d+}/', AdvertisementView)
])

web.run_app(app)