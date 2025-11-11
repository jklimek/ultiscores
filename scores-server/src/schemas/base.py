"""Base Pydantic models with common configuration."""
from pydantic import BaseModel, ConfigDict


def to_camel_case(string: str) -> str:
    """Convert snake_case to camelCase."""
    components = string.split('_')
    return components[0] + ''.join(x.title() for x in components[1:])


class CamelCaseModel(BaseModel):
    """Base model that converts snake_case field names to camelCase in JSON."""
    
    model_config = ConfigDict(
        alias_generator=to_camel_case,
        populate_by_name=True,  # Allow both snake_case and camelCase when parsing
        from_attributes=True,  # Allow ORM model conversion
    )

