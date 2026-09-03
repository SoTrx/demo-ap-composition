from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import AdditionalDataHolder, Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .operator_result_error import OperatorResult_error
    from .operator_result_execution_mode import OperatorResult_execution_mode
    from .operator_result_operator_version import OperatorResult_operator_version
    from .operator_result_service_instance import OperatorResult_service_instance
    from .operator_status import OperatorStatus

@dataclass
class OperatorResult(AdditionalDataHolder, Parsable):
    """
    Result of executing a single AP operator.
    """
    # Stores additional data not described in the OpenAPI description found when deserializing. Can be used for serialization as well.
    additional_data: dict[str, Any] = field(default_factory=dict)

    # The error property
    error: Optional[OperatorResult_error] = None
    # The execution_mode property
    execution_mode: Optional[OperatorResult_execution_mode] = None
    # The operator_id property
    operator_id: Optional[str] = None
    # The operator_labels property
    operator_labels: Optional[list[str]] = None
    # The operator_name property
    operator_name: Optional[str] = None
    # The operator_version property
    operator_version: Optional[OperatorResult_operator_version] = None
    # The service_instance property
    service_instance: Optional[OperatorResult_service_instance] = None
    # Status of a single operator execution.
    status: Optional[OperatorStatus] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> OperatorResult:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: OperatorResult
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return OperatorResult()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        from .operator_result_error import OperatorResult_error
        from .operator_result_execution_mode import OperatorResult_execution_mode
        from .operator_result_operator_version import OperatorResult_operator_version
        from .operator_result_service_instance import OperatorResult_service_instance
        from .operator_status import OperatorStatus

        from .operator_result_error import OperatorResult_error
        from .operator_result_execution_mode import OperatorResult_execution_mode
        from .operator_result_operator_version import OperatorResult_operator_version
        from .operator_result_service_instance import OperatorResult_service_instance
        from .operator_status import OperatorStatus

        fields: dict[str, Callable[[Any], None]] = {
            "error": lambda n : setattr(self, 'error', n.get_object_value(OperatorResult_error)),
            "execution_mode": lambda n : setattr(self, 'execution_mode', n.get_object_value(OperatorResult_execution_mode)),
            "operator_id": lambda n : setattr(self, 'operator_id', n.get_str_value()),
            "operator_labels": lambda n : setattr(self, 'operator_labels', n.get_collection_of_primitive_values(str)),
            "operator_name": lambda n : setattr(self, 'operator_name', n.get_str_value()),
            "operator_version": lambda n : setattr(self, 'operator_version', n.get_object_value(OperatorResult_operator_version)),
            "service_instance": lambda n : setattr(self, 'service_instance', n.get_object_value(OperatorResult_service_instance)),
            "status": lambda n : setattr(self, 'status', n.get_enum_value(OperatorStatus)),
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
        writer.write_object_value("error", self.error)
        writer.write_object_value("execution_mode", self.execution_mode)
        writer.write_str_value("operator_id", self.operator_id)
        writer.write_collection_of_primitive_values("operator_labels", self.operator_labels)
        writer.write_str_value("operator_name", self.operator_name)
        writer.write_object_value("operator_version", self.operator_version)
        writer.write_object_value("service_instance", self.service_instance)
        writer.write_enum_value("status", self.status)
        writer.write_additional_data_value(self.additional_data)
    

