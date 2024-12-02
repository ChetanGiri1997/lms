from bson import ObjectId
from pydantic import GetJsonSchemaHandler
from pydantic_core import core_schema
from typing import Any


class PyObjectId(ObjectId):
    """
    Custom type to integrate MongoDB's ObjectId with Pydantic v2.
    """

    @classmethod
    def __get_pydantic_core_schema__(
        cls, source_type: Any, handler: GetJsonSchemaHandler
    ) -> core_schema.CoreSchema:
        """
        Defines the validation and schema logic for PyObjectId.

        This schema ensures that values are either instances of ObjectId or valid ObjectId strings.
        """
        return core_schema.union_schema([
            core_schema.is_instance_schema(ObjectId),  # Accept actual ObjectId instances
            core_schema.chain_schema([
                core_schema.str_schema(),  # Accept strings
                core_schema.no_info_plain_validator_function(cls.validate),  # Validate the string as ObjectId
            ]),
        ])

    @classmethod
    def validate(cls, value: Any) -> ObjectId:
        """
        Validates the input as a valid ObjectId.

        Args:
            value (Any): The input value to validate.

        Returns:
            ObjectId: A valid ObjectId instance.

        Raises:
            ValueError: If the value is not a valid ObjectId.
        """
        if not ObjectId.is_valid(value):
            raise ValueError("Invalid ObjectId")
        return ObjectId(value)

    @classmethod
    def __get_pydantic_json_schema__(
        cls, schema: core_schema.CoreSchema, handler: GetJsonSchemaHandler
    ) -> dict:
        """
        Generates the JSON schema for PyObjectId.

        Args:
            schema (core_schema.CoreSchema): The core schema.
            handler (GetJsonSchemaHandler): The handler to process the schema.

        Returns:
            dict: The updated JSON schema.
        """
        json_schema = handler(schema)
        json_schema.update(type="string")  # Represent ObjectId as a string in JSON
        return json_schema
