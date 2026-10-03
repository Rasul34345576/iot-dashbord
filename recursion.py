"""Лаб 2 және Дәріс 2 үшін рекурсия мысалдары.

Модуль локациялар иерархиясын және күн бойынша Reading топтауын рекурсивті
тәсілмен орындайды. Әр функция бастапқы tuple-ды өзгертпей, жаңа tuple қайтарады.
"""

from functools import reduce

from app.core.domain import Device, Location, Reading, Sensor


def collect_descendant_locations(
    locations: tuple[Location, ...],
    root_id: str,
    seen: frozenset[str] = frozenset(),
) -> tuple[str, ...]:
    """root_id және оның барлық төменгі локация id мәндерін қайтарады.

    Кіріс locations tuple, root_id және seen (қонған түйіндер жиыны, әдепкіде бос);
    шығыс tuple[str, ...]. Екі базалық жағдай бар: балалары жоқ түйін және
    бұрын қонған түйін (цикл) — екіншісі бұзылған деректе шексіз рекурсиядан сақтайды.
    """

    if root_id in seen:
        return ()  # Базалық жағдай 2: цикл табылды, қайта кірмейміз.
    visited = seen | {root_id}  # Жаңа frozenset — бастапқы seen өзгермейді.
    children = tuple(filter(lambda loc: loc.parent_id == root_id, locations))
    # Дәріс 2: filter арқылы ағымдағы түйіннің тікелей балаларын аламыз.
    child_ids = reduce(
        lambda acc, child: acc
        + collect_descendant_locations(locations, child.id, visited),
        children,
        (),
    )  # Рекурсия: әр баланың ішіне түсіп, нәтижелерді tuple-ға жинаймыз.
    return (root_id,) + child_ids  # Базалық жағдай 1: children бос болса child_ids=().


def find_sensors_in_location(
    locations: tuple[Location, ...],
    devices: tuple[Device, ...],
    sensors: tuple[Sensor, ...],
    root_id: str,
) -> tuple[Sensor, ...]:
    """Локация иерархиясындағы барлық сенсорды табады.

    Кіріс locations/devices/sensors tuple және root_id; шығыс tuple[Sensor, ...].
    Ұрпақ локациялар рекурсиямен алынып, кейін құрылғы мен сенсор байланысы сүзеді.
    """

    location_ids = frozenset(collect_descendant_locations(locations, root_id))
    device_ids = frozenset(
        map(
            lambda device: device.id,
            filter(lambda device: device.location_id in location_ids, devices),
        )
    )
    return tuple(
        filter(lambda sensor: sensor.device_id in device_ids, sensors)
    )  # Дәріс 2: filter байланысқан сенсорларды ғана қалдырады.


def nest_readings_by_day(
    readings: tuple[Reading, ...],
) -> tuple[tuple[str, tuple[Reading, ...]], ...]:
    """Reading tuple-ын күн бойынша рекурсивті түрде топтайды.

    Кіріс readings tuple; шығыс tuple[(day, tuple[Reading, ...]), ...]. Бос
    кіріс базалық жағдай ретінде бос tuple қайтарады.
    """

    if len(readings) == 0:
        return ()  # Базалық жағдай: өңдейтін Reading қалмаса, рекурсия тоқтайды.
    day = readings[0].ts[:10]
    same_day = tuple(filter(lambda reading: reading.ts[:10] == day, readings))
    rest = tuple(filter(lambda reading: reading.ts[:10] != day, readings))
    return ((day, same_day),) + nest_readings_by_day(
        rest
    )  # Рекурсия: қалған күндерді дәл солай топтаймыз.
