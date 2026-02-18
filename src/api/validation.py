import pathlib
import json
import jsonschema


class Validator:

    expected_schema_path = (
        pathlib.Path(__file__).resolve().parent / "expected_schema.json"
    )

    def __init__(self, record):
        self.record = record
        self.expected_schema = self._read_schema()

    def _read_schema(self):
        with open(self.expected_schema_path, encoding="utf-8") as f:
            return json.load(f)

    def validate(self):
        jsonschema.validate(self.record, self.expected_schema)
