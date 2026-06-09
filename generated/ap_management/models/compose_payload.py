from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import AdditionalDataHolder, Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .compose_payload_ap1 import ComposePayload_ap1
    from .compose_payload_ap2 import ComposePayload_ap2

@dataclass
class ComposePayload(AdditionalDataHolder, Parsable):
    # Stores additional data not described in the OpenAPI description found when deserializing. Can be used for serialization as well.
    additional_data: dict[str, Any] = field(default_factory=dict)

    # The ap1 property
    ap1: Optional[ComposePayload_ap1] = None
    # The ap2 property
    ap2: Optional[ComposePayload_ap2] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> ComposePayload:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: ComposePayload
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return ComposePayload()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        from .compose_payload_ap1 import ComposePayload_ap1
        from .compose_payload_ap2 import ComposePayload_ap2

        from .compose_payload_ap1 import ComposePayload_ap1
        from .compose_payload_ap2 import ComposePayload_ap2

        fields: dict[str, Callable[[Any], None]] = {
            "ap1": lambda n : setattr(self, 'ap1', n.get_object_value(ComposePayload_ap1)),
            "ap2": lambda n : setattr(self, 'ap2', n.get_object_value(ComposePayload_ap2)),
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
        writer.write_object_value("ap1", self.ap1)
        writer.write_object_value("ap2", self.ap2)
        writer.write_additional_data_value(self.additional_data)
    

