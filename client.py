import aiohttp
import asyncio


async def main():
    session = aiohttp.ClientSession()
    response = await session.post(
        "http://127.0.0.1:8080/advertisement/",
        json={
            "title": "Solar eclipse",
            "description": "Astronomical phenomenon",
            "owner": "user_1"
        }
    )
    print(response.status)
    print(await response.json())


    # response = await session.get(
    #     "http://127.0.0.1:8080/advertisement/1/", )
    # print(response.status)
    # print(await response.json())
    #
    #
    # response = await session.patch(
    #     "http://127.0.0.1:8080/advertisement/1/",
    #     json={
    #         "title": "Moon eclipse",
    #         "owner": "user_2"
    #     }
    # )
    # print(response.status)
    # print(await response.json())


    # response = await session.delete(
    #     "http://127.0.0.1:8080/advertisement/1/",)
    # print(response.status)
    # print(await response.json())

    await session.close()


asyncio.run(main())