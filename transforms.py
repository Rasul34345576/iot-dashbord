"""Лаб 1-2 және Дәріс 1-4 үшін таза түрлендіру функциялары.

Модуль seed.json-ды домен модельдеріне айналдырады және климат көрсеткіштерін
map/filter/reduce, lambda, замыкание және жоғары ретті функциялар арқылы өңдейді.
Барлық функция кіріс tuple-дарын өзгертпей, жаңа tuple немесе жаңа dict қайтарады.
"""

from __future__ import annotations

import json
from dataclasses import replace
from functools import reduce
from pathlib import Path
from typing import Callable, Iterable, TypeVar

from app.core.domain import Alert, Device, Location, Reading, Rule, Sensor
from app.core.recursion import collect_descendant_locations

T = TypeVar("T")
U = TypeVar("U")


def _to_locations(items: Iterable[dict]) -> tuple[Location, ...]:
    """JSON dict тізімін Location tuple-ына айналдырады.

    Кіріс iterable dict болады, шығыс жаңа tuple[Location, ...]; tuple бастапқы
    деректі өзгертпеу үшін таңдалды.
    """

    return tuple(map(lambda item: Location(**item), items))  # Дәріс 2: map + lambda.


def _to_devices(items: Iterable[dict]) -> tuple[Device, ...]:
    """JSON dict тізімін Device tuple-ына айналдырады.

    Кіріс iterable dict, шығыс жаңа tuple[Device, ...]; әр элемент жаңа объект
    ретінде құрылады.
    """

    return tuple(map(lambda item: Device(**item), items))  # Дәріс 2: бірдей түрлендіру.


def _to_sensors(items: Iterable[dict]) -> tuple[Sensor, ...]:
    """JSON dict тізімін Sensor tuple-ына айналдырады.

    Кіріс iterable dict, шығыс жаңа tuple[Sensor, ...]; tuple UI мен тестте
    кездейсоқ мутацияны болдырмайды.
    """

    return tuple(map(lambda item: Sensor(**item), items))  # Дәріс 3: immutable жинақ.


def _to_readings(items: Iterable[dict]) -> tuple[Reading, ...]:
    """JSON dict тізімін Reading tuple-ына айналдырады.

    Кіріс iterable dict, шығыс жаңа tuple[Reading, ...]; Reading-тер бастапқы
    JSON-нан тәуелсіз immutable объектілер болады.
    """

    return tuple(map(lambda item: Reading(**item), items))


def _to_rules(items: Iterable[dict]) -> tuple[Rule, ...]:
    """JSON dict тізімін Rule tuple-ына айналдырады.

    Кіріс iterable dict, шығыс жаңа tuple[Rule, ...]; payload dict Rule ішінде
    FrozenDict-ке айналады, сондықтан ереже толық immutable болады.
    """

    return tuple(map(lambda item: Rule(**item), items))


def _to_alerts(items: Iterable[dict]) -> tuple[Alert, ...]:
    """JSON dict тізімін Alert tuple-ына айналдырады.

    Кіріс iterable dict, шығыс жаңа tuple[Alert, ...]; immutable alert журналы
    есептеулерде өзгермей қалады.
    """

    return tuple(map(lambda item: Alert(**item), items))


def load_seed(
    path: str | Path,
) -> tuple[
    tuple[Location, ...],
    tuple[Device, ...],
    tuple[Sensor, ...],
    tuple[Reading, ...],
    tuple[Rule, ...],
    tuple[Alert, ...],
]:
    """seed.json файлын оқып, барлық бөлімді tuple ретінде қайтарады.

    Кіріс path str немесе Path; шығыс locations, devices, sensors, readings,
    rules, alerts tuple-дарынан тұратын tuple, сондықтан бастапқы JSON өзгермейді.
    """

    data = json.loads(Path(path).read_text(encoding="utf-8"))
    return (
        _to_locations(data["locations"]),
        _to_devices(data["devices"]),
        _to_sensors(data["sensors"]),
        _to_readings(data["readings"]),
        _to_rules(data["rules"]),
        _to_alerts(data["alerts"]),
    )


def add_reading(readings: tuple[Reading, ...], reading: Reading) -> tuple[Reading, ...]:
    """Көрсеткіштерге жаңа Reading қосылған жаңа tuple қайтарады.

    Кіріс readings tuple және бір Reading; шығыс жаңа tuple, бастапқы readings
    өзгермейді.
    """

    return readings + (reading,)  # Дәріс 3: tuple concat мутация жасамайды.


def apply_calibration(
    sensors: tuple[Sensor, ...], sensor_id: str, delta: float
) -> tuple[Sensor, ...]:
    """Берілген сенсордың calibration мәнін жаңа tuple ішінде жаңартады.

    Кіріс sensors tuple, sensor_id және delta; шығыс жаңа tuple[Sensor, ...],
    тек сәйкес сенсор dataclasses.replace арқылы көшіріледі.
    """

    return tuple(
        map(
            lambda sensor: (
                replace(  # Дәріс 3: replace жаңа объект жасайды.
                    sensor, calibration=sensor.calibration + delta
                )
                if sensor.id == sensor_id
                else sensor
            ),
            sensors,
        )
    )


def _sensor_map(sensors: Iterable[Sensor]) -> dict[str, Sensor]:
    """Sensor iterable мәнінен id бойынша іздеу dict жасайды.

    Кіріс Sensor iterable, шығыс dict[str, Sensor]; бұл көмекші құрылым Reading
    ішінде kind жоқ болғандықтан керек.
    """

    return dict(map(lambda sensor: (sensor.id, sensor), sensors))


def _kind_of(sensors_by_id: dict[str, Sensor], sensor_id: str) -> str | None:
    """Сенсор түрін қайтарады; сенсор табылмаса None (KeyError орнына).

    Кіріс id бойынша dict және sensor_id; шығыс "temp"/"hum" немесе None.
    """

    sensor = sensors_by_id.get(sensor_id)
    return None if sensor is None else sensor.kind


def _calibration_of(sensors_by_id: dict[str, Sensor], sensor_id: str) -> float:
    """Сенсор калибровкасын қайтарады; сенсор табылмаса 0.0 (мән өзгермейді).

    Кіріс id бойынша dict және sensor_id; шығыс float.
    """

    sensor = sensors_by_id.get(sensor_id)
    return 0.0 if sensor is None else sensor.calibration


def calibrated_readings(
    readings: tuple[Reading, ...], sensors: tuple[Sensor, ...]
) -> tuple[Reading, ...]:
    """Калибрленген value бар жаңа Reading tuple қайтарады.

    Кіріс readings және sensors tuple; шығыс жаңа tuple[Reading, ...], бастапқы
    Reading объектілері өзгермейді.
    """

    sensors_by_id = _sensor_map(sensors)
    return tuple(
        map(
            lambda reading: replace(  # Дәріс 3: проекцияны immutable түрде жасаймыз.
                reading,
                value=reading.value + _calibration_of(sensors_by_id, reading.sensor_id),
            ),
            readings,
        )
    )  # Сенсоры жоқ Reading үшін calibration=0 → мән өзгермейді (KeyError жоқ).


def readings_stats(
    readings: tuple[Reading, ...], sensors: tuple[Sensor, ...], kind: str
) -> dict[str, float | int | None]:
    """Таңдалған sensor kind үшін min/max/avg/count статистикасын есептейді.

    Кіріс readings, sensors және kind; шығыс dict. Бір reduce қолданылады, бос
    жиынға count=0 және min/max/avg=None қайтарылады.
    """

    sensors_by_id = _sensor_map(sensors)
    values = map(
        lambda reading: reading.value,
        filter(
            lambda reading: _kind_of(sensors_by_id, reading.sensor_id) == kind,
            readings,
        ),
    )
    start = {"min": None, "max": None, "sum": 0.0, "count": 0}
    stats = reduce(
        lambda acc, value: {  # Дәріс 2: accumulator жаңа dict болып жиналады.
            "min": value if acc["min"] is None else min(acc["min"], value),
            "max": value if acc["max"] is None else max(acc["max"], value),
            "sum": acc["sum"] + value,
            "count": acc["count"] + 1,
        },
        values,
        start,
    )
    avg = None if stats["count"] == 0 else stats["sum"] / stats["count"]
    return {
        "min": stats["min"],
        "max": stats["max"],
        "avg": avg,
        "count": stats["count"],
    }


def by_sensor_kind(kind: str, sensors: tuple[Sensor, ...]) -> Callable[[Reading], bool]:
    """Reading kind бойынша сүзетін замыкание-предикат қайтарады.

    Кіріс kind және sensors tuple; шығыс Callable[[Reading], bool]. Замыкание
    sensors_by_id және kind мәндерін есте сақтайды.
    """

    sensors_by_id = _sensor_map(sensors)
    return (
        lambda reading: _kind_of(sensors_by_id, reading.sensor_id) == kind
    )  # Дәріс 4: kind замыкание ішінде сақталады.


def by_location(
    location_id: str,
    locations: tuple[Location, ...],
    devices: tuple[Device, ...],
    sensors: tuple[Sensor, ...],
) -> Callable[[Reading], bool]:
    """Иерархиялық локация бойынша Reading сүзетін предикат қайтарады.

    Кіріс location_id және домен tuple-дары; шығыс Callable[[Reading], bool].
    Замыкание descendant/device/sensor id жиындарын есте сақтайды.
    """

    location_ids = frozenset(collect_descendant_locations(locations, location_id))
    device_ids = frozenset(
        map(
            lambda device: device.id,
            filter(lambda device: device.location_id in location_ids, devices),
        )
    )
    sensor_ids = frozenset(
        map(
            lambda sensor: sensor.id,
            filter(lambda sensor: sensor.device_id in device_ids, sensors),
        )
    )
    return (
        lambda reading: reading.sensor_id in sensor_ids
    )  # Дәріс 4: дайын frozenset іздеуді жылдам және immutable етеді.


def by_time_range(start: str, end: str) -> Callable[[Reading], bool]:
    """ISO-8601 уақыт аралығын қоса тексеретін предикат қайтарады.

    Кіріс start/end жолдары; шығыс Callable[[Reading], bool]. ISO форматы
    лексикографиялық салыстыруға жарайды.
    """

    return (
        lambda reading: start <= reading.ts <= end
    )  # Дәріс 4: start/end мәндері замыканиеде сақталады.


def all_of(*predicates: Callable[[Reading], bool]) -> Callable[[Reading], bool]:
    """Барлық предикат орындалғанда True қайтаратын предикат құрады.

    Кіріс бірнеше Callable; шығыс бір Callable[[Reading], bool]. all() қысқа
    тоқтайды, сондықтан артық тексеріс жасамайды.
    """

    return lambda reading: all(
        map(lambda predicate: predicate(reading), predicates)
    )  # Дәріс 4: HOF арқылы бірнеше шарт біріктіріледі.


def select(
    readings: tuple[Reading, ...], predicate: Callable[[Reading], bool]
) -> tuple[Reading, ...]:
    """Reading tuple ішінен predicate сай элементтерді қайтарады.

    Кіріс readings tuple және Callable; шығыс жаңа tuple[Reading, ...], бастапқы
    tuple өзгермейді.
    """

    return tuple(filter(predicate, readings))  # Дәріс 2: filter таза сүзу жасайды.


def filter_data(data: Iterable[T], condition: Callable[[T], bool]) -> tuple[T, ...]:
    """Кез келген iterable деректі шарт бойынша сүзеді.

    Кіріс data және condition Callable; шығыс tuple[T, ...]. Жалпы функция
    pipeline мысалында қайта қолдануға арналған.
    """

    return tuple(
        filter(condition, data)
    )  # Дәріс 3: filter_data -> transform -> aggregate.


def transform_data(data: Iterable[T], transformer: Callable[[T], U]) -> tuple[U, ...]:
    """Кез келген iterable деректі transformer арқылы түрлендіреді.

    Кіріс data және transformer Callable; шығыс жаңа tuple[U, ...], map бастапқы
    жинақты өзгертпейді.
    """

    return tuple(map(transformer, data))  # Дәріс 2: map бір ережені бәріне қолданады.


def aggregate_data(data: Iterable[T], aggregator: Callable[[T, T], T]) -> T | None:
    """Iterable мәндерін aggregator арқылы бір мәнге жинақтайды.

    Кіріс data және екі аргументті Callable; шығыс T немесе бос кірісте None.
    None бос tuple жағдайын ерекше қате қылмай көрсету үшін қайтарылады.
    """

    items = tuple(data)
    return None if len(items) == 0 else reduce(aggregator, items)


def in_range(low: float, high: float) -> Callable[[Reading], bool]:
    """Reading.value берілген аралықта екенін тексеретін замыкание қайтарады.

    Кіріс low/high float; шығыс Callable[[Reading], bool]. Шекара мәндері
    предикат ішінде есте сақталады.
    """

    return (
        lambda reading: low <= reading.value <= high
    )  # Дәріс 4: low/high замыкание арқылы бекітіледі.


def readings_in_range(
    readings: tuple[Reading, ...], low: float, high: float
) -> tuple[Reading, ...]:
    """Көрсеткіштерді value аралығы бойынша сүзеді.

    Кіріс readings tuple және low/high; шығыс жаңа tuple[Reading, ...]. Негізгі
    жұмыс in_range замыканиесіне беріледі.
    """

    return select(readings, in_range(low, high))


def sort_readings(
    readings: tuple[Reading, ...], by: str, reverse: bool = False
) -> tuple[Reading, ...]:
    """Reading tuple-ын ts, value немесе sensor бойынша сұрыптап қайтарады.

    Кіріс readings, by және reverse; шығыс жаңа tuple[Reading, ...]. sorted жаңа
    list жасайды, оны tuple-ға айналдырып immutable нәтиже береміз.
    """

    keys: dict[str, Callable[[Reading], str | float]] = {
        "ts": lambda reading: reading.ts,
        "value": lambda reading: reading.value,
        "sensor": lambda reading: reading.sensor_id,
    }
    return tuple(
        sorted(readings, key=keys[by], reverse=reverse)
    )  # Дәріс 4: sorted + key=lambda.


def top_n_readings(readings: tuple[Reading, ...], n: int) -> tuple[Reading, ...]:
    """Ең үлкен value мәндері бар алғашқы n Reading қайтарады.

    Кіріс readings tuple және n; шығыс жаңа tuple[Reading, ...]. Алдымен таза
    сұрыптау жасалып, кейін кесінді алынады.
    """

    return sort_readings(readings, "value", reverse=True)[:n]


def avg_by_sensor(readings: tuple[Reading, ...]) -> tuple[tuple[str, float], ...]:
    """Әр sensor_id бойынша орташа value есептейді.

    Кіріс readings tuple; шығыс tuple[(sensor_id, avg), ...]. reduce accumulator-ы
    әр қадамда жаңа dict жасайды, сондықтан бастапқы дерек өзгермейді.
    """

    grouped = reduce(
        lambda acc, reading: {  # Дәріс 2: accumulator sum/count жұбын жинайды.
            **acc,
            reading.sensor_id: (
                acc.get(reading.sensor_id, (0.0, 0))[0] + reading.value,
                acc.get(reading.sensor_id, (0.0, 0))[1] + 1,
            ),
        },
        readings,
        {},
    )
    return tuple(map(lambda item: (item[0], item[1][0] / item[1][1]), grouped.items()))
