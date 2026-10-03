"""Лаб 1-2 тесттеріне ортақ immutable fixture деректерін береді."""

import pytest

from app.core.domain import Device, Location, Reading, Sensor


@pytest.fixture
def locations():
    """Локация иерархиясын tuple ретінде қайтарады.

    Кіріс жоқ; шығыс tuple[Location, ...]. c1 тармағы терең, c2 тармағы бөлек
    болуы иерархиялық сүзуді нақты тексеруге көмектеседі.
    """

    return (
        Location("c1", "Кампус 1"),
        Location("b1", "Ғимарат 1", "c1"),
        Location("f1", "Қабат 1", "b1"),
        Location("r1", "Бөлме 1", "f1"),
        Location("r2", "Бөлме 2", "f1"),
        Location("c2", "Кампус 2"),
        Location("r3", "Бөлме 3", "c2"),
    )


@pytest.fixture
def devices():
    """Құрылғыларды tuple ретінде қайтарады.

    Кіріс жоқ; шығыс tuple[Device, ...]. Әр құрылғы бөлек бөлмеге байланған,
    сондықтан by_location және find_sensors_in_location нақты тексеріледі.
    """

    return (
        Device("d1", "r1", "ESP32", "1.0.0"),
        Device("d2", "r2", "ESP32", "1.0.0"),
        Device("d3", "r3", "Zigbee", "1.0.0"),
    )


@pytest.fixture
def sensors():
    """Сенсорларды tuple ретінде қайтарады.

    Кіріс жоқ; шығыс tuple[Sensor, ...]. Температура мен ылғалдылық бірге
    беріліп, kind бойынша сүзу тексеріледі.
    """

    return (
        Sensor("s1", "d1", "temp", "°C", 0.5),
        Sensor("s2", "d1", "hum", "%", 0.0),
        Sensor("s3", "d2", "temp", "°C", -0.2),
        Sensor("s4", "d3", "hum", "%", 0.0),
    )


@pytest.fixture
def readings():
    """Көрсеткіштерді tuple ретінде қайтарады.

    Кіріс жоқ; шығыс tuple[Reading, ...]. Уақыт шекаралары мен value сұрыптауын
    тексеру үшін мәндер әдейі әртүрлі қойылған.
    """

    return (
        Reading("r1", "s1", "2025-03-01T00:00:00", 20.0),
        Reading("r2", "s2", "2025-03-01T01:00:00", 45.0),
        Reading("r3", "s3", "2025-03-02T00:00:00", 22.0),
        Reading("r4", "s4", "2025-03-03T00:00:00", 55.0),
    )
