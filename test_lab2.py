"""Лаб 2 үшін lambda, closure және рекурсия тесттері."""

from app.core.recursion import (
    collect_descendant_locations,
    find_sensors_in_location,
    nest_readings_by_day,
)
from app.core.transforms import (
    all_of,
    by_location,
    by_sensor_kind,
    by_time_range,
    select,
)


# by_sensor_kind тек таңдалған kind көрсеткіштерін өткізетінін тексереді.
def test_by_sensor_kind_filters_temperature(readings, sensors):
    """Температура предикаты s1 және s3 көрсеткіштерін ғана қалдырады."""

    result = select(readings, by_sensor_kind("temp", sensors))
    assert tuple(map(lambda reading: reading.id, result)) == ("r1", "r3")


# by_time_range шекара уақыттарын қоса алатынын тексереді.
def test_by_time_range_includes_edges(readings):
    """Уақыт аралығы start және end мәндерін қоса сүзеді."""

    result = select(
        readings, by_time_range("2025-03-01T00:00:00", "2025-03-01T01:00:00")
    )
    assert tuple(map(lambda reading: reading.id, result)) == ("r1", "r2")


# by_location иерархиядағы ішкі бөлмелерді ескеретінін тексереді.
def test_by_location_uses_hierarchy(locations, devices, sensors, readings):
    """c1 таңдалғанда r1 және r2 бөлмелеріндегі сенсорлар табылады."""

    result = select(readings, by_location("c1", locations, devices, sensors))
    assert tuple(map(lambda reading: reading.id, result)) == ("r1", "r2", "r3")


# Екі closure бір-бірінен тәуелсіз мән сақтайтынын тексереді.
def test_independent_closures(readings, sensors):
    """temp және hum closure-лары өз kind мәндерін бөлек есте сақтайды."""

    temp_predicate = by_sensor_kind("temp", sensors)
    hum_predicate = by_sensor_kind("hum", sensors)
    assert temp_predicate(readings[0]) is True
    assert temp_predicate(readings[1]) is False
    assert hum_predicate(readings[1]) is True


# all_of бірнеше предикатты бірге қолданатынын тексереді.
def test_all_of_combines_predicates(readings, sensors):
    """kind және уақыт шарттары бірге орындалғанда ғана Reading өтеді."""

    predicate = all_of(
        by_sensor_kind("temp", sensors),
        by_time_range("2025-03-02T00:00:00", "2025-03-03T00:00:00"),
    )
    result = select(readings, predicate)
    assert tuple(map(lambda reading: reading.id, result)) == ("r3",)


# collect_descendant_locations root және барлық ұрпақты қайтаратынын тексереді.
def test_collect_descendant_locations(locations):
    """c1 үшін root, ғимарат, қабат және екі бөлме қайтады."""

    result = collect_descendant_locations(locations, "c1")
    assert result == ("c1", "b1", "f1", "r1", "r2")


# find_sensors_in_location локациядағы сенсорларды табатынын тексереді.
def test_find_sensors_in_location(locations, devices, sensors):
    """c1 тармағында d1 және d2 құрылғыларының сенсорлары табылады."""

    result = find_sensors_in_location(locations, devices, sensors, "c1")
    assert tuple(map(lambda sensor: sensor.id, result)) == ("s1", "s2", "s3")


# nest_readings_by_day күн бойынша топтайтынын тексереді.
def test_nest_readings_by_day(readings):
    """Әр күн бөлек tuple тобына жиналады."""

    result = nest_readings_by_day(readings)
    assert tuple(map(lambda item: item[0], result)) == (
        "2025-03-01",
        "2025-03-02",
        "2025-03-03",
    )
    assert len(result[0][1]) == 2


# nest_readings_by_day бос кірісте бос tuple қайтаратынын тексереді.
def test_nest_readings_by_day_empty():
    """Бос readings tuple рекурсияның базалық жағдайын тексереді."""

    assert nest_readings_by_day(()) == ()
