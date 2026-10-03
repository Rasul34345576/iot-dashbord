"""Лаб 1-2 және 1-4 дәрістерін көрсететін Streamlit интерфейсі.

Бұл модуль климат/IoT seed дерегін session_state ішінде сақтап, таза функциялар,
өзгермейтіндік, рекурсия, замыкание, partial, pipe және decorator нәтижелерін UI
арқылы көрсетуге арналған.
"""

import sys
from collections.abc import Mapping
from dataclasses import asdict
from functools import partial
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import streamlit as st  # noqa: E402

from app.core.compose import pipe, timed  # noqa: E402
from app.core.domain import Reading  # noqa: E402
from app.core.recursion import (  # noqa: E402
    collect_descendant_locations,
    nest_readings_by_day,
)
from app.core.transforms import (  # noqa: E402
    add_reading,
    all_of,
    apply_calibration,
    avg_by_sensor,
    by_location,
    by_sensor_kind,
    by_time_range,
    calibrated_readings,
    load_seed,
    readings_stats,
    select,
    sort_readings,
    top_n_readings,
)

SEED_PATH = ROOT / "data" / "seed.json"
MENU = (
    "Overview",
    "Data",
    "Functional Core",
    "Pipelines",
    "Async/FRP",
    "Reports",
    "Tests",
    "About",
)


def get_seed():
    """session_state ішінен seed tuple-ын оқиды.

    Кіріс аргумент жоқ; шығыс seed tuple немесе None. Session_state қолданылса да,
    ядро функциялары бастапқы tuple-ды өзгертпейді.
    """

    return st.session_state.get("seed")


def _plain(item):
    """Dataclass-ты Streamlit түсінетін қарапайым dict-ке айналдырады.

    Кіріс dataclass объектісі; шығыс dict. FrozenDict (Rule.payload, Event.payload)
    кестеде көрсету үшін кәдімгі dict-ке ауыстырылады.
    """

    return {
        key: dict(value) if isinstance(value, Mapping) else value
        for key, value in asdict(item).items()
    }


def rows(items):
    """Dataclass объектілерін Streamlit кестесіне ыңғайлы dict тізіміне айналдырады.

    Кіріс dataclass iterable; шығыс list[dict]. UI-де көрсету үшін ғана list керек,
    ал функционалды ядро tuple-мен қалады.
    """

    return list(map(_plain, items))  # Дәріс 2: map UI проекциясына жеткілікті.


def ensure_seed():
    """Seed жүктелмесе, пайдаланушыға қысқа хабарлама көрсетеді.

    Кіріс жоқ; шығыс seed tuple немесе None. Бұл UI guard қайталанатын тексерісті
    бір жерде ұстайды.
    """

    seed = get_seed()
    if seed is None:
        st.info("Алдымен Data бөліміндегі «Load seed» батырмасын басыңыз.")
    return seed


def page_overview():
    """Жалпы метрикалар мен температура/ылғал статистикасын көрсетеді.

    Кіріс Streamlit күйінен алынады; шығыс UI элементтері. Есептеу үшін таза
    readings_stats функциясы қолданылады.
    """

    st.header("Жалпы шолу")
    seed = ensure_seed()
    if seed is None:
        return
    locations, devices, sensors, readings, _, _ = seed
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Локациялар", len(locations))
    c2.metric("Құрылғылар", len(devices))
    c3.metric("Сенсорлар", len(sensors))
    c4.metric("Көрсеткіштер", len(readings))

    for kind, label in (("temp", "Температура, °C"), ("hum", "Ылғалдылық, %")):
        st.subheader(label)
        stats = readings_stats(readings, sensors, kind)
        s1, s2, s3, s4 = st.columns(4)
        s1.metric("Ең аз", stats["min"])
        s2.metric("Ең көп", stats["max"])
        s3.metric("Орташа", None if stats["avg"] is None else round(stats["avg"], 2))
        s4.metric("Саны", stats["count"])


def page_data():
    """Seed дерегін жүктеп, бөлімдерді expander ішінде көрсетеді.

    Кіріс батырма әрекеті мен файл жолы; шығыс session_state ішіндегі seed және UI
    кестелері. Дерек tuple ретінде сақталады.
    """

    st.header("Деректер")
    if st.button("Load seed"):
        st.session_state["seed"] = load_seed(SEED_PATH)
        st.success("seed.json жүктелді.")
    seed = get_seed()
    if seed is None:
        return
    names = ("locations", "devices", "sensors", "readings", "rules", "alerts")
    for name, items in zip(names, seed, strict=True):
        with st.expander(f"{name}: {len(items)} жазба"):
            st.dataframe(rows(items[:200]), use_container_width=True)


def page_functional_core():
    """Таза функция, өзгермейтіндік, сұрыптау және timed decorator мысалдарын көрсетеді.

    Кіріс UI таңдаулары; шығыс жаңа tuple нәтижелері мен өлшеу уақыты. Бастапқы
    session_state seed тек жаңа tuple-мен ауыстырылады.
    """

    st.header("Функционалды ядро")
    seed = ensure_seed()
    if seed is None:
        return
    locations, devices, sensors, readings, rules, alerts = seed

    st.subheader("Жаңа көрсеткіш қосу")
    sensor_id = st.selectbox("Сенсор", tuple(map(lambda sensor: sensor.id, sensors)))
    value = st.number_input("Мән", value=22.0)
    if st.button("Көрсеткіш қосу"):
        reading = Reading(
            f"r-ui-{len(readings) + 1}", sensor_id, "2025-03-05T00:00:00", value
        )
        new_readings = add_reading(readings, reading)
        st.session_state["seed"] = (
            locations,
            devices,
            sensors,
            new_readings,
            rules,
            alerts,
        )
        st.write(f"Алдыңғы ұзындық: {len(readings)}")
        st.write(f"Жаңа ұзындық: {len(new_readings)}")

    st.subheader("Калибрлеу қолдану")
    calibration_sensor_id = st.selectbox(
        "Калибрленетін сенсор", tuple(map(lambda sensor: sensor.id, sensors))
    )
    delta = st.number_input("Қосу мәні", value=0.5)
    if st.button("Калибрлеуді қолдану"):
        new_sensors = apply_calibration(sensors, calibration_sensor_id, delta)
        before = tuple(filter(lambda item: item.id == calibration_sensor_id, sensors))[
            0
        ]
        after = tuple(
            filter(lambda item: item.id == calibration_sensor_id, new_sensors)
        )[0]
        st.session_state["seed"] = (
            locations,
            devices,
            new_sensors,
            readings,
            rules,
            alerts,
        )
        st.write(f"Дейін: {before.calibration}")
        st.write(f"Кейін: {after.calibration}")

    st.subheader("Калибрленген проекция")
    measured = timed(calibrated_readings)(readings[:50], sensors)
    calibrated, elapsed_ms = measured
    st.caption(f"timed decorator өлшеген уақыт: {elapsed_ms:.3f} мс")
    st.dataframe(rows(calibrated[:10]), use_container_width=True)

    st.subheader("Сұрыптау және top-5")
    sort_by = st.selectbox("Сұрыптау өрісі", ("ts", "value", "sensor"))
    st.dataframe(rows(top_n_readings(sort_readings(readings, sort_by), 5)))


def page_pipelines():
    """Сүзу, all_of, pipe+partial және рекурсия нәтижелерін көрсетеді.

    Кіріс UI фильтрлері; шығыс сүзілген tuple, статистика және кестелер. Pipeline
    бастапқы readings tuple-ын өзгертпейді.
    """

    st.header("Pipeline")
    seed = ensure_seed()
    if seed is None:
        return
    locations, devices, sensors, readings, _, _ = seed

    kind = st.selectbox("Сенсор түрі", ("all", "temp", "hum"))
    names = dict(map(lambda location: (location.id, location.name), locations))
    location_id = st.selectbox(
        "Локация", tuple(names), format_func=lambda item: names[item]
    )
    include_children = st.checkbox(
        "Иерархиядағы ішкі локацияларды қоса алу", value=True
    )
    days = sorted(frozenset(map(lambda reading: reading.ts[:10], readings)))
    if not days:
        st.info("Көрсеткіштер жоқ: алдымен деректі жүктеңіз.")
        return  # Guard: бос readings кезінде days[0] IndexError бермеу үшін.
    start_day, end_day = st.select_slider(
        "Кезең", options=days, value=(days[0], days[-1])
    )

    predicates = (by_time_range(f"{start_day}T00:00:00", f"{end_day}T23:59:59"),)
    if kind != "all":
        predicates = predicates + (by_sensor_kind(kind, sensors),)
    if include_children:
        predicates = predicates + (
            by_location(location_id, locations, devices, sensors),
        )
        st.caption(
            "Қамтылған локациялар: "
            + ", ".join(collect_descendant_locations(locations, location_id))
        )
    filtered = select(readings, all_of(*predicates))
    st.write(f"Табылған көрсеткіш саны: {len(filtered)}")

    for stat_kind in ("temp", "hum"):
        stats = readings_stats(filtered, sensors, stat_kind)
        st.write(f"{stat_kind}: {stats}")

    pipeline_result = pipe(
        filtered,
        partial(
            sort_readings, by="value", reverse=True
        ),  # Дәріс 4: partial аргумент бекітеді.
        partial(top_n_readings, n=5),
    )
    st.subheader("pipe + partial нәтижесі")
    st.dataframe(rows(pipeline_result), use_container_width=True)

    st.subheader("Сенсор бойынша орташа мән")
    st.dataframe(
        list(
            map(
                lambda item: {"sensor_id": item[0], "avg": item[1]},
                avg_by_sensor(filtered),
            )
        )
    )

    st.subheader("Күн бойынша рекурсивті топтау")
    st.dataframe(
        list(
            map(
                lambda item: {"күн": item[0], "саны": len(item[1])},
                nest_readings_by_day(filtered),
            )
        )
    )


def page_later(title: str):
    """Кейінгі лабораторияларға арналған заглушка көрсетеді.

    Кіріс title жолы; шығыс Streamlit info блогы. Бұл жоба тек Лаб 1-2 және
    1-4 дәрістер көлемінде қалуы үшін толық іске асыру жасалмайды.
    """

    st.header(title)
    st.info("Бұл бөлім кейін жасалады.")


def page_tests():
    """PowerShell үшін тексеру командаларын көрсетеді.

    Кіріс жоқ; шығыс UI code блогы. Командалар python -m үлгісінде берілген,
    сондықтан жалаң pytest/streamlit/pip қолданылмайды.
    """

    st.header("Тексеру командалары")
    st.code(
        "\n".join(
            (
                r".\.venv\Scripts\python.exe -m pytest -q",
                r".\.venv\Scripts\python.exe -m black --check .",
                r".\.venv\Scripts\python.exe -m ruff check .",
            )
        ),
        language="powershell",
    )


def page_about():
    """Дәрістер мен кодтағы орындарын кестемен көрсетеді.

    Кіріс жоқ; шығыс Streamlit кестесі. Бұл бөлім студентке қорғау кезінде
    тақырып пен файл байланысын жылдам көрсетуге көмектеседі.
    """

    st.header("Жоба туралы")
    st.table(
        (
            {"Дәріс": "1", "Кодтағы орны": "domain.py, transforms.py"},
            {"Дәріс": "2", "Кодтағы орны": "transforms.py, recursion.py"},
            {"Дәріс": "3", "Кодтағы орны": "domain.py, transforms.py"},
            {"Дәріс": "4", "Кодтағы орны": "compose.py, transforms.py, main.py"},
        )
    )


def main():
    """Streamlit бет параметрін орнатып, бүйір мәзір арқылы бет таңдайды.

    Кіріс жоқ; шығыс Streamlit UI. Мәзір атаулары тапсырмадағы нақты тізіммен
    сәйкес қалдырылады.
    """

    st.set_page_config(page_title="Климат IoT дашборды", layout="wide")
    st.sidebar.title("Мәзір")
    page = st.sidebar.radio("Бөлім", MENU)
    pages = {
        "Overview": page_overview,
        "Data": page_data,
        "Functional Core": page_functional_core,
        "Pipelines": page_pipelines,
        "Async/FRP": partial(page_later, "Async/FRP"),
        "Reports": partial(page_later, "Reports"),
        "Tests": page_tests,
        "About": page_about,
    }
    pages[page]()


main()
