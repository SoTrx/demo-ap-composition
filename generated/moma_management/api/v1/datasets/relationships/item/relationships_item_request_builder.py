from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.base_request_builder import BaseRequestBuilder
from kiota_abstractions.base_request_configuration import RequestConfiguration
from kiota_abstractions.default_query_parameters import QueryParameters
from kiota_abstractions.get_path_parameters import get_path_parameters
from kiota_abstractions.method import Method
from kiota_abstractions.request_adapter import RequestAdapter
from kiota_abstractions.request_information import RequestInformation
from kiota_abstractions.request_option import RequestOption
from kiota_abstractions.serialization import Parsable, ParsableFactory
from typing import Any, Optional, TYPE_CHECKING, Union
from warnings import warn

if TYPE_CHECKING:
    from ......models.dataset_relationship_output import DatasetRelationshipOutput
    from ......models.h_t_t_p_validation_error import HTTPValidationError

class RelationshipsItemRequestBuilder(BaseRequestBuilder):
    """
    Builds and executes requests for operations under /api/v1/datasets/relationships/{id}
    """
    def __init__(self,request_adapter: RequestAdapter, path_parameters: Union[str, dict[str, Any]]) -> None:
        """
        Instantiates a new RelationshipsItemRequestBuilder and sets the default values.
        param path_parameters: The raw url or the url-template parameters for the request.
        param request_adapter: The request adapter to use to execute the requests.
        Returns: None
        """
        super().__init__(request_adapter, "{+baseurl}/api/v1/datasets/relationships/{id}", path_parameters)
    
    async def delete(self,request_configuration: Optional[RequestConfiguration[QueryParameters]] = None) -> None:
        """
        Delete a DatasetRelationship by its root node ID.Only the relationship's internal nodes are removed; the two linked``sc:Dataset`` nodes are left intact.**Required role:** ``dg_admin`` / ``dg_dataset-curator`` / system.
        param request_configuration: Configuration for the request such as headers, query parameters, and middleware options.
        Returns: None
        """
        request_info = self.to_delete_request_information(
            request_configuration
        )
        from ......models.h_t_t_p_validation_error import HTTPValidationError

        error_mapping: dict[str, type[ParsableFactory]] = {
            "422": HTTPValidationError,
        }
        if not self.request_adapter:
            raise Exception("Http core is null") 
        return await self.request_adapter.send_no_response_content_async(request_info, error_mapping)
    
    async def get(self,request_configuration: Optional[RequestConfiguration[QueryParameters]] = None) -> Optional[DatasetRelationshipOutput]:
        """
        Retrieve a DatasetRelationship (shallow) by its root node ID.Only the root ``BasicDLElement`` node and its internal``PropertyComparison``/``TextEvidence`` subgraph are returned; thereferenced ``sc:Dataset`` nodes are not recursed into.**Required permission:** ``dg_ds-browse`` on **both** datasets linked bythe relationship, or realm role ``dg_admin`` / ``dg_dataset-curator``.
        param request_configuration: Configuration for the request such as headers, query parameters, and middleware options.
        Returns: Optional[DatasetRelationshipOutput]
        """
        request_info = self.to_get_request_information(
            request_configuration
        )
        from ......models.h_t_t_p_validation_error import HTTPValidationError

        error_mapping: dict[str, type[ParsableFactory]] = {
            "422": HTTPValidationError,
        }
        if not self.request_adapter:
            raise Exception("Http core is null") 
        from ......models.dataset_relationship_output import DatasetRelationshipOutput

        return await self.request_adapter.send_async(request_info, DatasetRelationshipOutput, error_mapping)
    
    def to_delete_request_information(self,request_configuration: Optional[RequestConfiguration[QueryParameters]] = None) -> RequestInformation:
        """
        Delete a DatasetRelationship by its root node ID.Only the relationship's internal nodes are removed; the two linked``sc:Dataset`` nodes are left intact.**Required role:** ``dg_admin`` / ``dg_dataset-curator`` / system.
        param request_configuration: Configuration for the request such as headers, query parameters, and middleware options.
        Returns: RequestInformation
        """
        request_info = RequestInformation(Method.DELETE, self.url_template, self.path_parameters)
        request_info.configure(request_configuration)
        request_info.headers.try_add("Accept", "application/json")
        return request_info
    
    def to_get_request_information(self,request_configuration: Optional[RequestConfiguration[QueryParameters]] = None) -> RequestInformation:
        """
        Retrieve a DatasetRelationship (shallow) by its root node ID.Only the root ``BasicDLElement`` node and its internal``PropertyComparison``/``TextEvidence`` subgraph are returned; thereferenced ``sc:Dataset`` nodes are not recursed into.**Required permission:** ``dg_ds-browse`` on **both** datasets linked bythe relationship, or realm role ``dg_admin`` / ``dg_dataset-curator``.
        param request_configuration: Configuration for the request such as headers, query parameters, and middleware options.
        Returns: RequestInformation
        """
        request_info = RequestInformation(Method.GET, self.url_template, self.path_parameters)
        request_info.configure(request_configuration)
        request_info.headers.try_add("Accept", "application/json")
        return request_info
    
    def with_url(self,raw_url: str) -> RelationshipsItemRequestBuilder:
        """
        Returns a request builder with the provided arbitrary URL. Using this method means any other path or query parameters are ignored.
        param raw_url: The raw URL to use for the request builder.
        Returns: RelationshipsItemRequestBuilder
        """
        if raw_url is None:
            raise TypeError("raw_url cannot be null.")
        return RelationshipsItemRequestBuilder(self.request_adapter, raw_url)
    
    @dataclass
    class RelationshipsItemRequestBuilderDeleteRequestConfiguration(RequestConfiguration[QueryParameters]):
        """
        Configuration for the request such as headers, query parameters, and middleware options.
        """
        warn("This class is deprecated. Please use the generic RequestConfiguration class generated by the generator.", DeprecationWarning)
    
    @dataclass
    class RelationshipsItemRequestBuilderGetRequestConfiguration(RequestConfiguration[QueryParameters]):
        """
        Configuration for the request such as headers, query parameters, and middleware options.
        """
        warn("This class is deprecated. Please use the generic RequestConfiguration class generated by the generator.", DeprecationWarning)
    

