from enum import Enum, auto
from dataclasses import dataclass
from datetime import datetime
from json import JSONEncoder, dumps

# Categorizes the origin of log events
# Enables filtering and routing in log aggregation systems
# Provides type safety for source identification
# Extensible design for future source types


class SourceType(Enum):
    GlueJob = auto()
    Lambda = auto()


# Custom Json Enoder
class EventEncoder(JSONEncoder):
    def default(self, o):
        if isinstance(o, datetime):
            return o.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        if isinstance(o, SourceType):
            return o.name
        if isinstance(o, (LogEvent, ErrorEvent, PerformanceEvent)):
            return {self._camel_case(k): v for k, v in o.__dict__.items() if v}
        return JSONEncoder.default(self, o)

    def _camel_case(self, key: str):
        chunks = key.split("_")
        return chunks[0] + "".join(word.title() for word in chunks[1:])


@dataclass
class BaseEvent:
    source_type: SourceType
    timestamp: datetime
    source_name: str
    correlation_id: str
    title: str


@dataclass
class BaseEventAdditionalInfos:
    message: str = None

    context: str = None

    user_id: str = None

    session_id: str = None


@dataclass
class LogEvent(BaseEventAdditionalInfos, BaseEvent):
    event_type: str = "InformationEvent"

    def __repr__(self):
        return dumps(self, cls=EventEncoder)


@dataclass
class ErrorEventAdditionalInfos:
    error_code: int

    error_type: str

    message: str = None

    context: str = None

    user_id: str = None

    session_id: str = None

    stack_trace: str = None

    process_id: str = None

    thread_id: str = None


@dataclass
class ErrorEvent(ErrorEventAdditionalInfos, BaseEvent):
    event_type: str = "ErrorEvent"

    def __repr__(self):
        return dumps(self, cls=EventEncoder)


@dataclass
class PerformanceEventAdditionalInfos:
    duration: int = None

    message: str = None

    context: str = None
    user_id: str = None

    session_id: str = None


@dataclass
class PerformanceEvent(PerformanceEventAdditionalInfos, BaseEvent):
    event_type: str = "PerformanceEvent"

    def __repr__(self):
        return dumps(self, cls=EventEncoder)
