import json
import logging
import sys
from typing import Any, Callable, List, Union

import structlog
from structlog.processors import _json_fallback_handler
from structlog.types import EventDict

_NOISY_LOG_SOURCES = (
    "boto",
    "boto3",
    "botocore",
    "urllib3",
    "s3transfer",
)


class AWSCloudWatchLogs:
    """
    Render a log line compatible with AWS CloudWatch Logs.  This is a copy
    and modification of `structlog.processors.JSONRenderer`

    Render the ``event_dict`` using ``serializer(event_dict, **json_kw)``.
    :param callouts: Are printed in clear-text on the front of the log line.
        Only the first two items of this list are called out.
    :param json_kw: Are passed unmodified to *serializer*.  If *default*
        is passed, it will disable support for ``__structlog__``-based
        serialization.
    :param serializer: A :func:`json.dumps`-compatible callable that
        will be used to format the string.  This can be used to use alternative
        JSON encoders like `simplejson
        <https://pypi.org/project/simplejson/>`_ or `RapidJSON
        <https://pypi.org/project/python-rapidjson/>`_ (faster but Python
        3-only) (default: :func:`json.dumps`).
    """

    def __init__(
        self,
        callouts: List | None = None,
        serializer: Callable[..., Union[str, bytes]] = json.dumps,
        **dumps_kw: Any,
    ) -> None:
        try:
            self._callout_one_key = callouts[0]
        except IndexError:
            self._callout_one_key = None
        try:
            self._callout_two_key = callouts[1]
        except IndexError:
            self._callout_two_key = None
        dumps_kw.setdefault("default", _json_fallback_handler)
        self._dumps_kw = dumps_kw
        self._dumps = serializer

    def __call__(self, _, name: str, event_dict: EventDict) -> Union[str, bytes]:
        """
        The return type of this depends on the return type of self._dumps.
        """
        if self._callout_one_key:
            callout_one = event_dict.get(self._callout_one_key, "")
        else:
            callout_one = "none"
        if self._callout_two_key:
            callout_two = event_dict.get(self._callout_two_key, "")
        else:
            callout_two = "none"
        return f'[{name.upper()}] "{callout_one}" "{callout_two}" ' + self._dumps(event_dict, **self._dumps_kw)


structlog.configure(
    processors=[
        # If log level is too low, abort pipeline and throw away log entry.
        structlog.stdlib.filter_by_level,
        # Add the name of the logger to event dict.
        structlog.stdlib.add_logger_name,
        # Add log level to event dict.
        structlog.stdlib.add_log_level,
        # Perform %-style formatting.
        structlog.stdlib.PositionalArgumentsFormatter(),
        # Add a timestamp in ISO 8601 format.
        structlog.processors.TimeStamper(fmt="iso"),
        # If the "stack_info" key in the event dict is true, remove it and
        # render the current stack trace in the "stack" key.
        structlog.processors.StackInfoRenderer(),
        # If the "exc_info" key in the event dict is either true or a
        # sys.exc_info() tuple, remove "exc_info" and render the exception
        # with traceback into the "exception" key.
        structlog.processors.format_exc_info,
        # If some value is in bytes, decode it to a Unicode str.
        structlog.processors.UnicodeDecoder(),
        # Add callsite parameters.
        structlog.processors.CallsiteParameterAdder(
            {
                structlog.processors.CallsiteParameter.FILENAME,
                structlog.processors.CallsiteParameter.FUNC_NAME,
                structlog.processors.CallsiteParameter.LINENO,
            }
        ),
        # Render the final event dict as JSON.
        structlog.processors.JSONRenderer(),
    ],
    # `wrapper_class` is the bound logger that you get back from
    # get_logger(). This one imitates the API of `logging.Logger`.
    wrapper_class=structlog.stdlib.BoundLogger,
    # `logger_factory` is used to create wrapped loggers that are used for
    # OUTPUT. This one returns a `logging.Logger`. The final value (a JSON
    # string) from the final processor (`JSONRenderer`) will be passed to
    # the method of the same name as that you've called on the bound logger.
    logger_factory=structlog.stdlib.LoggerFactory(),
    # Effectively freeze configuration after creating the first bound
    # logger.
    cache_logger_on_first_use=True,
)
logging.basicConfig(
    format="%(message)s",
    stream=sys.stdout,
    level=logging.DEBUG,
    force=True,
)
for source in _NOISY_LOG_SOURCES:
    logging.getLogger(source).setLevel(logging.WARNING)


def get_logger(name: str) -> structlog.stdlib.BoundLogger:
    return structlog.get_logger(name)


def full_stack():
    import sys
    import traceback

    exc = sys.exc_info()[0]
    stack = traceback.extract_stack()[:-1]  # last one would be full_stack()
    if exc is not None:  # i.e. an exception is present
        del stack[-1]  # remove call of full_stack, the printed exception
        # will contain the caught exception caller instead
    trc = "Traceback (most recent call last):\n"
    stackstr = trc + "".join(traceback.format_list(stack))
    if exc is not None:
        stackstr += "  " + traceback.format_exc().lstrip(trc)
    return stackstr
