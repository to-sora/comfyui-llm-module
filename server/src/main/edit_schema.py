from .errors import UserError
import json
from .settings import APP


def definitions():
    result = {}
    for path in sorted((APP / "config/content-config").glob("edits-*.json")):
        result.update(json.loads(path.read_text()))
    return result


def validate(operation, params):
    schemas = definitions()
    if operation not in schemas:
        raise UserError("Unknown image edit operation")
    schema = schemas[operation]
    if set(params) - set(schema):
        raise UserError("Unknown edit fields: " + ", ".join(sorted(set(params) - set(schema))))
    result = {}
    for name, spec in schema.items():
        value = params.get(name, spec[1])
        if spec[0] == "number":
            if isinstance(value, bool) or not isinstance(value, (int, float)) or not spec[2] <= value <= spec[3]:
                raise UserError(f"{name}: expected {spec[2]}..{spec[3]}")
        elif spec[0] == "boolean" and not isinstance(value, bool):
            raise UserError(f"{name}: expected boolean")
        elif spec[0] == "string" and (not isinstance(value, str) or len(value) > 10000):
            raise UserError(f"{name}: expected short text")
        elif spec[0] == "enum" and value not in spec[2:]:
            raise UserError(f"{name}: expected one of {spec[2:]}")
        result[name] = value
    return result
