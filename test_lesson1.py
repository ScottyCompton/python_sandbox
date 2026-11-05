import json
import pytest
import lesson1

TEST_DATA = {
    "people": [
        {
            "name": "John Doe",
            "age": 30,
            "city": "New York"
        },
        {
            "name": "Jane Doe",
            "age": 25,
            "city": "Los Angeles"
        },
        {
            "name": "Jim Beam",
            "age": 40,
            "city": "Chicago"
        }
    ]
}


 
def get_data():
    return TEST_DATA["people"]

def test_filter_by_age_positive():
    result = lesson1.filter_by_age(get_data(), age=30)
    vals = [p["name"] for p in result]
    assert vals == ["John Doe", "Jim Beam"]

def test_filter_by_age_negative():
    result = lesson1.filter_by_age(get_data(), age=-30)
    vals = [p["name"] for p in result]
    assert vals == ["John Doe", "Jane Doe"]


def test_filter_by_age_not_found():
    result = lesson1.filter_by_age(get_data(), age=450)
    vals = [p["name"] for p in result]
    assert vals == []

def test_filter_by_age_wrong_type():
    result = lesson1.filter_by_age(get_data(), age="oink")
    vals = [p["name"] for p in result]
    assert vals == []

def test_filter_by_city_case():
    result = lesson1.filter_by_city(get_data(), city="CHICAGO")
    vals = [p["city"] for p in result]
    assert vals == ["Chicago"]

def test_filter_by_city():
    result = lesson1.filter_by_city(get_data(), city="Chicago")
    vals = [p["city"] for p in result]
    assert vals == ["Chicago"]

def test_filter_by_city_notfound():
    result = lesson1.filter_by_city(get_data(), "Detroit")
    vals = [p["city"] for p in result]
    assert vals == []


def test_filter_by_name_exists():
    result = lesson1.filter_by_name(get_data(), name="John Doe")
    vals = [p["name"] for p in result]
    assert vals == ["John Doe"]

def test_filter_by_name_notfound():
    result = lesson1.filter_by_name(get_data(), name="Ben Dover")
    vals = [p["name"] for p in result]
    assert vals == []


def test_fiter_data_empty():
    result = lesson1.filter_data(age='',name='',city='')
    vals = [p["name"] for p in result]
    assert vals == []

def test_filter_data_with_name():
    result = lesson1.filter_data(name="John Doe", data_to_filter=get_data())
    vals = [p["name"] for p in result]
    assert vals == ["John Doe"]

def test_filter_data_with_age():
    result = lesson1.filter_data(age=10, data_to_filter=get_data())
    vals = [p["name"] for p in result]
    assert len(vals) == 3

def test_filter_data_with_city():
    result = lesson1.filter_data(city="Chicago", data_to_filter=get_data())
    vals = [p["city"] for p in result]
    assert vals == ["Chicago"]

def test_filter_with_all():
    result = lesson1.filter_data(age=40, name="Jim Beam", city="Chicago", data_to_filter=get_data())
    vals = [p["name"] for p in result]
    assert vals == ["Jim Beam"]

def test_filter_with_name_city():
    result = lesson1.filter_data(name="Jim Beam", city="Chicago", data_to_filter=get_data())
    vals = [p["name"] for p in result]
    assert vals == ["Jim Beam"]

def test_filter_with_age_city():
    result = lesson1.filter_data(age=40, city="Chicago", data_to_filter=get_data())
    vals = [p["name"] for p in result]
    assert vals == ["Jim Beam"]

def test_filter_with_age_name():
    result = lesson1.filter_data(age=40, name="Jim Beam", data_to_filter=get_data())
    vals = [p["name"] for p in result]
    assert vals == ["Jim Beam"]
                