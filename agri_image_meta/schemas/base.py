from pydantic import BaseModel, ConfigDict
from agri_image_meta.utils.namespaces import JSONLD_CONTEXT
from typing import Any
import datetime
from agri_image_meta.utils.file_system import get_strftime


class RDFModel(BaseModel):
    model_config = ConfigDict(
        use_enum_values=True
    )  # to make sure when export for model we do not get !!python:: etc

    rdf_type: str  # e.g. "dcat:Dataset"

    def model_dump(self, **kwargs) -> dict:
        """
        Override model_dump to convert datetime objects using get_strftime.
        """
        data = super().model_dump(**kwargs)
        return self._convert_datetimes(data)

    def _convert_datetimes(self, obj: Any) -> Any:
        """
        Recursively convert datetime objects to ISO format strings using get_strftime.
        """
        if isinstance(obj, datetime.datetime):
            return get_strftime(obj)
        elif isinstance(obj, dict):
            return {k: self._convert_datetimes(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._convert_datetimes(item) for item in obj]
        return obj

    def to_jsonld(self, top_level: bool = True) -> dict:
        data = self._as_linked_data()

        result = {"@type": self.rdf_type, **data}

        if top_level:
            result["@context"] = JSONLD_CONTEXT

        return result

    def _as_linked_data(self) -> dict:
        mapped = {}

        for field_name, field in self.model_fields.items():
            value = getattr(self, field_name)

            if value is None:
                continue

            # Skip internal rdf_type field
            if field_name == "rdf_type":
                continue

            # Get URI from field metadata
            uri = None
            is_rdf_list = False
            if field.json_schema_extra:
                uri = field.json_schema_extra.get("uri")
                is_rdf_list = field.json_schema_extra.get("rdf_list", False)

            key = self._compact_uri(uri) if uri else field_name
            mapped[key] = self._convert_value(value, is_rdf_list)

        return mapped

    def _convert_value(self, value: Any, is_rdf_list=False):
        if isinstance(value, RDFModel):
            return value.to_jsonld(top_level=False)

        if isinstance(value, list):
            if is_rdf_list:
                return {"@list": value}
            return [self._convert_value(v) for v in value]

        # If it's a datetime or ISO date string, wrap with xsd:dateTime
        # Python datetime objects
        if isinstance(value, datetime.datetime):
            return {
                "@value": get_strftime(value),
                "@type": "http://www.w3.org/2001/XMLSchema#dateTime",
            }

        # # ISO 8601 strings
        if isinstance(value, str):
            try:
                datetime.datetime.fromisoformat(value.replace("Z", "+00:00"))
                return {"@value": value, "@type": "http://www.w3.org/2001/XMLSchema#dateTime"}
            except ValueError:
                pass

        return value

    def _compact_uri(self, uri: str) -> str:
        if not uri:
            return None

        for prefix, base in JSONLD_CONTEXT.items():
            if uri.startswith(base):
                return f"{prefix}:{uri[len(base) :]}"

        return uri  # fallback to full URI
