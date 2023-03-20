from tests.factories import DataFactory


def test_create_data(repository, model_class) -> None:
    data = model_class(name="foo bar", age=18, job="developer")
    result = repository.save(data)
    assert result is not None


def test_list_data_from_db(repository, model_class):
    data = model_class(name="foo bar", age=18, job="developer")
    repository.save(data)

    result = repository.list_objects()
    assert len(result) == 1


def test_delete_data(repository, model_class):
    data = model_class(name="foo bar", age=18, job="developer")
    repository.save(data)

    result = repository.list_objects()
    assert len(result) == 1

    repository.delete(result[0].id)
    result = repository.list_objects()
    assert not result


def test_get_paginated_results(repository):
    repository.set_pagination(True)
    registers = DataFactory.batch(size=100)
    repository.bulk_create(registers)
    documents = repository.list_objects()

    assert documents["total"] == 50
    next_page = documents["next_page"]
    second_page = repository.list_objects(next_page=next_page)
    assert second_page["total"] == 50
