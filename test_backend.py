from backend import get_tiles, get_coordinates, get_data, get_tile_id, get_tile_rotation
import pytest

@pytest.mark.parametrize("map_name", ["test_1", "test_2", "test_3"])
def test_get_coordinates_returns_list(map_name):
    """Test that get_coordinates() returns a list for each map."""
    data = get_data("maps/" + map_name + ".json") 
    coordinates = get_coordinates(data)
    assert isinstance(coordinates, list)
    
 
# Set of tests checking the structure of read JSON file (supposed to come from Tiled 1.2)   
def test_map_returns_correct_data_list():
    """Take JSON file with test_1 map and assert correct data list.
    
    If the test_1.json map is changed or removed, the test needs to be updated."""
    data = get_data("maps/test_1.json")
    assert data["layers"][0]["data"] == [2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 1, 2, 1, 1, 1, 1, 1, 1, 1, 1, 2, 1, 1, 2, 1, 1, 1, 1, 1, 1, 1, 2, 1, 1, 1, 2, 1, 1, 1, 1, 1, 1, 2, 1, 1, 1, 1, 2, 1, 1, 1, 1, 1, 2, 1, 1, 1, 1, 1, 2, 1, 1, 1, 1, 2, 1, 1, 1, 1, 1, 1, 2, 1, 1, 1, 2, 1, 1, 1, 1, 1, 1, 1, 2, 1, 1, 2, 1, 1, 1, 1, 1, 1, 1, 1, 2, 1, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2]

      
@pytest.mark.parametrize(("id_number", "expected_value"), 
                           [(0, 0),
                           (2, 2),
                           (4, 6),
                           (6, 9), 
                           (13, 16),]) 
def test_map_returns_correct_image_ID(id_number, expected_value):
    """Take JSON file with test_1 map and assert correct image ID.
    
    If the test_1.json map is changed or removed, the test needs to be updated."""
    data = get_data("maps/test_1.json")
    assert data["tilesets"][0]["tiles"][id_number]["id"] == expected_value 
    
    
@pytest.mark.parametrize(("id_number", "expected_value"), 
                           [(0, "../img/squares/png/ground.png"),
                           (2, "../img/squares/png/laser_1_base.png"),
                           (4, "../img/squares/png/gear_r.png"),
                           (6, "../img/squares/png/pusher_1_3_5.png"), 
                           (13, "../img/squares/png/laser_2.png"),]) 
def test_map_returns_correct_image_path(id_number, expected_value):
    """Take JSON file with test_1 map and assert correct image path.
    
    If the test_1.json map is changed or removed, the test needs to be updated."""
    data = get_data("maps/test_1.json")
    assert data["tilesets"][0]["tiles"][id_number]["image"] == expected_value 
    
    
def test_get_tiles_instance():
    """ Take JSON file with test_3 map and assert correct tilelist is returned.
    
    If the test_3.json map is changed or removed, the test needs to be updated."""
    
    data = get_data("maps/test_3.json")
    tilelist = get_tiles(data)
    assert isinstance(tilelist, dict)
    assert isinstance(tilelist[1], list) 
    
@pytest.mark.parametrize(("input_number", "converted_number"),
                         [(1, 1),
                         (2684354573, 13),
                         (2684354584, 24),
                         (1610612749, 13)])
def test_convert_tile_id(input_number, converted_number):
    assert get_tile_id(input_number) == converted_number
    
        
@pytest.mark.parametrize(("input_number", "converted_number"),
                         [(1, 0),
                         (2684354573, 10),
                         (2684354584, 10),
                         (1610612749, 6),
                         (3221225497, 12)])
def test_convert_tile_rotation(input_number, converted_number):
    assert get_tile_rotation(input_number) == converted_number



