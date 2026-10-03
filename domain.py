"""Лаб 1 және Дәріс 3 үшін өзгермейтін домен модельдері.

Бұл файл климат/IoT жүйесіндегі негізгі сущностьтерді frozen dataclass арқылы
сипаттайды. Модельдер tuple-пен бірге қолданылып, бастапқы деректі өзгертпеу
қағидасын көрсетуге арналған.
"""

from collections.abc import Iterator, Mapping
from dataclasses import dataclass, field
from typing import Any, Literal


class FrozenDict(Mapping):
    """Өзгертуге болмайтын (immutable) сөздік — Rule.payload үшін.

    Кіріс кез келген Mapping; шығыс оқуға ғана арналған, hash-талатын объект.
    Mapping-те __setitem__ жоқ, сондықтан payload["min"] = 0 қате береді.
    """

    def __init__(self, data: Mapping | None = None) -> None:
        """Бастапқы сөздікті көшіріп алады (сыртқы dict өзгерсе, бізге әсер етпейді)."""

        self._data = dict(data or {})

    def __getitem__(self, key: Any) -> Any:
        """Кілт бойынша мәнді оқиды."""

        return self._data[key]

    def __iter__(self) -> Iterator:
        """Кілттерді айналып шығады."""

        return iter(self._data)

    def __len__(self) -> int:
        """Кілттер санын қайтарады."""

        return len(self._data)

    def __hash__(self) -> int:
        """Мазмұн бойынша hash: frozenset(items) — реттен тәуелсіз."""

        return hash(frozenset(self._data.items()))

    def __repr__(self) -> str:
        """Оқуға ыңғайлы жол: FrozenDict({...})."""

        return f"FrozenDict({self._data!r})"


# Дәріс 3: өзгермейтіндік. frozen=True объект өрістерін кейін ауыстыртпайды.
@dataclass(frozen=True)
class Location:
    """Локация кампус, ғимарат, қабат немесе бөлмені білдіреді.

    Кіріс өрістер мәтіндік id/name және parent_id болуы мүмкін; объект immutable
    күйде сақталады және иерархияда түйін ретінде қолданылады.
    """

    id: str  # Бірегей кілт: басқа кестелер осы мән арқылы байланыстырады.
    name: str  # UI-де адамға түсінікті атауды көрсету үшін керек.
    parent_id: str | None = None  # None жоғарғы деңгей екенін білдіреді.


@dataclass(frozen=True)
class Device:
    """Құрылғы белгілі бір бөлмеде тұрған IoT жабдығын білдіреді.

    Кіріс өрістер құрылғыны локациямен байланыстырады; шығыс ретінде immutable
    Device объектісі тесттер мен UI-де өзгеріссіз қайта пайдаланылады.
    """

    id: str  # Құрылғының тұрақты идентификаторы.
    location_id: str  # Құрылғы тұрған Location.id мәні.
    model: str  # Аппарат моделін бөлек сақтау талдауды жеңілдетеді.
    firmware: str  # Нұсқа жолы құрылғы күйін сипаттайды.


@dataclass(frozen=True)
class Sensor:
    """Сенсор температура немесе ылғалдылық өлшейтін құрылғы арнасын білдіреді.

    Кіріс kind/unit шектеулі мәндерден тұрады; calibration өзгерісі жаңа Sensor
    tuple арқылы қайтарылады, бастапқы объект өзгермейді.
    """

    id: str  # Reading.sensor_id осы өріске сілтейді.
    device_id: str  # Сенсор қай Device ішінде екенін көрсетеді.
    kind: Literal["temp", "hum"]  # Дерек түрін шектеу қате мәнді ерте табады.
    unit: Literal["°C", "%"]  # Өлшем бірлігі UI және тест үшін анық беріледі.
    calibration: float = 0.0  # Түзету мәні өлшемге қосылады, модель өзгермейді.


@dataclass(frozen=True)
class Reading:
    """Reading бір уақыттағы сенсор көрсеткішін білдіреді.

    Кіріс sensor_id, ISO-8601 уақыт жолы және value санынан тұрады; функциялар
    жаңа tuple немесе жаңа Reading жасап, бастапқы көрсеткішті өзгертпейді.
    """

    id: str  # Көрсеткіштің бірегей идентификаторы.
    sensor_id: str  # Қай Sensor өлшегенін байланыстырады.
    ts: str  # ISO-8601 жолы мәтіндік салыстыруға ыңғайлы етіп таңдалды.
    value: float  # Нақты өлшенген сандық мән.


@dataclass(frozen=True)
class Rule:
    """Ереже диапазон, өзгеріс жылдамдығы немесе stale тексерісін білдіреді.

    Кіріс payload кез келген Mapping (мысалы dict) болуы мүмкін; __post_init__ оны
    FrozenDict-ке айналдырады, сондықтан Rule толық immutable және hash-талады.
    """

    id: str  # Ережені alert немесе UI ішінде тануға арналған кілт.
    kind: Literal["range", "delta", "stale"]  # Рұқсат етілген тексеріс түрлері.
    payload: Mapping = field(default_factory=FrozenDict)  # Икемді параметрлер.

    def __post_init__(self) -> None:
        """payload-ты FrozenDict-ке ауыстырады.

        frozen=True болғандықтан кәдімгі self.payload = ... жұмыс істемейді,
        сондықтан object.__setattr__ бір рет, инициализация кезінде қолданылады.
        """

        object.__setattr__(self, "payload", FrozenDict(self.payload))


@dataclass(frozen=True)
class Alert:
    """Alert жүйе тапқан ескерту немесе ақпараттық оқиғаны білдіреді.

    Кіріс кейде sensor_id немесе location_id жоқ болуы мүмкін; объект immutable
    болғандықтан журнал оқиғасы кездейсоқ өзгермейді.
    """

    id: str  # Alert жазбасын ажырататын кілт.
    ts: str  # Оқиға уақыты ISO-8601 жолымен беріледі.
    sensor_id: str | None  # Кейбір alert жалпы локацияға ғана қатысты болуы мүмкін.
    location_id: str | None  # Локация белгісіз болса None сақталады.
    code: str  # Машина оқитын қысқа код.
    message: str  # Адам оқитын қысқа хабарлама.
    severity: str  # Маңыздылық деңгейі: мысалы info немесе warning.


@dataclass(frozen=True)
class Event:
    """Event жүйедегі оқиғаны білдіреді (READING, ALERT_RAISED, ...).

    Лаб 6 (FRP шина) үшін алдын ала дайындалған модель: name — оқиға түрі,
    payload — оқиғаға тән деректер (FrozenDict түрінде өзгермейді).
    """

    id: str  # Оқиғаның бірегей идентификаторы.
    ts: str  # Оқиға уақыты, ISO-8601.
    name: str  # READING, ALERT_RAISED, ALERT_CLEARED, CALIBRATION_APPLIED ...
    payload: Mapping = field(default_factory=FrozenDict)  # Оқиға деректері.

    def __post_init__(self) -> None:
        """payload-ты Rule сияқты FrozenDict-ке айналдырады."""

        object.__setattr__(self, "payload", FrozenDict(self.payload))
