from __future__ import annotations
from collections.abc import Callable
from kiota_abstractions.base_request_builder import BaseRequestBuilder
from kiota_abstractions.get_path_parameters import get_path_parameters
from kiota_abstractions.request_adapter import RequestAdapter
from typing import Any, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .convert.convert_request_builder import ConvertRequestBuilder
    from .croissant.croissant_request_builder import CroissantRequestBuilder
    from .empty_path_segment_request_builder import EmptyPathSegmentRequestBuilder
    from .item.datasets_item_request_builder import DatasetsItemRequestBuilder
    from .validate.validate_request_builder import ValidateRequestBuilder

class DatasetsRequestBuilder(BaseRequestBuilder):
    """
    Builds and executes requests for operations under /api/v1/datasets
    """
    def __init__(self,request_adapter: RequestAdapter, path_parameters: Union[str, dict[str, Any]]) -> None:
        """
        Instantiates a new DatasetsRequestBuilder and sets the default values.
        param path_parameters: The raw url or the url-template parameters for the request.
        param request_adapter: The request adapter to use to execute the requests.
        Returns: None
        """
        super().__init__(request_adapter, "{+baseurl}/api/v1/datasets", path_parameters)
    
    def by_id(self,id: str) -> DatasetsItemRequestBuilder:
        """
        Gets an item from the ApiSdk.api.v1.datasets.item collection
        param id: Unique identifier of the item
        Returns: DatasetsItemRequestBuilder
        """
        if id is None:
            raise TypeError("id cannot be null.")
        from .item.datasets_item_request_builder import DatasetsItemRequestBuilder

        url_tpl_params = get_path_parameters(self.path_parameters)
        url_tpl_params["id"] = id
        return DatasetsItemRequestBuilder(self.request_adapter, url_tpl_params)
    
    @property
    def convert(self) -> ConvertRequestBuilder:
        """
        The convert property
        """
        from .convert.convert_request_builder import ConvertRequestBuilder

        return ConvertRequestBuilder(self.request_adapter, self.path_parameters)
    
    @property
    def croissant(self) -> CroissantRequestBuilder:
        """
        The croissant property
        """
        from .croissant.croissant_request_builder import CroissantRequestBuilder

        return CroissantRequestBuilder(self.request_adapter, self.path_parameters)
    
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
    

