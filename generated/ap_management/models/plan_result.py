from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import AdditionalDataHolder, Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .analytical_pattern import AnalyticalPattern
    from .suggested_parameter import SuggestedParameter

@dataclass
class PlanResult(AdditionalDataHolder, Parsable):
    """
    The AP produced by the planner, plus the parameters needed to instantiate it.
    """
    # Stores additional data not described in the OpenAPI description found when deserializing. Can be used for serialization as well.
    additional_data: dict[str, Any] = field(default_factory=dict)

    # The ap property
    ap: Optional[AnalyticalPattern] = None
    # The instantiation_parameters property
    instantiation_parameters: Optional[list[SuggestedParameter]] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> PlanResult:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: PlanResult
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return PlanResult()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        from .analytical_pattern import AnalyticalPattern
        from .suggested_parameter import SuggestedParameter

        from .analytical_pattern import AnalyticalPattern
        from .suggested_parameter import SuggestedParameter

        fields: dict[str, Callable[[Any], None]] = {
            "ap": lambda n : setattr(self, 'ap', n.get_object_value(AnalyticalPattern)),
            "instantiation_parameters": lambda n : setattr(self, 'instantiation_parameters', n.get_collection_of_object_values(SuggestedParameter)),
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
        writer.write_object_value("ap", self.ap)
        writer.write_collection_of_object_values("instantiation_parameters", self.instantiation_parameters)
        writer.write_additional_data_value(self.additional_data)
    

