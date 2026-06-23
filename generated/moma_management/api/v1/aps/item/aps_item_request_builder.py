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
    from .....models.analytical_pattern_output import AnalyticalPatternOutput
    from .....models.h_t_t_p_validation_error import HTTPValidationError
    from .evaluations.evaluations_request_builder import EvaluationsRequestBuilder

class ApsItemRequestBuilder(BaseRequestBuilder):
    """
    Builds and executes requests for operations under /api/v1/aps/{id}
    """
    def __init__(self,request_adapter: RequestAdapter, path_parameters: Union[str, dict[str, Any]]) -> None:
        """
        Instantiates a new ApsItemRequestBuilder and sets the default values.
        param path_parameters: The raw url or the url-template parameters for the request.
        param request_adapter: The request adapter to use to execute the requests.
        Returns: None
        """
        super().__init__(request_adapter, "", path_parameters)
    
    async def delete(self,request_configuration: Optional[RequestConfiguration[QueryParameters]] = None) -> None:
        """
        Delete an AnalyticalPattern by its root node ID.Only the AP root and its Operator nodes are removed; referenced datanodes (belonging to datasets) are left intact.**Required permission:** ``dg_ds-browse`` on **all** datasets referencedby the AP's ``input`` edges, or realm role ``dg_admin`` /``dg_dataset-curator``.
        param request_configuration: Configuration for the request such as headers, query parameters, and middleware options.
        Returns: None
        """
        request_info = self.to_delete_request_information(
            request_configuration
        )
        from .....models.h_t_t_p_validation_error import HTTPValidationError

        error_mapping: dict[str, type[ParsableFactory]] = {
            "422": HTTPValidationError,
        }
        if not self.request_adapter:
            raise Exception("Http core is null") 
        return await self.request_adapter.send_no_response_content_async(request_info, error_mapping)
    
    async def get(self,request_configuration: Optional[RequestConfiguration[ApsItemRequestBuilderGetQueryParameters]] = None) -> Optional[AnalyticalPatternOutput]:
        """
        Retrieve an AnalyticalPattern (shallow) by its root node ID.Only the root node, its Operator nodes, and the first-level Data/Usernodes reachable from the operators are returned.  The full datasetsubgraph is **not** recursed into.**Required permission:** ``dg_ds-browse`` on the referenced inputdataset, or realm role ``dg_admin`` / ``dg_dataset-curator``.Returns 404 on permission denial to prevent enumeration.
        param request_configuration: Configuration for the request such as headers, query parameters, and middleware options.
        Returns: Optional[AnalyticalPatternOutput]
        """
        request_info = self.to_get_request_information(
            request_configuration
        )
        from .....models.h_t_t_p_validation_error import HTTPValidationError

        error_mapping: dict[str, type[ParsableFactory]] = {
            "422": HTTPValidationError,
        }
        if not self.request_adapter:
            raise Exception("Http core is null") 
        from .....models.analytical_pattern_output import AnalyticalPatternOutput

        return await self.request_adapter.send_async(request_info, AnalyticalPatternOutput, error_mapping)
    
    def to_delete_request_information(self,request_configuration: Optional[RequestConfiguration[QueryParameters]] = None) -> RequestInformation:
        """
        Delete an AnalyticalPattern by its root node ID.Only the AP root and its Operator nodes are removed; referenced datanodes (belonging to datasets) are left intact.**Required permission:** ``dg_ds-browse`` on **all** datasets referencedby the AP's ``input`` edges, or realm role ``dg_admin`` /``dg_dataset-curator``.
        param request_configuration: Configuration for the request such as headers, query parameters, and middleware options.
        Returns: RequestInformation
        """
        request_info = RequestInformation(Method.DELETE, '{+baseurl}/api/v1/aps/{id}', self.path_parameters)
        request_info.configure(request_configuration)
        request_info.headers.try_add("Accept", "application/json")
        return request_info
    
    def to_get_request_information(self,request_configuration: Optional[RequestConfiguration[ApsItemRequestBuilderGetQueryParameters]] = None) -> RequestInformation:
        """
        Retrieve an AnalyticalPattern (shallow) by its root node ID.Only the root node, its Operator nodes, and the first-level Data/Usernodes reachable from the operators are returned.  The full datasetsubgraph is **not** recursed into.**Required permission:** ``dg_ds-browse`` on the referenced inputdataset, or realm role ``dg_admin`` / ``dg_dataset-curator``.Returns 404 on permission denial to prevent enumeration.
        param request_configuration: Configuration for the request such as headers, query parameters, and middleware options.
        Returns: RequestInformation
        """
        request_info = RequestInformation(Method.GET, '{+baseurl}/api/v1/aps/{id}{?include_evaluations*}', self.path_parameters)
        request_info.configure(request_configuration)
        request_info.headers.try_add("Accept", "application/json")
        return request_info
    
    def with_url(self,raw_url: str) -> ApsItemRequestBuilder:
        """
        Returns a request builder with the provided arbitrary URL. Using this method means any other path or query parameters are ignored.
        param raw_url: The raw URL to use for the request builder.
        Returns: ApsItemRequestBuilder
        """
        if raw_url is None:
            raise TypeError("raw_url cannot be null.")
        return ApsItemRequestBuilder(self.request_adapter, raw_url)
    
    @property
    def evaluations(self) -> EvaluationsRequestBuilder:
        """
        The evaluations property
        """
        from .evaluations.evaluations_request_builder import EvaluationsRequestBuilder

        return EvaluationsRequestBuilder(self.request_adapter, self.path_parameters)
    
    @dataclass
    class ApsItemRequestBuilderDeleteRequestConfiguration(RequestConfiguration[QueryParameters]):
        """
        Configuration for the request such as headers, query parameters, and middleware options.
        """
        warn("This class is deprecated. Please use the generic RequestConfiguration class generated by the generator.", DeprecationWarning)
    
    @dataclass
    class ApsItemRequestBuilderGetQueryParameters():
        """
        Retrieve an AnalyticalPattern (shallow) by its root node ID.Only the root node, its Operator nodes, and the first-level Data/Usernodes reachable from the operators are returned.  The full datasetsubgraph is **not** recursed into.**Required permission:** ``dg_ds-browse`` on the referenced inputdataset, or realm role ``dg_admin`` / ``dg_dataset-curator``.Returns 404 on permission denial to prevent enumeration.
        """
        # Include evaluations for the returned AnalyticalPattern.
        include_evaluations: Optional[bool] = None

    
    @dataclass
    class ApsItemRequestBuilderGetRequestConfiguration(RequestConfiguration[ApsItemRequestBuilderGetQueryParameters]):
        """
        Configuration for the request such as headers, query parameters, and middleware options.
        """
        warn("This class is deprecated. Please use the generic RequestConfiguration class generated by the generator.", DeprecationWarning)
    

