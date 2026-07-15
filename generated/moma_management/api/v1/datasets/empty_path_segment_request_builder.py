from __future__ import annotations
import datetime
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
    from ....models.dataset_input import DatasetInput
    from ....models.dataset_property import DatasetProperty
    from ....models.dataset_sort_field import DatasetSortField
    from ....models.h_t_t_p_validation_error import HTTPValidationError
    from ....models.mime_type import MimeType
    from ....models.node_label import NodeLabel
    from ....models.sort_direction import SortDirection
    from ....models.status import Status
    from .get_response import GetResponse

class EmptyPathSegmentRequestBuilder(BaseRequestBuilder):
    """
    Builds and executes requests for operations under /api/v1/datasets/
    """
    def __init__(self,request_adapter: RequestAdapter, path_parameters: Union[str, dict[str, Any]]) -> None:
        """
        Instantiates a new EmptyPathSegmentRequestBuilder and sets the default values.
        param path_parameters: The raw url or the url-template parameters for the request.
        param request_adapter: The request adapter to use to execute the requests.
        Returns: None
        """
        super().__init__(request_adapter, "{+baseurl}/api/v1/datasets/{?direction*,mimeTypes*,nodeIds*,orderBy*,page*,pageSize*,properties*,publishedFrom*,publishedTo*,status*,types*}", path_parameters)
    
    async def get(self,request_configuration: Optional[RequestConfiguration[EmptyPathSegmentRequestBuilderGetQueryParameters]] = None) -> Optional[GetResponse]:
        """
        List datasets with optional filtering, sorting, and pagination criteria.Only datasets the authenticated user holds the `dg_ds-browse` grant for are returned.Realm roles `dg_admin` and `dg_dataset-curator` bypass individual datasetgrants and allow browsing all datasets. When authentication is disabled, all datasetsare returned regardless of grants.
        param request_configuration: Configuration for the request such as headers, query parameters, and middleware options.
        Returns: Optional[GetResponse]
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
        from .get_response import GetResponse

        return await self.request_adapter.send_async(request_info, GetResponse, error_mapping)
    
    async def post(self,body: DatasetInput, request_configuration: Optional[RequestConfiguration[QueryParameters]] = None) -> Optional[bytes]:
        """
        Create a new dataset in the MoMa graph repository.**Required permission:** realm role `dg_admin` or `dg_dataset-uploader`.
        param body: The request body
        param request_configuration: Configuration for the request such as headers, query parameters, and middleware options.
        Returns: bytes
        """
        if body is None:
            raise TypeError("body cannot be null.")
        request_info = self.to_post_request_information(
            body, request_configuration
        )
        from ....models.h_t_t_p_validation_error import HTTPValidationError

        error_mapping: dict[str, type[ParsableFactory]] = {
            "422": HTTPValidationError,
        }
        if not self.request_adapter:
            raise Exception("Http core is null") 
        return await self.request_adapter.send_primitive_async(request_info, "bytes", error_mapping)
    
    def to_get_request_information(self,request_configuration: Optional[RequestConfiguration[EmptyPathSegmentRequestBuilderGetQueryParameters]] = None) -> RequestInformation:
        """
        List datasets with optional filtering, sorting, and pagination criteria.Only datasets the authenticated user holds the `dg_ds-browse` grant for are returned.Realm roles `dg_admin` and `dg_dataset-curator` bypass individual datasetgrants and allow browsing all datasets. When authentication is disabled, all datasetsare returned regardless of grants.
        param request_configuration: Configuration for the request such as headers, query parameters, and middleware options.
        Returns: RequestInformation
        """
        request_info = RequestInformation(Method.GET, self.url_template, self.path_parameters)
        request_info.configure(request_configuration)
        request_info.headers.try_add("Accept", "application/json")
        return request_info
    
    def to_post_request_information(self,body: DatasetInput, request_configuration: Optional[RequestConfiguration[QueryParameters]] = None) -> RequestInformation:
        """
        Create a new dataset in the MoMa graph repository.**Required permission:** realm role `dg_admin` or `dg_dataset-uploader`.
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
        List datasets with optional filtering, sorting, and pagination criteria.Only datasets the authenticated user holds the `dg_ds-browse` grant for are returned.Realm roles `dg_admin` and `dg_dataset-curator` bypass individual datasetgrants and allow browsing all datasets. When authentication is disabled, all datasetsare returned regardless of grants.
        """
        def get_query_parameter(self,original_name: str) -> str:
            """
            Maps the query parameters names to their encoded names for the URI template parsing.
            param original_name: The original query parameter name in the class.
            Returns: str
            """
            if original_name is None:
                raise TypeError("original_name cannot be null.")
            if original_name == "mime_types":
                return "mimeTypes"
            if original_name == "node_ids":
                return "nodeIds"
            if original_name == "order_by":
                return "orderBy"
            if original_name == "page_size":
                return "pageSize"
            if original_name == "published_from":
                return "publishedFrom"
            if original_name == "published_to":
                return "publishedTo"
            if original_name == "direction":
                return "direction"
            if original_name == "page":
                return "page"
            if original_name == "properties":
                return "properties"
            if original_name == "status":
                return "status"
            if original_name == "types":
                return "types"
            return original_name
        
        # Sort direction applied to all `orderBy` fields.
        direction: Optional[SortDirection] = None

        # Filter datasets by the MIME types of their file objects.
        mime_types: list[MimeType] = field(default_factory=list)

        # Filter results to only datasets whose subgraph contains nodes with these IDs.
        node_ids: Optional[list[str]] = None

        # One or more dataset properties to sort results by. Applied left-to-right.
        order_by: list[DatasetSortField] = field(default_factory=list)

        # Page number (1-indexed).
        page: Optional[int] = None

        # Number of results per page (1–100).
        page_size: Optional[int] = None

        # Dataset root-node properties to include in each result item. Returns all properties if empty.
        properties: list[DatasetProperty] = field(default_factory=list)

        # Inclusive lower bound on `datePublished` (ISO 8601 date, e.g. `2024-01-01`).
        published_from: Optional[datetime.date] = None

        # Inclusive upper bound on `datePublished` (ISO 8601 date, e.g. `2024-12-31`).
        published_to: Optional[datetime.date] = None

        # Filter datasets by publication status.
        status: Optional[Status] = None

        # Filter datasets by the label types of their connected file nodes.
        types: list[NodeLabel] = field(default_factory=list)

    
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
    

