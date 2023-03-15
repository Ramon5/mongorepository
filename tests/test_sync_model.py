def test_create_data(repository, model_class) -> None:
    data = model_class(name="foo bar", age=18, job="developer")
    result = repository.save(data)
    assert result is not None


def test_list_data_from_db(repository, model_class):
    data = model_class(name="foo bar", age=18, job="developer")
    repository.save(data)

    result = repository.list_all()
    assert len(result) == 1


def test_delete_data(repository, model_class):
    data = model_class(name="foo bar", age=18, job="developer")
    repository.save(data)

    result = repository.list_all()
    assert len(result) == 1

    repository.delete(result[0])
    result = repository.list_all()
    assert not result
