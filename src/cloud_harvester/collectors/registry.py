from cloud_harvester.collectors.base import BaseCollector


class CollectorRegistry:
    def __init__(self):
        self._collectors: dict[str, BaseCollector] = {}

    def register(self, collector: BaseCollector) -> None:
        key = f"{collector.domain}:{collector.resource_type}"
        self._collectors[key] = collector

    def get(self, domain: str, resource_type: str) -> BaseCollector | None:
        return self._collectors.get(f"{domain}:{resource_type}")

    def get_by_domain(self, domain: str) -> list[BaseCollector]:
        return [c for k, c in self._collectors.items() if k.startswith(f"{domain}:")]

    def get_all(self) -> list[BaseCollector]:
        return list(self._collectors.values())

    def get_domains(self) -> list[str]:
        return sorted(set(c.domain for c in self._collectors.values()))
