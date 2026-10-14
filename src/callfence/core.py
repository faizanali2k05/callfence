from __future__ import annotations

import asyncio
import inspect
from dataclasses import dataclass
from time import monotonic
from typing import Any, Awaitable, Callable


@dataclass(frozen=True)
class CallResult:
    ok: bool
    value: Any = None
    error: BaseException | None = None
    elapsed: float = 0.0
    timed_out: bool = False

    @property
    def error_type(self) -> str | None:
        return type(self.error).__name__ if self.error else None

    def as_dict(self) -> dict[str, Any]:
        return {
            "ok": self.ok,
            "value": self.value,
            "error": str(self.error) if self.error else None,
            "error_type": self.error_type,
            "elapsed": self.elapsed,
            "timed_out": self.timed_out,
        }


async def run(call: Callable[[], Any | Awaitable[Any]], timeout: float) -> CallResult:
    """Run a callable behind a deadline and return a consistent boundary.

    Synchronous callables are moved to a worker thread so the event loop stays
    responsive. A timed-out thread cannot be forcefully killed; callers should
    make such functions idempotent or provide their own cancellation mechanism.
    """

    if timeout <= 0:
        raise ValueError("timeout must be positive")
    started = monotonic()

    async def invoke() -> Any:
        if inspect.iscoroutinefunction(call):
            result = call()
        else:
            result = await asyncio.to_thread(call)
        if inspect.isawaitable(result):
            return await result
        return result

    try:
        value = await asyncio.wait_for(invoke(), timeout)
        return CallResult(True, value=value, elapsed=monotonic() - started)
    except asyncio.TimeoutError as exc:
        return CallResult(False, error=exc, elapsed=monotonic() - started, timed_out=True)
    except Exception as exc:
        return CallResult(False, error=exc, elapsed=monotonic() - started)
