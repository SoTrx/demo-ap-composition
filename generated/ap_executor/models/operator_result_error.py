from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import ComposedTypeWrapper, Parsable, ParseNode, ParseNodeHelper, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .operator_result_error_member1 import OperatorResult_errorMember1

@dataclass
class OperatorResult_error(ComposedTypeWrapper, Parsable):
    """
    Composed type wrapper for classes OperatorResult_errorMember1, str
    """
    # Composed type representation for type OperatorResult_errorMember1
    operator_result_error_member1: Optional[OperatorResult_errorMember1] = None
    # Composed type representation for type str
    string: Optional[str] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> OperatorResult_error:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: OperatorResult_error
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        result = OperatorResult_error()
        if string_value := parse_node.get_str_value():
            result.string = string_value
        else:
            from .operator_result_error_member1 import OperatorResult_errorMember1

            result.operator_result_error_member1 = OperatorResult_errorMember1()
        return result
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        from .operator_result_error_member1 import OperatorResult_errorMember1

        if self.operator_result_error_member1:
            return ParseNodeHelper.merge_deserializers_for_intersection_wrapper(self.operator_result_error_member1)
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
            writer.write_object_value(None, self.operator_result_error_member1)
    

