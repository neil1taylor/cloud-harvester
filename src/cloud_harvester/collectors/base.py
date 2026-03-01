from abc import ABC, abstractmethod


class BaseCollector(ABC):
    domain: str = ""
    resource_type: str = ""
    worksheet_name: str = ""

    @abstractmethod
    def collect(self, client, context: dict) -> list[dict]:
        """Collect resources. Returns list of row dicts matching schema fields."""
        ...
