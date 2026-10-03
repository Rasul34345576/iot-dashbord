"""Ревью кезінде табылған әлсіз жерлерді жабатын қосымша тесттер."""

import pytest

from app.core.domain import Event, FrozenDict, Location, Reading, Rule
from app.core.recursion import collect_descendant_locations
from app.core.transforms import (
    calibrated_readings,
    readings_in_range,
    readings_stats,
    sort_readings,
)


# Rule.payload енді өзгертуге болмайтын FrozenDict екенін тексереді.
def test_rule_payload_is_immutable():
    """dict берсек те, Rule ішінде payload өзгертілмейді және hash-талады."""

    source = {"sensor": "temp", "min": 18, "max": 26}
    rule = Rule("rule1", "range", source)
    source["min"] = 0  # Сыртқы dict өзгерсе де, Rule-ға әсер етпейді.
    assert rule.payload["min"] == 18
    assert isinstance(rule.payload, FrozenDict)
    with pytest.raises(TypeError):
        rule.payload["min"] = 0  # type: ignore[index]
    assert isinstance(hash(rule), int)


# Event моделі де immutable екенін тексереді.
def test_event_is_frozen():
    """Event атрибутын өзгерту FrozenInstanceError береді."""

    event = Event("e1", "2025-03-01T00:00:00", "READING", {"value": 21.0})
    assert event.payload["value"] == 21.0
    with pytest.raises(AttributeError):
        event.name = "ALERT_RAISED"  # type: ignore[misc]


# Циклі бар (бұзылған) иерархияда рекурсия шексіз кетпейтінін тексереді.
def test_collect_descendants_cycle_guard():
    """a -> b -> a циклінде әр id бір-ақ рет қайтады."""

    cyclic = (Location("a", "A", "b"), Location("b", "B", "a"))
    assert collect_descendant_locations(cyclic, "a") == ("a", "b")


# Белгісіз sensor_id кезінде функциялар құламайтынын тексереді.
def test_unknown_sensor_does_not_crash(sensors):
    """Сенсоры жоқ Reading калибрленбейді және статистикаға кірмейді."""

    orphan = (Reading("x1", "unknown", "2025-03-01T00:00:00", 10.0),)
    assert calibrated_readings(orphan, sensors)[0].value == 10.0
    assert readings_stats(orphan, sensors, "temp")["count"] == 0


# readings_in_range шекараларды қоса есептейтінін тексереді.
def test_readings_in_range_inclusive(readings):
    """low/high шекара мәндері нәтижеге кіреді; бос диапазон — бос tuple."""

    assert len(readings_in_range(readings, 20.0, 22.0)) == 2
    assert readings_in_range(readings, 100.0, 200.0) == ()


# sort_readings қате өріс берілгенде KeyError беретінін тексереді.
def test_sort_readings_invalid_field(readings):
    """Белгісіз 'by' мәні үнсіз өтпей, KeyError көтереді."""

    with pytest.raises(KeyError):
        sort_readings(readings, "unknown")
