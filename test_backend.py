from backend import get_tiles, get_coordinates, get_data
import pytest

@pytest.mark.parametrize('map_name', ['test_1', 'test_2', 'test_3'])
def test_get_coordinates_returns_list(map_name):
    """Test that get_coordinates() returns a list for each map."""
    data = get_data('maps/' + map_name + '.json') 
    coordinates = get_coordinates(data)
    assert isinstance(coordinates, list)
