import asyncio
import time
from dataclasses import dataclass
from enum import Enum
from typing import Callable, Dict

import psutil


class HealthStatus(Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"


@dataclass
class HealthCheck:
    name: str
    status: HealthStatus
    message: str
    response_time: float
    timestamp: float


class HealthChecker:
    def __init__(self):
        self.checks: Dict[str, Callable] = {}
        self.results: Dict[str, HealthCheck] = {}

    def register_check(self, name: str, check_func: Callable):
        """Реєструє перевірку здоров'я"""
        self.checks[name] = check_func

    async def run_check(self, name: str) -> HealthCheck:
        """Виконує окрему перевірку"""
        start_time = time.time()
        try:
            result = await self.checks[name]()
            status = HealthStatus.HEALTHY if result else HealthStatus.UNHEALTHY
            message = "OK" if result else "Check failed"
        except Exception as e:
            status = HealthStatus.UNHEALTHY
            message = str(e)

        response_time = time.time() - start_time

        return HealthCheck(
            name=name,
            status=status,
            message=message,
            response_time=response_time,
            timestamp=time.time(),
        )

    async def run_all_checks(self) -> Dict[str, HealthCheck]:
        """Виконує всі перевірки здоров'я"""
        tasks = [self.run_check(name) for name in self.checks]
        results = await asyncio.gather(*tasks)

        self.results = {result.name: result for result in results}
        return self.results

    def get_overall_status(self) -> HealthStatus:
        """Повертає загальний статус системи"""
        if not self.results:
            return HealthStatus.UNHEALTHY

        unhealthy_count = sum(
            1 for r in self.results.values() if r.status == HealthStatus.UNHEALTHY
        )
        degraded_count = sum(
            1 for r in self.results.values() if r.status == HealthStatus.DEGRADED
        )

        if unhealthy_count > 0:
            return HealthStatus.UNHEALTHY
        elif degraded_count > 0:
            return HealthStatus.DEGRADED
        else:
            return HealthStatus.HEALTHY


# Приклади перевірок
async def database_health_check():
    """Перевірка підключення до бази даних"""
    # Тут має бути логіка перевірки БД
    return True


async def memory_health_check():
    """Перевірка використання пам'яті"""
    memory_percent = psutil.virtual_memory().percent
    return memory_percent < 90


async def disk_health_check():
    """Перевірка використання диска"""
    disk_percent = psutil.disk_usage("/").percent
    return disk_percent < 95
