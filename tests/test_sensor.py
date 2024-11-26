"""Tests for the HWAM Smart Control sensors."""
import pytest
from unittest.mock import AsyncMock, Mock, patch

from homeassistant.const import TEMP_CELSIUS, PERCENTAGE
from homeassistant.components.sensor import SensorDeviceClass

from custom_components.hwam_stove.sensor import HWAMSensor
from custom_components.hwam_stove.models import StoveData, StoveState, AlarmState

@pytest.fixture
def mock_coordinator():
    """Create a mock coordinator."""
    coordinator = Mock()
    coordinator.data = StoveData(
        algorithm="test",
        firmware_version="1.0.0",
        wifi_version="1.0.0",
        remote_version="1.0.0",
        service_date="2024-01-01",
        state=StoveState(
            phase=3,
            burn_level=2,
            operation_mode=2,
            door_open=False,
            updating=False,
            night_lowering=False
        ),
        alarms=AlarmState(),
        stove_temperature=120.0,
        room_temperature=21.0,
        oxygen_level=20.0,
        valve1_position=50,
        valve2_position=60,
        valve3_position=70,
        night_begin_time="22:00",
        night_end_time="06:00",
        current_datetime="2024-01-01 12:00:00",
        time_since_remote_msg="00:05",
        new_fire_wood_time="01:30"
    )
    return coordinator

def test_temperature_sensor(mock_coordinator):
    """Test the temperature sensor."""
    description = Mock(
        key="stove_temperature",
        name="Température du poêle",
        native_unit_of_measurement=TEMP_CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
    )

    sensor = HWAMSensor(
        coordinator=mock_coordinator,
        entry_id="test_entry",
        device_id="test_device",
        entity_description=description,
    )

    assert sensor.native_value == 120.0
    assert sensor.native_unit_of_measurement == TEMP_CELSIUS
    assert sensor.device_class == SensorDeviceClass.TEMPERATURE

def test_oxygen_sensor(mock_coordinator):
    """Test the oxygen sensor."""
    description = Mock(
        key="oxygen_level",
        name="Niveau d'oxygène",
        native_unit_of_measurement=PERCENTAGE,
    )

    sensor = HWAMSensor(
        coordinator=mock_coordinator,
        entry_id="test_entry",
        device_id="test_device",
        entity_description=description,
    )

    assert sensor.native_value == 20.0
    assert sensor.native_unit_of_measurement == PERCENTAGE

def test_phase_sensor(mock_coordinator):
    """Test the phase sensor."""
    description = Mock(
        key="phase",
        name="Phase de combustion",
    )

    sensor = HWAMSensor(
        coordinator=mock_coordinator,
        entry_id="test_entry",
        device_id="test_device",
        entity_description=description,
    )

    assert sensor.native_value == "Combustion"
