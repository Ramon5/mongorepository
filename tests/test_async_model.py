import pytest

from tests.factories import DataFactory

pytestmark = pytest.mark.asyncio


async def test_create_data(async_repository, model_class) -> None:
    data = model_class(name="foo bar", age=18, job="developer")
    result = await async_repository.save(data)
    assert result is not None


async def test_list_data_from_db(async_repository, model_class):
    data = model_class(name="foo bar", age=18, job="developer")
    await async_repository.save(data)

    result = await async_repository.list_objects()
    assert len(result) == 1


async def test_delete_data(async_repository, model_class):
    data = model_class(name="foo bar", age=18, job="developer")
    await async_repository.save(data)

    result = await async_repository.list_objects()
    assert len(result) == 1

    await async_repository.delete(result[0])
    result = await async_repository.list_objects()
    assert not result


async def test_get_paginated_results(async_repository):
    async_repository.set_pagination(True)
    registers = DataFactory.batch(size=100)
    await async_repository.bulk_create(registers)
    documents = await async_repository.list_objects()
    assert documents["total"] == 50
