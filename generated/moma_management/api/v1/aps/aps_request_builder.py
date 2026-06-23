from __future__ import annotations
from collections.abc import Callable
from kiota_abstractions.base_request_builder import BaseRequestBuilder
from kiota_abstractions.get_path_parameters import get_path_parameters
from kiota_abstractions.request_adapter import RequestAdapter
from typing import Any, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .empty_path_segment_request_builder import EmptyPathSegmentRequestBuilder
    from .item.aps_item_request_builder import ApsItemRequestBuilder
    from .validate.validate_request_builder import ValidateRequestBuilder

class ApsRequestBuilder(BaseRequestBuilder):
    """
    Builds and executes requests for operations under /api/v1/aps
    """
    def __init__(self,request_adapter: RequestAdapter, path_parameters: Union[str, dict[str, Any]]) -> None:
        """
        Instantiates a new ApsRequestBuilder and sets the default values.
        param path_parameters: The raw url or the url-template parameters for the request.
        param request_adapter: The request adapter to use to execute the requests.
        Returns: None
        """
        super().__init__(request_adapter, "{+baseurl}/api/v1/aps", path_parameters)
    
    def by_id(self,id: str) -> ApsItemRequestBuilder:
        """
        Gets an item from the ApiSdk.api.v1.aps.item collection
        param id: Unique identifier of the item
        Returns: ApsItemRequestBuilder
        """
        if id is None:
            raise TypeError("id cannot be null.")
        from .item.aps_item_request_builder import ApsItemRequestBuilder

        url_tpl_params = get_path_parameters(self.path_parameters)
        url_tpl_params["id"] = id
        return ApsItemRequestBuilder(self.request_adapter, url_tpl_params)
    
    @property
    def empty_path_segment(self) -> EmptyPathSegmentRequestBuilder:
        """
        The EmptyPathSegment property
        """
        from .empty_path_segment_request_builder import EmptyPathSegmentRequestBuilder

        return EmptyPathSegmentRequestBuilder(self.request_adapter, self.path_parameters)
    
    @property
    def validate(self) -> ValidateRequestBuilder:
        """
        The validate property
        """
        from .validate.validate_request_builder import ValidateRequestBuilder

        return ValidateRequestBuilder(self.request_adapter, self.path_parameters)
    

