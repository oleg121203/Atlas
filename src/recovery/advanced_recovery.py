import hashlib
import pickle
import time
from enum import Enum
from typing import Any, Callable, Dict


class RecoveryStrategy(Enum):
    RESTART = "restart"
    ROLLBACK = "rollback"
    FAILOVER = "failover"
    GRACEFUL_DEGRADATION = "graceful_degradation"


class StateManager:
    def __init__(self, checkpoint_interval: int = 300):  # 5 хвилин
        self.checkpoint_interval = checkpoint_interval
        self.state_history = []
        self.current_state_hash = None

    async def create_checkpoint(self, state: Dict[str, Any]):
        """Створює контрольну точку стану системи"""
        checkpoint = {
            "timestamp": time.time(),
            "state": state,
            "hash": hashlib.md5(pickle.dumps(state)).hexdigest(),
        }

        # Зберігаємо тільки останні 10 чекпоінтів
        self.state_history.append(checkpoint)
        if len(self.state_history) > 10:
            self.state_history.pop(0)

        # Зберігаємо на диск
        with open(f"checkpoints/checkpoint_{checkpoint['timestamp']}.pkl", "wb") as f:
            pickle.dump(checkpoint, f)

    async def restore_from_checkpoint(self, checkpoint_index: int = -1):
        """Відновлює стан з контрольної точки"""
        if not self.state_history:
            raise Exception("No checkpoints available")

        checkpoint = self.state_history[checkpoint_index]
        return checkpoint["state"]


class CircuitBreaker:
    def __init__(self, failure_threshold: int = 5, recovery_timeout: int = 60):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN

    async def call(self, func: Callable, *args, **kwargs):
        if self.state == "OPEN":
            if time.time() - self.last_failure_time > self.recovery_timeout:
                self.state = "HALF_OPEN"
            else:
                raise Exception("Circuit breaker is OPEN")

        try:
            result = await func(*args, **kwargs)
            if self.state == "HALF_OPEN":
                self.state = "CLOSED"
                self.failure_count = 0
            return result
        except Exception as e:
            self.failure_count += 1
            self.last_failure_time = time.time()

            if self.failure_count >= self.failure_threshold:
                self.state = "OPEN"
            raise e
