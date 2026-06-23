from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import AdditionalDataHolder, Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union
from uuid import UUID

if TYPE_CHECKING:
    from .type import Type

@dataclass
class EvaluationRequest(AdditionalDataHolder, Parsable):
    # Stores additional data not described in the OpenAPI description found when deserializing. Can be used for serialization as well.
    additional_data: dict[str, Any] = field(default_factory=dict)

    # The dimension property
    dimension: Optional[Type] = None
    # The evaluation property
    evaluation: Optional[str] = None
    # The execution_id property
    execution_id: Optional[UUID] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> EvaluationRequest:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: EvaluationRequest
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return EvaluationRequest()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        from .type import Type

        from .type import Type

        fields: dict[str, Callable[[Any], None]] = {
            "dimension": lambda n : setattr(self, 'dimension', n.get_enum_value(Type)),
            "evaluation": lambda n : setattr(self, 'evaluation', n.get_str_value()),
            "execution_id": lambda n : setattr(self, 'execution_id', n.get_uuid_value()),
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
        writer.write_enum_value("dimension", self.dimension)
        writer.write_str_value("evaluation", self.evaluation)
        writer.write_uuid_value("execution_id", self.execution_id)
        writer.write_additional_data_value(self.additional_data)
    

