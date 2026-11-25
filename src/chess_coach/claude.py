from typing import Literal, NamedTuple

from anthropic import (
    Anthropic,
    APIConnectionError,
    APIStatusError,
    APITimeoutError,
    AuthenticationError,
    BadRequestError,
    InternalServerError,
    NotFoundError,
    PermissionDeniedError,
    RateLimitError,
    Timeout,
)
from anthropic.types import StopReason, TextBlock

MAX_TOKENS = 16_000
DEFAULT_TIMEOUT = 60
CONNECT_TIMEOUT = 5
READ_TIMEOUT = 300

type Outcome = Literal["answered", "cut off", "declined"]


class ClaudeError(Exception):
    """A Claude call that produced no usable answer.

    The message is one line written for the user. The SDK exception, if any,
    is attached as the cause.
    """


class Result(NamedTuple):
    """Claude's answer and whether it is complete.

    Attributes:
        answer: The answer text; may be partial or empty unless the outcome is
            "answered".
        outcome: Whether Claude answered fully, was cut off or declined.
    """

    answer: str
    outcome: Outcome


def _stop_reason_to_outcome(stop_reason: StopReason | None) -> Outcome:
    """Translate Claude's stop reason into this app's outcome."""
    match stop_reason:
        case "end_turn":
            return "answered"
        case "refusal":
            return "declined"
        case "max_tokens" | "model_context_window_exceeded":
            return "cut off"
        case "stop_sequence" | "pause_turn" | "tool_use":
            raise ClaudeError(f"Claude stopped unexpectedly ({stop_reason})")
        case None:
            raise ClaudeError("Claude's response had no stop reason")


def build_client(api_key: str) -> Anthropic:
    """Create a Claude client that uses only the given API key.

    Passing the key explicitly stops the SDK from falling back to other
    credentials it finds on the machine.

    Args:
        api_key: The key from settings, already unwrapped from `SecretStr`.

    Returns:
        A client to pass to `get_answer`.
    """
    return Anthropic(
        api_key=api_key,
        timeout=Timeout(DEFAULT_TIMEOUT, connect=CONNECT_TIMEOUT, read=READ_TIMEOUT),
    )


def get_answer(client: Anthropic, model: str, question: str) -> Result:
    """Ask Claude one question.

    Args:
        client: The client from `build_client`, or a fake in tests.
        model: The model ID to ask.
        question: The user's question.

    Returns:
        The answer text and its outcome.

    Raises:
        ClaudeError: The call failed or stopped for an unexpected reason.
    """
    try:
        response = client.messages.create(
            model=model,
            messages=[{"role": "user", "content": question}],
            max_tokens=MAX_TOKENS,
        )
    except AuthenticationError as err:
        raise ClaudeError(
            "the Claude API rejected your API key; check ANTHROPIC_API_KEY"
        ) from err
    except PermissionDeniedError as err:
        raise ClaudeError(
            "your API key isn't allowed to make this request; check your workspace access in the Claude Console"
        ) from err
    except NotFoundError as err:
        raise ClaudeError(
            f"model '{model}' doesn't exist or isn't available to your account; check CLAUDE_MODEL"
        ) from err
    except RateLimitError as err:
        raise ClaudeError("rate or spend limit reached; try again later") from err
    except InternalServerError as err:
        raise ClaudeError(
            f"the Claude API is having problems (status {err.status_code}); try again later"
        ) from err
    except BadRequestError as err:
        raise ClaudeError("the Claude API rejected the request (status 400)") from err
    except APIStatusError as err:
        raise ClaudeError(
            f"the Claude API request failed (status {err.status_code})"
        ) from err
    except APITimeoutError as err:
        raise ClaudeError("the Claude API didn't respond in time; try again") from err
    except APIConnectionError as err:
        raise ClaudeError(
            "couldn't reach the Claude API; check your internet connection"
        ) from err

    outcome = _stop_reason_to_outcome(response.stop_reason)

    text = "".join(
        block.text for block in response.content if isinstance(block, TextBlock)
    )

    if outcome == "answered" and not text:
        raise ClaudeError("Claude's answer contained no text")

    return Result(answer=text, outcome=outcome)
