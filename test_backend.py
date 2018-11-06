from backend import get_tiles, get_coordinates, get_data
import pytest

# Test that get_tiles() returns value under key 'data' of the 0th element of the
# array under key 'layers', no matter what it actually is.
# This is just a simple test to try it out, not particularly useful.
@pytest.mark.parametrize('x', [3, 'asd', (1, 'bl', 7)])  
def test_get_tiles(x):
    data = {'layers' : [{'data' : x}]}
    assert get_tiles(data) == x

# Test that get_coordinates() returns a list for each map.
@pytest.mark.parametrize('map_name', ['test_1', 'test_2', 'test_3'])
def test_get_coordinates_returns_list(map_name):
    data = get_data('maps/' + map_name + '.json') 
    coordinates = get_coordinates(data)
    assert isinstance(coordinates, list) 
