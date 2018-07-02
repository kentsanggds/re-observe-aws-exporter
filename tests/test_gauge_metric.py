import pytest

from app import GaugeMetric


def test_emit_sets_the_gauge_metric(mocker):
    def test_number_count():
        return 11
    gauge_metric = GaugeMetric(test_number_count, "test_number_count")
    gauge_metric.emit()

    # need to mock out self.gauge.set to check the passed args
    assert False
