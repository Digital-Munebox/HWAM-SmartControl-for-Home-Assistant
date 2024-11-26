"""Test the HWAM models."""
import pytest
from datetime import datetime

from custom_components.hwam_stove.models import StoveData

def test_stove_data_creation(mock_stove_data):
    """Test creating StoveData object."""
    data = StoveData.from_dict(mock_stove_data)
    assert data.temperatures.stove_temperature == 245.0
    assert data.temperatures.room_temperature == 21.0
    assert data.temperatures.oxygen_level == 20.0
    assert data.state.phase == 3
    assert data.state.burn_level == 2
    assert data.state.operation_mode == 2
    assert not data.state.door_open

def test_stove_data_validation():
    """Test StoveData validation."""
    invalid_data = mock_stove_data.copy()
    invalid_data["stove_temperature"] = 90000  # 900°C
    
    with pytest.raises(ValueError):
        StoveData.from_dict(invalid_data)

def test_alarm_state():
    """Test alarm state handling."""
    data = StoveData.from_dict(mock_stove_data)
    assert not data.alarms.has_alarms()
    assert len(data.alarms.get_active_alarms()) == 0
