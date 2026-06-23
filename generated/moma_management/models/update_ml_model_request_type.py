from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import ComposedTypeWrapper, Parsable, ParseNode, ParseNodeHelper, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .update_ml_model_request_type_member1 import UpdateMlModelRequest_typeMember1

@dataclass
class UpdateMlModelRequest_type(ComposedTypeWrapper, Parsable):
    """
    Composed type wrapper for classes str, UpdateMlModelRequest_typeMember1
    """
    # Composed type representation for type str
    string: Optional[str] = None
    # Composed type representation for type UpdateMlModelRequest_typeMember1
    update_ml_model_request_type_member1: Optional[UpdateMlModelRequest_typeMember1] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> UpdateMlModelRequest_type:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: UpdateMlModelRequest_type
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        result = UpdateMlModelRequest_type()
        if string_value := parse_node.get_str_value():
            result.string = string_value
        else:
            from .update_ml_model_request_type_member1 import UpdateMlModelRequest_typeMember1

            result.update_ml_model_request_type_member1 = UpdateMlModelRequest_typeMember1()
        return result
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        from .update_ml_model_request_type_member1 import UpdateMlModelRequest_typeMember1

        if self.update_ml_model_request_type_member1:
            return ParseNodeHelper.merge_deserializers_for_intersection_wrapper(self.update_ml_model_request_type_member1)
        return {}
    
    def serialize(self,writer: SerializationWriter) -> None:
        """
        Serializes information the current object
        param writer: Serialization writer to use to serialize this model
        Returns: None
        """
        if writer is None:
            raise TypeError("writer cannot be null.")
        if self.string:
            writer.write_str_value(None, self.string)
        else:
            writer.write_object_value(None, self.update_ml_model_request_type_member1)
    

