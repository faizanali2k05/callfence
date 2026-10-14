# callfence

Put a deadline around a synchronous or asynchronous callable and get a consistent result boundary.

```bash
python -m pip install callfence
```

```python
from callfence import run

result = await run(lambda: client.fetch(), timeout=3)
if not result.ok:
    logger.warning("call failed", extra=result.as_dict())
```

Synchronous callables run in a worker thread so they do not block the event loop; async callables are awaited directly. Timeouts are represented as data. A worker thread cannot be forcibly stopped, so use cooperative cancellation for side-effectful operations.
