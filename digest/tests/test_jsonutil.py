import pytest

from digest.core.jsonutil import JSONExtractError, extract_json


def test_extract_plain_json_object():
    assert extract_json('{"a": 1}') == {"a": 1}


def test_extract_json_from_code_fence():
    text = "Here you go:\n```json\n{\"a\": 1, \"b\": [2,3]}\n```\nthanks"
    assert extract_json(text) == {"a": 1, "b": [2, 3]}


def test_extract_json_array_with_surrounding_prose():
    text = "Result: [1, 2, 3] done"
    assert extract_json(text) == [1, 2, 3]


def test_extract_raises_when_no_json():
    with pytest.raises(JSONExtractError):
        extract_json("no json here")
