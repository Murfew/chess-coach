from collections.abc import Callable

from anthropic import APIStatusError
from anthropic.types import (
    ContentBlock,
    Message,
    StopReason,
    TextBlock,
    ThinkingBlock,
    Usage,
)
from httpx2 import Request, Response

FAKE_REQUEST = Request("POST", "https://api.anthropic.com/v1/messages")
MODEL = "test-model"
FAKE_API_KEY = "fake-api-key"

type ReplyWith = Callable[[Message | Exception], None]
"""The `reply_with` fixture: sets what `client.messages.create` returns or raises."""


def thinking_block() -> ThinkingBlock:
    """Build a thinking block; its content never matters to the app."""
    return ThinkingBlock(type="thinking", thinking="", signature="fake-signature")


def text_block(text: str) -> TextBlock:
    """Build a text block holding the given text."""
    return TextBlock(type="text", text=text)


def make_message(
    content: list[ContentBlock], stop_reason: StopReason | None
) -> Message:
    """Build a response with the given blocks and stop reason."""
    return Message(
        id="msg_test",
        type="message",
        role="assistant",
        model=MODEL,
        content=content,
        stop_reason=stop_reason,
        usage=Usage(input_tokens=1, output_tokens=1),
    )


def make_status_error(
    error_class: type[APIStatusError], status_code: int, body: object | None = None
) -> APIStatusError:
    """Build an SDK status error with the given class, status and body."""
    response = Response(status_code, request=FAKE_REQUEST)
    return error_class("test error", response=response, body=body)
