from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import AdditionalDataHolder, Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .update_ml_model_request_name import UpdateMlModelRequest_name
    from .update_ml_model_request_type import UpdateMlModelRequest_type

@dataclass
class UpdateMlModelRequest(AdditionalDataHolder, Parsable):
    # Stores additional data not described in the OpenAPI description found when deserializing. Can be used for serialization as well.
    additional_data: dict[str, Any] = field(default_factory=dict)

    # The name property
    name: Optional[UpdateMlModelRequest_name] = None
    # The type property
    type: Optional[UpdateMlModelRequest_type] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> UpdateMlModelRequest:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: UpdateMlModelRequest
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return UpdateMlModelRequest()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        from .update_ml_model_request_name import UpdateMlModelRequest_name
        from .update_ml_model_request_type import UpdateMlModelRequest_type

        from .update_ml_model_request_name import UpdateMlModelRequest_name
        from .update_ml_model_request_type import UpdateMlModelRequest_type

        fields: dict[str, Callable[[Any], None]] = {
            "name": lambda n : setattr(self, 'name', n.get_object_value(UpdateMlModelRequest_name)),
            "type": lambda n : setattr(self, 'type', n.get_object_value(UpdateMlModelRequest_type)),
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
        writer.write_object_value("name", self.name)
        writer.write_object_value("type", self.type)
        writer.write_additional_data_value(self.additional_data)
    

