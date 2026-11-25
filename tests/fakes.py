from anthropic import APIStatusError
from anthropic.types import ContentBlock, Message, StopReason, Usage
from httpx2 import Request, Response

FAKE_REQUEST = Request("POST", "https://api.anthropic.com/v1/messages")
"""The request SDK errors refer to; it is never sent."""


def make_message(
    content: list[ContentBlock], stop_reason: StopReason | None
) -> Message:
    """Build a response with the given blocks and stop reason."""
    return Message(
        id="msg_test",
        type="message",
        role="assistant",
        model="claude-haiku-5-5",
        content=content,
        stop_reason=stop_reason,
        usage=Usage(input_tokens=1, output_tokens=1),
    )


def make_status_error(
    error_class: type[APIStatusError], status_code: int
) -> APIStatusError:
    """Build an SDK status error of the given class and HTTP status."""
    response = Response(status_code, request=FAKE_REQUEST)
    return error_class("test error", response=response, body=None)
