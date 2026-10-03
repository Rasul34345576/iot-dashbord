"""Дәріс 4 үшін compose, pipe, curry және декораторлар.

Модуль жоғары ретті функцияларды Callable арқылы көрсетеді. Функциялар мен
декораторлар таза қолдануға ыңғайлы: timed print жасамайды, logged sink-ті сырттан
алады, type_checked қате типті TypeError арқылы тоқтатады.
"""

from __future__ import annotations

from functools import reduce, wraps
from time import perf_counter
from typing import Any, Callable, TypeVar

T = TypeVar("T")
U = TypeVar("U")
V = TypeVar("V")


def compose(*functions: Callable[[Any], Any]) -> Callable[[Any], Any]:
    """Функцияларды оңнан солға біріктіретін жаңа функция қайтарады.

    Кіріс бірнеше Callable; шығыс бір Callable. Оңнан солға орындау математикадағы
    f(g(x)) жазылуына сәйкес келеді.
    """

    return lambda value: reduce(
        lambda acc, function: function(acc), reversed(functions), value
    )  # Дәріс 4: accumulator аралық нәтижені ұстайды.


def pipe(value: T, *functions: Callable[[Any], Any]) -> Any:
    """Мәнді функциялар тізбегінен солдан оңға өткізеді.

    Кіріс бастапқы value және Callable тізімі; шығыс соңғы функция нәтижесі.
    Pipeline UI-де сүзу -> сұрыптау -> top-n қадамын оқуға жеңіл етеді.
    """

    return reduce(
        lambda acc, function: function(acc), functions, value
    )  # Дәріс 4: солдан оңға оқу үшін pipe таңдалды.


def curry2(function: Callable[[T, U], V]) -> Callable[[T], Callable[[U], V]]:
    """Екі аргументті функцияны бір-бір аргумент қабылдайтын функцияларға бөледі.

    Кіріс Callable[[T, U], V]; шығыс Callable[[T], Callable[[U], V]]. Бірінші
    аргумент ішкі замыкание ішінде есте сақталады.
    """

    return lambda first: lambda second: function(
        first, second
    )  # Дәріс 4: first мәні каррирленген замыканиеде сақталады.


def timed(function: Callable[..., T]) -> Callable[..., tuple[T, float]]:
    """Функция нәтижесін және орындалу уақытын миллисекундпен қайтаратын decorator.

    Кіріс кез келген Callable; шығыс wrapper, ол (нәтиже, ms) tuple қайтарады.
    print қолданылмайды, себебі өлшеу нәтижесі тест пен UI-ге таза беріледі.
    """

    @wraps(function)
    def wrapper(*args: Any, **kwargs: Any) -> tuple[T, float]:
        """Ішкі wrapper бастапқы функцияны өлшеп, нәтижені уақытпен бірге қайтарады."""

        start = perf_counter()
        result = function(*args, **kwargs)
        elapsed_ms = (perf_counter() - start) * 1000
        return result, elapsed_ms  # Дәріс 4: wrapper жанама print жасамайды.

    return wrapper


def logged(
    sink: Callable[[str], None],
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """Лог жазатын sink сырттан берілетін decorator фабрикасын қайтарады.

    Кіріс sink Callable; шығыс decorator. Dependency Injection тестте sink-ті
    list.append сияқты қарапайым функциямен ауыстыруға мүмкіндік береді.
    """

    def decorator(function: Callable[..., T]) -> Callable[..., T]:
        """Decorator бастапқы функция атауын wrapper ішінде sink-ке жазады."""

        @wraps(function)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            """Ішкі wrapper логты жанама сақтау орнына емес, берілген sink-ке жазады."""

            sink(
                function.__name__
            )  # Дәріс 4: wrapper шақыру фактісін DI арқылы береді.
            return function(*args, **kwargs)

        return wrapper

    return decorator


def type_checked(
    correct_type: type,
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """Нәтиже типін тексеретін decorator фабрикасын қайтарады.

    Кіріс күтілетін type; шығыс decorator. Нәтиже дұрыс тип болмаса TypeError
    көтереді, сондықтан қате келісімшарт ерте байқалады.
    """

    def decorator(function: Callable[..., T]) -> Callable[..., T]:
        """Decorator бастапқы функцияның нәтижесін wrapper ішінде тексереді."""

        @wraps(function)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            """Ішкі wrapper нәтиже типін тексеріп, дұрыс болса сол мәнді қайтарады."""

            result = function(*args, **kwargs)
            if not isinstance(result, correct_type):
                raise TypeError(f"Күтілетін тип: {correct_type.__name__}")
            return result

        return wrapper

    return decorator
