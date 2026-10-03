"""Лаб 3 каркасы: қымбат есептеулерді (аномалиялар, агрегаттар) кэштеу.

Әзірге бос орын (заглушка). Лаб 3-те мұнда lru_cache және иммутабельді кэш
кілті (sensor_id, start, end, window) бар detect_anomalies жазылады.
"""

from __future__ import annotations

from app.core.domain import Reading


def detect_anomalies(
    key: str, readings_index: tuple[Reading, ...], window: int = 30
) -> tuple[Reading, ...]:
    """Аномалды Reading-терді табады (Лаб 3-те іске асады).

    Кіріс иммутабельді key, readings tuple және терезе өлшемі; шығыс tuple.
    """

    raise NotImplementedError("Лаб 3: z-score / жылжымалы терезе + lru_cache")
