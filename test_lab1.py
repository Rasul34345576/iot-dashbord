"""Лаб 1 үшін таза функциялар мен өзгермейтіндік тесттері."""

from dataclasses import FrozenInstanceError

import pytest

from app.core.domain import Reading
from app.core.transforms import (
    add_reading,
    apply_calibration,
    calibrated_readings,
    load_seed,
    readings_stats,
)


# Frozen dataclass өрісі өзгермейтінін тексереді.
def test_frozen_sensor_rejects_mutation(sensors):
    """Sensor frozen болғандықтан өріс ауыстыру FrozenInstanceError береді."""

    with pytest.raises(FrozenInstanceError):
        sensors[0].calibration = 9.0


# add_reading бастапқы tuple-ды өзгертпейтінін тексереді.
def test_add_reading_returns_new_tuple(readings):
    """Жаңа Reading қосылған tuple қайтады, бастапқы readings өзгермейді."""

    new_reading = Reading("r-new", "s1", "2025-03-04T00:00:00", 21.0)
    result = add_reading(readings, new_reading)
    assert len(readings) == 4
    assert len(result) == 5
    assert result[-1] == new_reading


# apply_calibration тек керек сенсорды өзгертетінін тексереді.
def test_apply_calibration_changes_only_matching_sensor(sensors):
    """Тек s1 calibration мәні жаңа объект арқылы өзгереді."""

    result = apply_calibration(sensors, "s1", 1.0)
    assert result[0].calibration == 1.5
    assert result[1:] == sensors[1:]
    assert sensors[0].calibration == 0.5


# apply_calibration белгісіз sensor_id кезінде tuple мазмұнын сақтайтынын тексереді.
def test_apply_calibration_unknown_sensor_keeps_values(sensors):
    """Белгісіз id ешбір сенсорды өзгертпейді."""

    result = apply_calibration(sensors, "missing", 1.0)
    assert result == sensors
    assert result is not sensors


# readings_stats temp көрсеткіштері үшін min/max/avg/count есептейтінін тексереді.
def test_readings_stats_for_temperature(readings, sensors):
    """Температура статистикасы sensors арқылы kind тауып есептеледі."""

    stats = readings_stats(readings, sensors, "temp")
    assert stats == {"min": 20.0, "max": 22.0, "avg": 21.0, "count": 2}


# readings_stats бос жинақта None және count=0 қайтаратынын тексереді.
def test_readings_stats_empty(readings, sensors):
    """Сәйкес kind жоқ болса, бос статистика қайтады."""

    stats = readings_stats(readings, sensors, "pressure")
    assert stats == {"min": None, "max": None, "avg": None, "count": 0}


# calibrated_readings бастапқы Reading мәндерін өзгертпейтінін тексереді.
def test_calibrated_readings_projects_new_values(readings, sensors):
    """Калибрленген tuple жаңа мәндер береді, бастапқы tuple өзгермейді."""

    result = calibrated_readings(readings, sensors)
    assert result[0].value == 20.5
    assert result[2].value == 21.8
    assert readings[0].value == 20.0


# load_seed талаптағы көлемнен кем емес дерек оқитынын тексереді.
def test_load_seed_volume():
    """seed.json tuple бөлімдерін және талаптағы минимум көлемді тексереді."""

    locations, devices, sensors, readings, rules, alerts = load_seed("data/seed.json")
    room_count = len(tuple(filter(lambda location: "-r" in location.id, locations)))
    assert room_count >= 12
    assert len(devices) >= 8
    assert len(sensors) >= 20
    assert len(readings) >= 1000
    assert len(rules) >= 5
    assert len(alerts) == 2
