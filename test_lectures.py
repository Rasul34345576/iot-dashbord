"""1-4 дәріс тақырыптарына арналған қосымша тесттер."""

from functools import partial

import pytest

from app.core.compose import compose, curry2, logged, pipe, timed, type_checked
from app.core.transforms import (
    aggregate_data,
    avg_by_sensor,
    filter_data,
    in_range,
    sort_readings,
    top_n_readings,
    transform_data,
)


# compose оңнан солға, pipe солдан оңға жұмыс істейтінін тексереді.
def test_compose_and_pipe():
    """Функцияларды біріктіру реті дұрыс нәтиже береді."""

    def double(value):
        """Санды екіге көбейтеді."""

        return value * 2

    def inc(value):
        """Санға бірді қосады."""

        return value + 1

    assert compose(double, inc)(3) == 8
    assert pipe(3, inc, double) == 8


# curry2 және functools.partial аргумент бекітетінін тексереді.
def test_curry2_and_partial():
    """Каррирование мен partial бір аргументті алдын ала сақтайды."""

    def add(left, right):
        """Екі санды қосады."""

        return left + right

    assert curry2(add)(2)(5) == 7
    assert partial(add, 2)(5) == 7


# timed нәтиже мен миллисекундты қайтаратынын тексереді.
def test_timed_returns_result_and_ms():
    """timed print жасамай, нәтиже мен уақыт tuple-ын береді."""

    result, elapsed_ms = timed(lambda value: value + 1)(4)
    assert result == 5
    assert elapsed_ms >= 0


# logged sink арқылы шақыру атауын жазатынын тексереді.
def test_logged_uses_injected_sink():
    """Лог сыртқы sink-ке жазылады, сондықтан тестте list қолданылады."""

    messages = []

    @logged(messages.append)
    def add_one(value):
        """Тест ішіндегі қарапайым функция."""

        return value + 1

    assert add_one(3) == 4
    assert messages == ["add_one"]


# type_checked дұрыс емес нәтиже типінде TypeError көтеретінін тексереді.
def test_type_checked_raises_type_error():
    """Decorator нәтиже келісімшартын тексереді."""

    @type_checked(int)
    def as_text():
        """Әдейі қате тип қайтаратын функция."""

        return "қате"

    with pytest.raises(TypeError):
        as_text()


# filter/transform/aggregate тізбегі бірге қолданылатынын тексереді.
def test_filter_transform_aggregate_pipeline():
    """Сүзу, түрлендіру және жинақтау таза pipeline құрайды."""

    filtered = filter_data((1, 2, 3, 4), lambda value: value % 2 == 0)
    transformed = transform_data(filtered, lambda value: value * 10)
    assert aggregate_data(transformed, lambda left, right: left + right) == 60


# in_range замыканиесі value шекарасын есте сақтайтынын тексереді.
def test_in_range_closure(readings):
    """low/high мәндері closure ішінде сақталып, Reading.value тексереді."""

    predicate = in_range(19.0, 21.0)
    assert predicate(readings[0]) is True
    assert predicate(readings[2]) is False


# sort_readings жаңа tuple беріп, бастапқы tuple-ды өзгертпейтінін тексереді.
def test_sort_readings_without_mutation(readings):
    """value бойынша сұрыптау бастапқы readings ретін өзгертпейді."""

    result = sort_readings(readings, "value", reverse=True)
    assert tuple(map(lambda reading: reading.id, result)) == ("r4", "r2", "r3", "r1")
    assert tuple(map(lambda reading: reading.id, readings)) == ("r1", "r2", "r3", "r4")


# top_n ең үлкен value көрсеткіштерін қайтаратынын тексереді.
def test_top_n_readings(readings):
    """Top-n функциясы value бойынша кему ретімен алғашқы n алады."""

    result = top_n_readings(readings, 2)
    assert tuple(map(lambda reading: reading.id, result)) == ("r4", "r2")


# avg_by_sensor sensor_id бойынша орташа мән есептейтінін тексереді.
def test_avg_by_sensor(readings):
    """Әр сенсордың орташа мәні tuple[(sensor_id, avg)] ретінде қайтады."""

    result = dict(avg_by_sensor(readings))
    assert result["s1"] == 20.0
    assert result["s4"] == 55.0
