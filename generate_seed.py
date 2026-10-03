"""Лаб 1-2 үшін seed.json файлын детерминді генерациялайды.

Скрипт Дәріс 1-3 тақырыптарына керек бастапқы деректі жасайды: локация
иерархиясы, құрылғылар, сенсорлар, көрсеткіштер, ережелер және alert жазбалары.
random.seed(42) нәтижені әр іске қосқанда бірдей қылады.
"""

import json
import math
import random
from datetime import datetime, timedelta
from pathlib import Path


def build_seed() -> dict:
    """Демо деректі Python dict ретінде құрады.

    Кіріс аргумент жоқ; шығыс seed.json құрылымына сәйкес dict. Дерек көлемі
    тапсырмадағы сандық талаптарды дәл орындау үшін бір жерде құрылады.
    """

    random.seed(42)
    locations, rooms = [], []
    for campus_number in range(1, 4):
        campus_id = f"c{campus_number}"
        locations.append(
            {"id": campus_id, "name": f"Кампус {campus_number}", "parent_id": None}
        )
        building_id = f"{campus_id}-b1"
        locations.append(
            {
                "id": building_id,
                "name": f"Ғимарат {campus_number}.1",
                "parent_id": campus_id,
            }
        )
        for floor_number, room_count in enumerate((3, 2), 1):
            floor_id = f"{building_id}-f{floor_number}"
            locations.append(
                {
                    "id": floor_id,
                    "name": f"Қабат {campus_number}.{floor_number}",
                    "parent_id": building_id,
                }
            )
            for room_number in range(1, room_count + 1):
                room_id = f"{floor_id}-r{room_number}"
                locations.append(
                    {
                        "id": room_id,
                        "name": f"Бөлме {campus_number}{floor_number}{room_number:02d}",
                        "parent_id": floor_id,
                    }
                )
                rooms.append(room_id)

    devices, sensors = [], []
    models = ("ESP32-Hub", "RPi-Gateway", "Zigbee-GW")
    for index, room_id in enumerate(rooms[:12], 1):
        device_id = f"d{index:02d}"
        devices.append(
            {
                "id": device_id,
                "location_id": room_id,
                "model": models[index % len(models)],
                "firmware": f"1.{index % 4}.0",
            }
        )
        sensors.append(
            {
                "id": f"{device_id}-t",
                "device_id": device_id,
                "kind": "temp",
                "unit": "°C",
                "calibration": random.choice((0.0, 0.0, 0.3, -0.2)),
            }
        )
        sensors.append(
            {
                "id": f"{device_id}-h",
                "device_id": device_id,
                "kind": "hum",
                "unit": "%",
                "calibration": 0.0,
            }
        )

    readings, reading_number = [], 0
    start = datetime(2025, 3, 1)
    for sensor in sensors:
        base = (
            random.uniform(20, 23)
            if sensor["kind"] == "temp"
            else random.uniform(40, 55)
        )
        amplitude = 1.5 if sensor["kind"] == "temp" else 5.0
        for hour in range(60):
            value = (
                base
                + amplitude * math.sin(2 * math.pi * hour / 24)
                + random.gauss(0, 0.4)
            )
            if random.random() < 0.01:
                value += random.choice((-1, 1)) * (
                    8 if sensor["kind"] == "temp" else 25
                )
            reading_number += 1
            readings.append(
                {
                    "id": f"r{reading_number:05d}",
                    "sensor_id": sensor["id"],
                    "ts": (start + timedelta(hours=hour)).isoformat(),
                    "value": round(value, 2),
                }
            )

    rules = [
        {
            "id": "rule1",
            "kind": "range",
            "payload": {"sensor": "temp", "min": 18, "max": 26},
        },
        {
            "id": "rule2",
            "kind": "range",
            "payload": {"sensor": "hum", "min": 30, "max": 60},
        },
        {
            "id": "rule3",
            "kind": "delta",
            "payload": {"sensor": "temp", "max_per_hour": 4},
        },
        {
            "id": "rule4",
            "kind": "delta",
            "payload": {"sensor": "hum", "max_per_hour": 15},
        },
        {"id": "rule5", "kind": "stale", "payload": {"minutes": 90}},
    ]
    alerts = [
        {
            "id": "a1",
            "ts": "2025-03-01T10:00:00",
            "sensor_id": "d01-t",
            "location_id": None,
            "code": "RANGE_HIGH",
            "message": "Температура 26 °C мәнінен жоғары",
            "severity": "warning",
        },
        {
            "id": "a2",
            "ts": "2025-03-02T04:00:00",
            "sensor_id": "d03-h",
            "location_id": None,
            "code": "RANGE_LOW",
            "message": "Ылғалдылық 30 % мәнінен төмен",
            "severity": "info",
        },
    ]
    return {
        "locations": locations,
        "devices": devices,
        "sensors": sensors,
        "readings": readings,
        "rules": rules,
        "alerts": alerts,
    }


def main() -> None:
    """seed.json файлын data папкасына жазады.

    Кіріс аргумент жоқ; шығыс файлдық жүйедегі data/seed.json. JSON адам оқуға
    ыңғайлы болуы үшін ensure_ascii=False және indent=2 қолданылады.
    """

    output = Path(__file__).resolve().parent.parent / "data" / "seed.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(build_seed(), ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print("seed.json дайын")


if __name__ == "__main__":
    main()
