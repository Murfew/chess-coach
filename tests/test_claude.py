import re

import pytest
from anthropic import (
    Anthropic,
    APIConnectionError,
    APIStatusError,
    APITimeoutError,
    AuthenticationError,
    BadRequestError,
    InternalServerError,
    NotFoundError,
    OverloadedError,
    PaymentRequiredError,
    PermissionDeniedError,
    RateLimitError,
    Timeout,
)
from anthropic.types import ContentBlock, Message, StopReason
from fake_claude import (
    FAKE_API_KEY,
    FAKE_REQUEST,
    MODEL,
    ReplyWith,
    make_message,
    make_status_error,
    text_block,
    thinking_block,
)
from httpx2 import codes

from chess_coach.claude import (
    CONNECT_TIMEOUT,
    MAX_TOKENS,
    READ_TIMEOUT,
    ClaudeError,
    Result,
    build_client,
    get_answer,
)

QUESTION = "Some question..."
OVERLOADED = 529


def test_returns_text_after_thinking_block(
    reply_with: ReplyWith, client: Anthropic
) -> None:
    answer = "Answer to the question..."
    reply_with(
        make_message(
            [thinking_block(), text_block(answer)],
            "end_turn",
        )
    )

    result = get_answer(client, MODEL, QUESTION)

    assert result == Result(answer=answer, outcome="answered")


def test_refusal_without_text_is_declined(
    reply_with: ReplyWith, client: Anthropic
) -> None:
    reply_with(make_message([], "refusal"))

    result = get_answer(client, MODEL, QUESTION)

    assert result == Result(answer="", outcome="declined")


@pytest.mark.parametrize(
    (
        "content",
        "stop_reason",
    ),
    [
        pytest.param(thinking_block(), "max_tokens", id="thinking-max-tokens"),
        pytest.param(
            text_block(""),
            "model_context_window_exceeded",
            id="text-exceeded-context",
        ),
    ],
)
def test_cut_off_outcomes(
    reply_with: ReplyWith,
    client: Anthropic,
    content: ContentBlock,
    stop_reason: StopReason,
) -> None:
    reply_with(make_message([content], stop_reason))

    result = get_answer(client, MODEL, QUESTION)

    assert result == Result(answer="", outcome="cut off")


@pytest.mark.parametrize(
    ("stop_reason", "expected_fragment"),
    [
        pytest.param("stop_sequence", "stop_sequence"),
        pytest.param("pause_turn", "pause_turn"),
        pytest.param("tool_use", "tool_use"),
        pytest.param(None, "no stop reason"),
    ],
)
def test_unexpected_stop_reason_raises(
    reply_with: ReplyWith,
    client: Anthropic,
    stop_reason: StopReason | None,
    expected_fragment: str,
) -> None:
    reply_with(make_message([text_block("some answer...")], stop_reason))

    with pytest.raises(ClaudeError, match=expected_fragment):
        get_answer(client, MODEL, QUESTION)


def test_answered_without_text_raises(
    reply_with: ReplyWith,
    client: Anthropic,
) -> None:
    reply_with(make_message([text_block("")], "end_turn"))

    with pytest.raises(ClaudeError):
        get_answer(client, MODEL, QUESTION)


def test_sends_model_question_and_max_tokens(
    monkeypatch: pytest.MonkeyPatch,
    client: Anthropic,
) -> None:
    args: dict[str, object] = {}

    def fake_create(**kwargs: object) -> Message:
        args.update(kwargs)

        return make_message([text_block("some answer...")], "end_turn")

    monkeypatch.setattr(client.messages, "create", fake_create)

    get_answer(client, MODEL, QUESTION)

    assert args.get("model") == MODEL
    assert args.get("max_tokens") == MAX_TOKENS
    assert args.get("messages") == [{"role": "user", "content": QUESTION}]


@pytest.mark.parametrize(
    ("error_class", "status_code", "expected_fragment"),
    [
        pytest.param(
            BadRequestError,
            codes.BAD_REQUEST,
            "rejected the request",
            id="400-bad-request",
        ),
        pytest.param(
            AuthenticationError,
            codes.UNAUTHORIZED,
            "ANTHROPIC_API_KEY",
            id="401-bad-key",
        ),
        pytest.param(
            PermissionDeniedError,
            codes.FORBIDDEN,
            "workspace access",
            id="403-permission-denied",
        ),
        pytest.param(NotFoundError, codes.NOT_FOUND, MODEL, id="404-unknown-model"),
        pytest.param(
            RateLimitError,
            codes.TOO_MANY_REQUESTS,
            "rate or spend limit",
            id="429-rate-limited",
        ),
        pytest.param(
            InternalServerError,
            codes.INTERNAL_SERVER_ERROR,
            "having problems (status 500)",
            id="500-server-error",
        ),
        pytest.param(
            OverloadedError,
            OVERLOADED,
            "having problems (status 529)",
            id="529-overloaded",
        ),
        pytest.param(
            PaymentRequiredError,
            codes.PAYMENT_REQUIRED,
            "request failed (status 402)",
            id="402-unhandled-status",
        ),
    ],
)
def test_status_errors_become_claude_error(
    reply_with: ReplyWith,
    client: Anthropic,
    error_class: type[APIStatusError],
    status_code: int,
    expected_fragment: str,
) -> None:
    status_error = make_status_error(error_class, status_code)
    reply_with(status_error)

    with pytest.raises(ClaudeError, match=re.escape(expected_fragment)) as excinfo:
        get_answer(client, MODEL, QUESTION)

    assert excinfo.value.__cause__ is status_error


@pytest.mark.parametrize(
    ("connection_error", "expected_fragment"),
    [
        pytest.param(
            APITimeoutError(FAKE_REQUEST), "didn't respond in time", id="timeout"
        ),
        pytest.param(
            APIConnectionError(request=FAKE_REQUEST),
            "couldn't reach the Claude API",
            id="no-connection",
        ),
    ],
)
def test_network_errors_become_claude_error(
    reply_with: ReplyWith,
    client: Anthropic,
    connection_error: APIConnectionError,
    expected_fragment: str,
) -> None:
    reply_with(connection_error)

    with pytest.raises(ClaudeError, match=re.escape(expected_fragment)) as excinfo:
        get_answer(client, MODEL, QUESTION)

    assert excinfo.value.__cause__ is connection_error


def test_build_client_sets_timeouts() -> None:
    client = build_client(FAKE_API_KEY)

    assert isinstance(client.timeout, Timeout)

    assert client.timeout.connect == CONNECT_TIMEOUT
    assert client.timeout.read == READ_TIMEOUT
