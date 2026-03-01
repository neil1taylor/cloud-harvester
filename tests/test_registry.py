from cloud_harvester.collectors.base import BaseCollector
from cloud_harvester.collectors.registry import CollectorRegistry


class FakeCollector(BaseCollector):
    domain = "classic"
    resource_type = "test"
    worksheet_name = "vTest"

    def collect(self, client, context):
        return [{"id": 1, "name": "test"}]


def test_register_and_get_collector():
    registry = CollectorRegistry()
    collector = FakeCollector()
    registry.register(collector)
    assert registry.get("classic", "test") is collector


def test_get_by_domain():
    registry = CollectorRegistry()
    c1 = FakeCollector()
    c1.resource_type = "a"
    c2 = FakeCollector()
    c2.resource_type = "b"
    c2.domain = "vpc"
    registry.register(c1)
    registry.register(c2)
    classic = registry.get_by_domain("classic")
    assert len(classic) == 1
    vpc = registry.get_by_domain("vpc")
    assert len(vpc) == 1
