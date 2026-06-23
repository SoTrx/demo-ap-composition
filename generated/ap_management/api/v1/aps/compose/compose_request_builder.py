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
    from .....models.analytical_pattern import AnalyticalPattern
    from .....models.compose_payload import ComposePayload
    from .....models.error_response import ErrorResponse
    from .....models.h_t_t_p_validation_error import HTTPValidationError

class ComposeRequestBuilder(BaseRequestBuilder):
    """
    Builds and executes requests for operations under /api/v1/aps/compose
    """
    def __init__(self,request_adapter: RequestAdapter, path_parameters: Union[str, dict[str, Any]]) -> None:
        """
        Instantiates a new ComposeRequestBuilder and sets the default values.
        param path_parameters: The raw url or the url-template parameters for the request.
        param request_adapter: The request adapter to use to execute the requests.
        Returns: None
        """
        super().__init__(request_adapter, "{+baseurl}/api/v1/aps/compose", path_parameters)
    
    async def post(self,body: ComposePayload, request_configuration: Optional[RequestConfiguration[QueryParameters]] = None) -> Optional[AnalyticalPattern]:
        """
        Create a new AnalyticalPattern in the MoMa graph repository.d    The ``input`` edges of the AP **must** reference Data nodes that belong    to an existing dataset, and the caller must be able to **browse** those    datasets.  The AP cannot create Dataset nodes itself.
        param body: The request body
        param request_configuration: Configuration for the request such as headers, query parameters, and middleware options.
        Returns: Optional[AnalyticalPattern]
        """
        if body is None:
            raise TypeError("body cannot be null.")
        request_info = self.to_post_request_information(
            body, request_configuration
        )
        from .....models.error_response import ErrorResponse
        from .....models.h_t_t_p_validation_error import HTTPValidationError

        error_mapping: dict[str, type[ParsableFactory]] = {
            "400": ErrorResponse,
            "422": HTTPValidationError,
            "500": ErrorResponse,
        }
        if not self.request_adapter:
            raise Exception("Http core is null") 
        from .....models.analytical_pattern import AnalyticalPattern

        return await self.request_adapter.send_async(request_info, AnalyticalPattern, error_mapping)
    
    def to_post_request_information(self,body: ComposePayload, request_configuration: Optional[RequestConfiguration[QueryParameters]] = None) -> RequestInformation:
        """
        Create a new AnalyticalPattern in the MoMa graph repository.d    The ``input`` edges of the AP **must** reference Data nodes that belong    to an existing dataset, and the caller must be able to **browse** those    datasets.  The AP cannot create Dataset nodes itself.
        param body: The request body
        param request_configuration: Configuration for the request such as headers, query parameters, and middleware options.
        Returns: RequestInformation
        """
        if body is None:
            raise TypeError("body cannot be null.")
        request_info = RequestInformation(Method.POST, self.url_template, self.path_parameters)
        request_info.configure(request_configuration)
        request_info.headers.try_add("Accept", "application/json")
        request_info.set_content_from_parsable(self.request_adapter, "application/json", body)
        return request_info
    
    def with_url(self,raw_url: str) -> ComposeRequestBuilder:
        """
        Returns a request builder with the provided arbitrary URL. Using this method means any other path or query parameters are ignored.
        param raw_url: The raw URL to use for the request builder.
        Returns: ComposeRequestBuilder
        """
        if raw_url is None:
            raise TypeError("raw_url cannot be null.")
        return ComposeRequestBuilder(self.request_adapter, raw_url)
    
    @dataclass
    class ComposeRequestBuilderPostRequestConfiguration(RequestConfiguration[QueryParameters]):
        """
        Configuration for the request such as headers, query parameters, and middleware options.
        """
        warn("This class is deprecated. Please use the generic RequestConfiguration class generated by the generator.", DeprecationWarning)
    

