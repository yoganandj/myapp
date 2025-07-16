from .models import LogEvent, ErrorEvent, PerformanceEvent
from logging import Logger, DEBUG, Formatter, StreamHandler, getLogger
from sys import stdout

LOGGING_FORMAT = "%(message)s"


class BaseLogger:
    def log_activity(self, event: LogEvent):
        raise NotImplementedError("Subclasses should implement this method.")

    def log_error(self, event: ErrorEvent):
        raise NotImplementedError("Subclasses should implement this method.")

    def log_performance(self, event: PerformanceEvent):
        raise NotImplementedError("Subclasses should implement this method.")


class ConsoleLogger(BaseLogger):
    logger: Logger

    def __init__(self, level=DEBUG):
        sh = StreamHandler(stdout)
        sh.setFormatter(Formatter(LOGGING_FORMAT))
        self.logger = getLogger(__name__)
        self.logger.setLevel(level)
        self.logger.addHandler(sh)

    def log_activity(self, event: LogEvent):
        self.logger.info(event)

    def log_error(self, event: ErrorEvent):
        self.logger.error(event)

    def log_performance(self, event: PerformanceEvent):
        self.logger.debug(event)
