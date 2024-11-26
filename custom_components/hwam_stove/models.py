"""Data models for HWAM Smart Control."""
from datetime import datetime, date, time, timedelta
from typing import List, Optional
import logging
from pydantic import BaseModel, validator, Field

_LOGGER = logging.getLogger(__name__)

class AlarmState(BaseModel):
    """Représentation des états d'alarme."""
    maintenance_alarms: int = Field(default=0, ge=0)
    safety_alarms: int = Field(default=0, ge=0)
    refill_alarm: bool = False
    remote_refill_alarm: bool = False
    remote_refill_beeps: int = Field(default=0, ge=0)

    def has_alarms(self) -> bool:
        """Vérifie si des alarmes sont actives."""
        return (self.maintenance_alarms > 0 or 
                self.safety_alarms > 0 or 
                self.refill_alarm or 
                self.remote_refill_alarm)

    def get_active_alarms(self) -> List[str]:
        """Récupère la liste des alarmes actives."""
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

    @validator('maintenance_alarms', 'safety_alarms')
    def validate_alarm_count(cls, v):
        """Validation du nombre d'alarmes."""
        if v < 0:
            raise ValueError("Le nombre d'alarmes ne peut pas être négatif")
        return v

class StoveState(BaseModel):
    """État opérationnel du poêle."""
    phase: int = Field(..., ge=1, le=5)
    burn_level: int = Field(..., ge=0, le=5)
    operation_mode: int = Field(..., ge=0, le=10)
    door_open: bool = False
    updating: bool = False
    night_lowering: bool = False

    @property
    def is_active(self) -> bool:
        """Vérifie si le poêle est en combustion active."""
        return self.phase in [1, 2, 3]  # Allumage, Démarrage, Combustion

    @validator('phase')
    def validate_phase(cls, v):
        """Validation de la phase."""
        valid_phases = {1, 2, 3, 4, 5}
        if v not in valid_phases:
            raise ValueError(f"Phase invalide: {v}")
        return v

    @validator('burn_level')
    def validate_burn_level(cls, v):
        """Validation du niveau de combustion."""
        if not 0 <= v <= 5:
            raise ValueError(f"Niveau de combustion invalide: {v}")
        return v

class TemperatureData(BaseModel):
    """Données de température avec validation."""
    stove_temperature: float = Field(..., ge=0, le=800)
    room_temperature: float = Field(..., ge=-20, le=50)
    oxygen_level: float = Field(..., ge=0, le=100)

    @validator('stove_temperature')
    def validate_stove_temp(cls, v):
        """Validation de la température du poêle."""
        if v > 600:
            _LOGGER.warning("Température du poêle très élevée: %s°C", v)
        return v

class StoveData(BaseModel):
    """Modèle complet des données du poêle."""
    # Informations système
    algorithm: str
    firmware_version: str
    wifi_version: str
    remote_version: str
    service_date: date

    # États
    state: StoveState
    alarms: AlarmState
    temperatures: TemperatureData

    # Positions des valves
    valve1_position: int = Field(..., ge=0, le=100)
    valve2_position: int = Field(..., ge=0, le=100)
    valve3_position: int = Field(..., ge=0, le=100)

    # Données temporelles
    night_begin_time: time
    night_end_time: time
    current_datetime: datetime
    time_since_remote_msg: timedelta
    new_fire_wood_time: timedelta

    class Config:
        """Configuration Pydantic."""
        validate_assignment = True
        arbitrary_types_allowed = True

    @classmethod
    def from_dict(cls, data: dict) -> 'StoveData':
        """Crée une instance StoveData à partir d'un dictionnaire."""
        try:
            # Traitement des températures
            temperatures = TemperatureData(
                stove_temperature=data["stove_temperature"] / 100,
                room_temperature=data["room_temperature"] / 100,
                oxygen_level=data["oxygen_level"] / 100,
            )

            # État du poêle
            state = StoveState(
                phase=data["phase"],
                burn_level=data["burn_level"],
                operation_mode=data["operation_mode"],
                door_open=data["door_open"] == 1,
                updating=data["updating"] == 1,
                night_lowering=data["night_lowering"] == 1
            )

            # État des alarmes
            alarms = AlarmState(
                maintenance_alarms=data["maintenance_alarms"],
                safety_alarms=data["safety_alarms"],
                refill_alarm=data["refill_alarm"] == 1,
                remote_refill_alarm=data["remote_refill_alarm"] == 1,
                remote_refill_beeps=data["remote_refill_beeps"]
            )

            # Construction de l'instance complète
            return cls(
                algorithm=data["algorithm"],
                firmware_version=f"{data['version_major']}.{data['version_minor']}.{data['version_build']}",
                wifi_version=f"{data['wifi_version_major']}.{data['wifi_version_minor']}.{data['wifi_version_build']}",
                remote_version=f"{data['remote_version_major']}.{data['remote_version_minor']}.{data['remote_version_build']}",
                service_date=datetime.strptime(data["service_date"], "%Y-%m-%d").date(),
                state=state,
                alarms=alarms,
                temperatures=temperatures,
                valve1_position=data["valve1_position"],
                valve2_position=data["valve2_position"],
                valve3_position=data["valve3_position"],
                night_begin_time=time(
                    hour=data["night_begin_hour"],
                    minute=data["night_begin_minute"]
                ),
                night_end_time=time(
                    hour=data["night_end_hour"],
                    minute=data["night_end_minute"]
                ),
                current_datetime=datetime(
                    year=data["year"],
                    month=data["month"],
                    day=data["day"],
                    hour=data["hours"],
                    minute=data["minutes"],
                    second=data["seconds"]
                ),
                time_since_remote_msg=timedelta(
                    hours=data["time_since_remote_msg"].hour,
                    minutes=data["time_since_remote_msg"].minute
                ),
                new_fire_wood_time=timedelta(
                    hours=data["new_fire_wood_hours"],
                    minutes=data["new_fire_wood_minutes"]
                )
            )

        except KeyError as e:
            raise ValueError(f"Donnée manquante dans la réponse API: {e}")
        except (ValueError, TypeError) as e:
            raise ValueError(f"Erreur de conversion des données: {e}")
        except Exception as e:
            raise ValueError(f"Erreur inattendue lors du parsing: {e}")

    def to_dict(self) -> dict:
        """Convertit l'instance en dictionnaire."""
        return self.dict(by_alias=True)
