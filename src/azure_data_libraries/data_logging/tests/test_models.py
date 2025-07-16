import unittest
from datetime import datetime
from data_logging.models import LogEvent, ErrorEvent, PerformanceEvent, SourceType


class TestModels(unittest.TestCase):
    def test_log_event_creation(self):
        event = LogEvent(
            source_type=SourceType.GlueJob,
            timestamp=datetime.now(),
            source_name="test_glue_job",
            correlation_id="test_correlation_id",
            title="Test Log Event",
            message="This is a test log event.",
        )
        self.assertIsInstance(event, LogEvent)
        self.assertEqual(event.event_type, "InformationEvent")

    def test_error_event_creation(self):
        event = ErrorEvent(
            source_type=SourceType.Lambda,
            timestamp=datetime.now(),
            source_name="test_lambda",
            correlation_id="test_correlation_id",
            title="Test Error Event",
            error_code=500,
            error_type="TestError",
        )
        self.assertIsInstance(event, ErrorEvent)
        self.assertEqual(event.event_type, "ErrorEvent")

    def test_performance_event_creation(self):
        event = PerformanceEvent(
            source_type=SourceType.GlueJob,
            timestamp=datetime.now(),
            source_name="test_glue_job",
            correlation_id="test_correlation_id",
            title="Test Performance Event",
            duration=1000,
        )
        self.assertIsInstance(event, PerformanceEvent)
        self.assertEqual(event.event_type, "PerformanceEvent")


if __name__ == "__main__":
    unittest.main()
