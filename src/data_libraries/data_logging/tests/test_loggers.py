import unittest
from unittest.mock import MagicMock
from data_logging.loggers import ConsoleLogger
from data_logging.models import LogEvent, ErrorEvent, PerformanceEvent, SourceType
from datetime import datetime


class TestConsoleLogger(unittest.TestCase):
    def setUp(self):
        self.logger = ConsoleLogger()
        self.logger.logger = MagicMock()

    def test_log_activity(self):
        event = LogEvent(
            source_type=SourceType.GlueJob,
            timestamp=datetime.now(),
            source_name="test_glue_job",
            correlation_id="test_correlation_id",
            title="Test Log Event",
            message="This is a test log event.",
        )
        self.logger.log_activity(event)
        self.logger.logger.info.assert_called_once_with(event)

    def test_log_error(self):
        event = ErrorEvent(
            source_type=SourceType.Lambda,
            timestamp=datetime.now(),
            source_name="test_lambda",
            correlation_id="test_correlation_id",
            title="Test Error Event",
            error_code=500,
            error_type="TestError",
        )
        self.logger.log_error(event)
        self.logger.logger.error.assert_called_once_with(event)

    def test_log_performance(self):
        event = PerformanceEvent(
            source_type=SourceType.GlueJob,
            timestamp=datetime.now(),
            source_name="test_glue_job",
            correlation_id="test_correlation_id",
            title="Test Performance Event",
            duration=1000,
        )
        self.logger.log_performance(event)
        self.logger.logger.debug.assert_called_once_with(event)


if __name__ == "__main__":
    unittest.main()
