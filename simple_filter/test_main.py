import json
import pytest
import main

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
    result = main.filter_by_age(get_data(), age=30)
    vals = [p["name"] for p in result]
    assert vals == ["John Doe", "Jim Beam"]

def test_filter_by_age_negative():
    result = main.filter_by_age(get_data(), age=-30)
    vals = [p["name"] for p in result]
    assert vals == ["John Doe", "Jane Doe"]

def test_filter_by_age_is_zero():
    result = main.filter_by_age(get_data(), age=0)
    vals = [p["name"] for p in result]
    assert vals == []

def test_filter_by_age_is_blank():
    result = main.filter_by_age(get_data())
    #vals = [p["name"] for p in result]
    assert len(result) == 3

def test_filter_by_age_not_found():
    result = main.filter_by_age(get_data(), age=450)
    vals = [p["name"] for p in result]
    assert vals == []

def test_filter_by_age_wrong_type():
    result = main.filter_by_age(get_data(), age="oink")
    vals = [p["name"] for p in result]
    assert vals == []

def test_filter_by_city_case():
    result = main.filter_by_city(get_data(), city="CHICAGO")
    vals = [p["city"] for p in result]
    assert vals == ["Chicago"]

def test_filter_by_city():
    result = main.filter_by_city(get_data(), city="Chicago")
    vals = [p["city"] for p in result]
    assert vals == ["Chicago"]

def test_filter_by_city_notfound():
    result = main.filter_by_city(get_data(), "Detroit")
    vals = [p["city"] for p in result]
    assert vals == []

def test_filter_by_city_is_blank():
    result = main.filter_by_city(get_data(), city='')
    assert len(result) == 3


def test_filter_by_name_exists():
    result = main.filter_by_name(get_data(), name="John Doe")
    vals = [p["name"] for p in result]
    assert vals == ["John Doe"]

def test_filter_by_name_notfound():
    result = main.filter_by_name(get_data(), name="Ben Dover")
    vals = [p["name"] for p in result]
    assert vals == []

def test_filter_by_name_is_blank():
    result = main.filter_by_name(get_data(), name='')
    assert len(result) == 3

def test_fiter_data_empty():
    result = main.filter_data(age='',name='',city='')
    vals = [p["name"] for p in result]
    assert vals == []

def test_filter_data_with_name():
    result = main.filter_data(name="John Doe", data_to_filter=get_data())
    vals = [p["name"] for p in result]
    assert vals == ["John Doe"]

def test_filter_data_with_age():
    result = main.filter_data(age=10, data_to_filter=get_data())
    vals = [p["name"] for p in result]
    assert len(vals) == 3

def test_filter_data_with_city():
    result = main.filter_data(city="Chicago", data_to_filter=get_data())
    vals = [p["city"] for p in result]
    assert vals == ["Chicago"]

def test_filter_with_all():
    result = main.filter_data(age=40, name="Jim Beam", city="Chicago", data_to_filter=get_data())
    vals = [p["name"] for p in result]
    assert vals == ["Jim Beam"]

def test_filter_with_name_city():
    result = main.filter_data(name="Jim Beam", city="Chicago", data_to_filter=get_data())
    vals = [p["name"] for p in result]
    assert vals == ["Jim Beam"]

def test_filter_with_age_city():
    result = main.filter_data(age=40, city="Chicago", data_to_filter=get_data())
    vals = [p["name"] for p in result]
    assert vals == ["Jim Beam"]

def test_filter_with_age_name():
    result = main.filter_data(age=40, name="Jim Beam", data_to_filter=get_data())
    vals = [p["name"] for p in result]
    assert vals == ["Jim Beam"]

def test_load_data_success(tmp_path):
    """Test that valid JSON data is loaded correctly."""
    test_data = {"people": [{"name": "Fred", "age":30, "city": "Dallas"}]}               
    file_path = tmp_path / "test.json"

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(test_data, f)
    
    result = main.load_data(file_path)
    assert result == test_data

def test_load_data_invalid_json(tmp_path):
    """Test that a JSONDecodeError is returned when the file contains invalid JSON. """
    test_data = "I am not data"
    file_path = tmp_path / "test.json"

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(test_data)
    
    result = main.load_data(file_path)
    assert isinstance(result, json.JSONDecodeError)

def test_load_data_file_not_found(tmp_path):
    """Test that a FileNotFoundError is raised if the file doesn't exist."""
    with pytest.raises(FileNotFoundError):
        main.load_data("this_file_does_not_exist.json")