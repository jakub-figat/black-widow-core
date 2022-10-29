from pydantic import BaseModel


def to_camel_case(field_name: str) -> str:
    words = field_name.split("_")
    return words[0] + "".join(word.capitalize() for word in words[1:])


class BaseSchema(BaseModel):
    class Config:
        orm_mode = True
        alias_generator = to_camel_case
        allow_population_by_field_name = True
