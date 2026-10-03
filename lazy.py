"""Лаб 5 каркасы: көрсеткіштер ағынына арналған жалқау (lazy) генераторлар.

Әзірге бос орын. Лаб 5-те yield қолданатын iter_readings және
lazy_rolling_avg жазылады: бүкіл ағынды жадқа жүктемей өңдеу.
"""

from __future__ import annotations

from collections.abc import Callable, Iterable, Iterator

from app.core.domain import Reading


def iter_readings(
    readings: tuple[Reading, ...], pred: Callable[[Reading], bool]
) -> Iterable[Reading]:
    """Предикатқа сай Reading-терді біртіндеп береді (Лаб 5-те іске асады)."""

    raise NotImplementedError("Лаб 5: yield-генератор")


def lazy_rolling_avg(
    stream: Iterable[Reading], window: int
) -> Iterator[tuple[str, float]]:
    """(ts, орташа) жұптарын ағын келген сайын береді (Лаб 5-те іске асады)."""

    raise NotImplementedError("Лаб 5: жылжымалы орташа")
