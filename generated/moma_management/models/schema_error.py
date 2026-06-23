from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import AdditionalDataHolder, Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .schema_error_params import SchemaError_params

@dataclass
class SchemaError(AdditionalDataHolder, Parsable):
    """
    Single validation error in AJV format.
    """
    # Stores additional data not described in the OpenAPI description found when deserializing. Can be used for serialization as well.
    additional_data: dict[str, Any] = field(default_factory=dict)

    # The instancePath property
    instance_path: Optional[str] = None
    # The keyword property
    keyword: Optional[str] = None
    # The message property
    message: Optional[str] = None
    # The params property
    params: Optional[SchemaError_params] = None
    # The schemaPath property
    schema_path: Optional[str] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> SchemaError:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: SchemaError
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return SchemaError()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        from .schema_error_params import SchemaError_params

        from .schema_error_params import SchemaError_params

        fields: dict[str, Callable[[Any], None]] = {
            "instancePath": lambda n : setattr(self, 'instance_path', n.get_str_value()),
            "keyword": lambda n : setattr(self, 'keyword', n.get_str_value()),
            "message": lambda n : setattr(self, 'message', n.get_str_value()),
            "params": lambda n : setattr(self, 'params', n.get_object_value(SchemaError_params)),
            "schemaPath": lambda n : setattr(self, 'schema_path', n.get_str_value()),
        }
        return fields
    
    def serialize(self,writer: SerializationWriter) -> None:
        """
        Serializes information the current object
        param writer: Serialization writer to use to serialize this model
        Returns: None
        """
        if writer is None:
            raise TypeError("writer cannot be null.")
        writer.write_str_value("instancePath", self.instance_path)
        writer.write_str_value("keyword", self.keyword)
        writer.write_str_value("message", self.message)
        writer.write_object_value("params", self.params)
        writer.write_str_value("schemaPath", self.schema_path)
        writer.write_additional_data_value(self.additional_data)
    

