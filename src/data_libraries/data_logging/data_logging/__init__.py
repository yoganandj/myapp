from contextlib import contextmanager
from logging import DEBUG
from os import environ
from time import perf_counter
from uuid import uuid4
from warnings import warn

from .loggers import BaseLogger, ConsoleLogger
from .models import (
    SourceType,
    BaseEvent,
    BaseEventAdditionalInfos,
    LogEvent,
    ErrorEvent,
    ErrorEventAdditionalInfos,
    PerformanceEvent,
    PerformanceEventAdditionalInfos,
)
from dataclasses import asdict

CONSOLE_LOGGER = "console"


class LoggerManager:
    logger: BaseLogger
    source_type: SourceType
    source_name: str
    is_muted: bool = False

    def __init__(
        self,
        source_type=None,
        source_name=None,
        logger_level=DEBUG,
        logger_type=CONSOLE_LOGGER,
    ):
        logger_type = environ.get("LOGGER_TYPE", logger_type)
        logger_level = environ.get("LOGGER_LEVEL", logger_level)
        if logger_type == CONSOLE_LOGGER:
            self.logger = ConsoleLogger(level=logger_level)
        else:
            raise RuntimeError(f"Unknown logger type: {logger_type}")

        source_type = environ.get("SOURCE_TYPE", source_type)
        try:
            self.source_type = SourceType[source_type]
        except KeyError as e:
            raise RuntimeError(f"Unknown source type: {source_type}") from e

        try:
            self.source_name = environ.get("SOURCE_NAME", source_name)
        except KeyError as e:
            raise RuntimeError("Source name is required") from e

        self.correlation_id = None

    def log_activity(self, title: str, **additional_infos) -> None:
        if self.is_muted:
            return

        base_event = self._build_base_event(title)
        base_event.additional_info = BaseEventAdditionalInfos(**additional_infos)
        log_event = LogEvent(**asdict(base_event), **asdict(base_event.additional_info))

        self.logger.log_activity(log_event)

    def log_error(self, title: str, **additional_infos) -> None:
        if self.is_muted:
            return

        base_event = self._build_base_event(title)
        error_event_additional_info = ErrorEventAdditionalInfos(**additional_infos)
        error_event = ErrorEvent(
            **asdict(base_event), **asdict(error_event_additional_info)
        )

        self.logger.log_error(error_event)

    def log_performance(self, title: str, **additional_infos) -> None:
        if self.is_muted:
            return

        base_event = self._build_base_event(title)
        performance_event_additional_info = PerformanceEventAdditionalInfos(
            **additional_infos
        )
        performance_event = PerformanceEvent(
            **asdict(base_event), **asdict(performance_event_additional_info)
        )

        self.logger.log_performance(performance_event)

    def mute(self, mute: bool = True) -> None:
        self.is_muted = mute

    def unmute(self) -> None:
        self.is_muted = False

    @contextmanager
    def time(self, title: str) -> None:
        start_time = perf_counter()
        yield
        duration = perf_counter() - start_time
        duration *= 1000.0  # Convert to milliseconds
        self.log_performance(title, duration=duration)

    @property
    def correlation_id(self) -> str:
        if not self._correlation_id:
            warn(
                "No correlation_id was set on the LoggerManager",
                RuntimeWarning,
                stacklevel=2,
            )
        return self._correlation_id

    @correlation_id.setter
    def correlation_id(self, value: str):
        self._correlation_id = value

    def _build_base_event(self, title: str) -> BaseEvent:
        correlation_id = self.correlation_id or str(uuid4())
        return BaseEvent(
            source_type=self.source_type,
            source_name=self.source_name,
            correlation_id=correlation_id,
            title=title,
        )
