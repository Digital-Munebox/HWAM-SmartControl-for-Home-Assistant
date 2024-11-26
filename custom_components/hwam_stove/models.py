"""Data models for HWAM Smart Control."""
from dataclasses import dataclass
import datetime
from typing import List, Optional

@dataclass
class AlarmState:
    """Represents alarm state of the stove."""
    maintenance_alarms: int = 0
    safety_alarms: int = 0
    refill_alarm: bool = False
    remote_refill_alarm: bool = False
    remote_refill_beeps: int = 0

    def has_alarms(self) -> bool:
        """Check if any alarm is active."""
        return (self.maintenance_alarms > 0 or 
                self.safety_alarms > 0 or 
                self.refill_alarm or 
                self.remote_refill_alarm)

    def get_active_alarms(self) -> List[str]:
        """Get list of active alarms."""
        alarms = []
        if self.maintenance_alarms:
            alarms.append("Maintenance nécessaire")
        if self.safety_alarms:
            alarms.append("Alarme de sécurité")
        if self.refill_alarm:
            alarms.append("Rechargement nécessaire")
        if self.remote_refill_alarm:
            alarms.append("Alarme rechargement distant")
        return alarms

@dataclass
class StoveState:
    """Represents operational state of the stove."""
    phase: int
    burn_level: int
    operation_mode: int
    door_open: bool
    updating: bool
    night_lowering: bool
    
    @property
    def is_active(self) -> bool:
        """Check if stove is actively burning."""
        return self.phase in [1, 2, 3]  # Allumage, Démarrage, Combustion

@dataclass
class StoveData:
    """Complete stove data model."""
    # System info
    algorithm: str
    firmware_version: str
    wifi_version: str
    remote_version: str
    service_date: datetime.date
    
    # State
    state: StoveState
    alarms: AlarmState
    
    # Measurements
    stove_temperature: float
    room_temperature: float
    oxygen_level: float
    
    # Valve positions
    valve1_position: int
    valve2_position: int
    valve3_position: int
    
    # Timing
    night_begin_time: datetime.time
    night_end_time: datetime.time
    current_datetime: datetime.datetime
    time_since_remote_msg: datetime.time
    new_fire_wood_time: datetime.time

    @staticmethod
    def from_dict(data: dict) -> 'StoveData':
        """Create StoveData instance from API response dictionary."""
        try:
            return StoveData(
                algorithm=data["algorithm"],
                firmware_version=f"{data['version_major']}.{data['version_minor']}.{data['version_build']}",
                wifi_version=f"{data['wifi_version_major']}.{data['wifi_version_minor']}.{data['wifi_version_build']}",
                remote_version=f"{data['remote_version_major']}.{data['remote_version_minor']}.{data['remote_version_build']}",
                service_date=datetime.datetime.strptime(data["service_date"], "%Y-%m-%d").date(),
                
                state=StoveState(
                    phase=data["phase"],
                    burn_level=data["burn_level"],
                    operation_mode=data["operation_mode"],
                    door_open=data["door_open"] == 1,
                    updating=data["updating"] == 1,
                    night_lowering=data["night_lowering"] == 1
                ),
                
                alarms=AlarmState(
                    maintenance_alarms=data["maintenance_alarms"],
                    safety_alarms=data["safety_alarms"],
                    refill_alarm=data["refill_alarm"] == 1,
                    remote_refill_alarm=data["remote_refill_alarm"] == 1,
                    remote_refill_beeps=data["remote_refill_beeps"]
                ),
                
                stove_temperature=round(data["stove_temperature"] / 100, 1),
                room_temperature=round(data["room_temperature"] / 100, 1),
                oxygen_level=round(data["oxygen_level"] / 100, 1),
                
                valve1_position=data["valve1_position"],
                valve2_position=data["valve2_position"],
                valve3_position=data["valve3_position"],
                
                night_begin_time=datetime.time(
                    hour=data["night_begin_hour"],
                    minute=data["night_begin_minute"]
                ),
                night_end_time=datetime.time(
                    hour=data["night_end_hour"],
                    minute=data["night_end_minute"]
                ),
                current_datetime=datetime.datetime(
                    year=data["year"],
                    month=data["month"],
                    day=data["day"],
                    hour=data["hours"],
                    minute=data["minutes"],
                    second=data["seconds"]
                ),
                time_since_remote_msg=data["time_since_remote_msg"],
                new_fire_wood_time=datetime.time(
                    hour=data["new_fire_wood_hours"],
                    minute=data["new_fire_wood_minutes"]
                )
            )
        except KeyError as e:
            raise ValueError(f"Missing required field in data: {e}")
        except Exception as e:
            raise ValueError(f"Error parsing stove data: {e}")
