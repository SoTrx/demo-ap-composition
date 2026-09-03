from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import AdditionalDataHolder, Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .analytical_pattern import AnalyticalPattern
    from .ap_instance_state import ApInstance_state

@dataclass
class ApInstance(AdditionalDataHolder, Parsable):
    """
    An AP *instance*: an AP template plus the runtime values to execute it with.``state`` is namespaced by operator node id, mapping each operator's inputname to its caller-supplied value (or, once executed, its output):``{node_id: {name: value}}``.
    """
    # Stores additional data not described in the OpenAPI description found when deserializing. Can be used for serialization as well.
    additional_data: dict[str, Any] = field(default_factory=dict)

    # The ap property
    ap: Optional[AnalyticalPattern] = None
    # The state property
    state: Optional[ApInstance_state] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> ApInstance:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: ApInstance
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return ApInstance()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        from .analytical_pattern import AnalyticalPattern
        from .ap_instance_state import ApInstance_state

        from .analytical_pattern import AnalyticalPattern
        from .ap_instance_state import ApInstance_state

        fields: dict[str, Callable[[Any], None]] = {
            "ap": lambda n : setattr(self, 'ap', n.get_object_value(AnalyticalPattern)),
            "state": lambda n : setattr(self, 'state', n.get_object_value(ApInstance_state)),
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
        writer.write_object_value("state", self.state)
        writer.write_additional_data_value(self.additional_data)
    

