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
    from ....models.analytical_pattern_input import AnalyticalPatternInput
    from ....models.h_t_t_p_validation_error import HTTPValidationError
    from .post_response import PostResponse

class EmptyPathSegmentRequestBuilder(BaseRequestBuilder):
    """
    Builds and executes requests for operations under /api/v1/aps/
    """
    def __init__(self,request_adapter: RequestAdapter, path_parameters: Union[str, dict[str, Any]]) -> None:
        """
        Instantiates a new EmptyPathSegmentRequestBuilder and sets the default values.
        param path_parameters: The raw url or the url-template parameters for the request.
        param request_adapter: The request adapter to use to execute the requests.
        Returns: None
        """
        super().__init__(request_adapter, "", path_parameters)
    
    async def get(self,request_configuration: Optional[RequestConfiguration[EmptyPathSegmentRequestBuilderGetQueryParameters]] = None) -> Optional[bytes]:
        """
        List all AnalyticalPatterns with optional filtering, pagination and evaluation enrichment.When ``search.q`` is provided, a semantic search is performed and results areordered by relevance.  Pagination (``page``/``pageSize``) applies to both thelist and search paths.Only APs whose ``input`` edges reference datasets the authenticated user can browseare returned.  APs with no ``input`` edges are always included.When authentication is disabled all APs are returned.When ``include_evaluations=true``, Evaluation nodes are included in eachAP's ``nodes`` list (with labels such as ``Evaluation`` + ``SystemEvaluation``).By default they are excluded.
        param request_configuration: Configuration for the request such as headers, query parameters, and middleware options.
        Returns: bytes
        """
        request_info = self.to_get_request_information(
            request_configuration
        )
        from ....models.h_t_t_p_validation_error import HTTPValidationError

        error_mapping: dict[str, type[ParsableFactory]] = {
            "422": HTTPValidationError,
        }
        if not self.request_adapter:
            raise Exception("Http core is null") 
        return await self.request_adapter.send_primitive_async(request_info, "bytes", error_mapping)
    
    async def post(self,body: AnalyticalPatternInput, request_configuration: Optional[RequestConfiguration[QueryParameters]] = None) -> Optional[PostResponse]:
        """
        Create a new AnalyticalPattern in the MoMa graph repository.The ``input`` edges of the AP **must** reference Data nodes that belongto an existing dataset, and the caller must be able to **browse** thosedatasets.  The AP cannot create Dataset nodes itself.
        param body: The request body
        param request_configuration: Configuration for the request such as headers, query parameters, and middleware options.
        Returns: Optional[PostResponse]
        """
        if body is None:
            raise TypeError("body cannot be null.")
        request_info = self.to_post_request_information(
            body, request_configuration
        )
        if not self.request_adapter:
            raise Exception("Http core is null") 
        from .post_response import PostResponse

        return await self.request_adapter.send_async(request_info, PostResponse, None)
    
    def to_get_request_information(self,request_configuration: Optional[RequestConfiguration[EmptyPathSegmentRequestBuilderGetQueryParameters]] = None) -> RequestInformation:
        """
        List all AnalyticalPatterns with optional filtering, pagination and evaluation enrichment.When ``search.q`` is provided, a semantic search is performed and results areordered by relevance.  Pagination (``page``/``pageSize``) applies to both thelist and search paths.Only APs whose ``input`` edges reference datasets the authenticated user can browseare returned.  APs with no ``input`` edges are always included.When authentication is disabled all APs are returned.When ``include_evaluations=true``, Evaluation nodes are included in eachAP's ``nodes`` list (with labels such as ``Evaluation`` + ``SystemEvaluation``).By default they are excluded.
        param request_configuration: Configuration for the request such as headers, query parameters, and middleware options.
        Returns: RequestInformation
        """
        request_info = RequestInformation(Method.GET, '{+baseurl}/api/v1/aps/{?include_evaluations*,page*,pageSize*,search%2Eq*,search%2Ethreshold*,search%2Etop_k*}', self.path_parameters)
        request_info.configure(request_configuration)
        request_info.headers.try_add("Accept", "application/json")
        return request_info
    
    def to_post_request_information(self,body: AnalyticalPatternInput, request_configuration: Optional[RequestConfiguration[QueryParameters]] = None) -> RequestInformation:
        """
        Create a new AnalyticalPattern in the MoMa graph repository.The ``input`` edges of the AP **must** reference Data nodes that belongto an existing dataset, and the caller must be able to **browse** thosedatasets.  The AP cannot create Dataset nodes itself.
        param body: The request body
        param request_configuration: Configuration for the request such as headers, query parameters, and middleware options.
        Returns: RequestInformation
        """
        if body is None:
            raise TypeError("body cannot be null.")
        request_info = RequestInformation(Method.POST, '{+baseurl}/api/v1/aps/', self.path_parameters)
        request_info.configure(request_configuration)
        request_info.headers.try_add("Accept", "application/json")
        request_info.set_content_from_parsable(self.request_adapter, "application/json", body)
        return request_info
    
    def with_url(self,raw_url: str) -> EmptyPathSegmentRequestBuilder:
        """
        Returns a request builder with the provided arbitrary URL. Using this method means any other path or query parameters are ignored.
        param raw_url: The raw URL to use for the request builder.
        Returns: EmptyPathSegmentRequestBuilder
        """
        if raw_url is None:
            raise TypeError("raw_url cannot be null.")
        return EmptyPathSegmentRequestBuilder(self.request_adapter, raw_url)
    
    @dataclass
    class EmptyPathSegmentRequestBuilderGetQueryParameters():
        """
        List all AnalyticalPatterns with optional filtering, pagination and evaluation enrichment.When ``search.q`` is provided, a semantic search is performed and results areordered by relevance.  Pagination (``page``/``pageSize``) applies to both thelist and search paths.Only APs whose ``input`` edges reference datasets the authenticated user can browseare returned.  APs with no ``input`` edges are always included.When authentication is disabled all APs are returned.When ``include_evaluations=true``, Evaluation nodes are included in eachAP's ``nodes`` list (with labels such as ``Evaluation`` + ``SystemEvaluation``).By default they are excluded.
        """
        def get_query_parameter(self,original_name: str) -> str:
            """
            Maps the query parameters names to their encoded names for the URI template parsing.
            param original_name: The original query parameter name in the class.
            Returns: str
            """
            if original_name is None:
                raise TypeError("original_name cannot be null.")
            if original_name == "page_size":
                return "pageSize"
            if original_name == "search_q":
                return "search%2Eq"
            if original_name == "search_threshold":
                return "search%2Ethreshold"
            if original_name == "search_top_k":
                return "search%2Etop_k"
            if original_name == "include_evaluations":
                return "include_evaluations"
            if original_name == "page":
                return "page"
            return original_name
        
        # Include evaluations for each returned AnalyticalPattern.
        include_evaluations: Optional[bool] = None

        # Page number (1-indexed).
        page: Optional[int] = None

        # Number of results per page (1–100).
        page_size: Optional[int] = None

        # Semantic search query. When provided, results are ordered by relevance.
        search_q: Optional[str] = None

        # Minimum similarity score, 0–1 (requires `search.q`).
        search_threshold: Optional[float] = None

        # Maximum number of results returned by semantic search (requires `search.q`).
        search_top_k: Optional[int] = None

    
    @dataclass
    class EmptyPathSegmentRequestBuilderGetRequestConfiguration(RequestConfiguration[EmptyPathSegmentRequestBuilderGetQueryParameters]):
        """
        Configuration for the request such as headers, query parameters, and middleware options.
        """
        warn("This class is deprecated. Please use the generic RequestConfiguration class generated by the generator.", DeprecationWarning)
    
    @dataclass
    class EmptyPathSegmentRequestBuilderPostRequestConfiguration(RequestConfiguration[QueryParameters]):
        """
        Configuration for the request such as headers, query parameters, and middleware options.
        """
        warn("This class is deprecated. Please use the generic RequestConfiguration class generated by the generator.", DeprecationWarning)
    

