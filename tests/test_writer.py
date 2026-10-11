from uuid import uuid4

from mlops.services.writer.parse import parse_stream_entry


def test_writer_parses_valid_entry() -> None:
    run_id = uuid4()
    metric = parse_stream_entry({"run_id": str(run_id), "name": "loss", "value": "0.42", "step": "3"})
    assert metric is not None
    assert metric.run_id == run_id
    assert metric.name == "loss"
    assert metric.value == 0.42
    assert metric.step == 3


def test_writer_drops_invalid_entry() -> None:
    assert parse_stream_entry({"run_id": "nope", "name": "loss"}) is None
