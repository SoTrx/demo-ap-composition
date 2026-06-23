from __future__ import annotations
from collections.abc import Callable
from kiota_abstractions.base_request_builder import BaseRequestBuilder
from kiota_abstractions.get_path_parameters import get_path_parameters
from kiota_abstractions.request_adapter import RequestAdapter
from typing import Any, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .empty_path_segment_request_builder import EmptyPathSegmentRequestBuilder
    from .item.ml_models_item_request_builder import MlModelsItemRequestBuilder

class MlModelsRequestBuilder(BaseRequestBuilder):
    """
    Builds and executes requests for operations under /api/v1/ml-models
    """
    def __init__(self,request_adapter: RequestAdapter, path_parameters: Union[str, dict[str, Any]]) -> None:
        """
        Instantiates a new MlModelsRequestBuilder and sets the default values.
        param path_parameters: The raw url or the url-template parameters for the request.
        param request_adapter: The request adapter to use to execute the requests.
        Returns: None
        """
        super().__init__(request_adapter, "{+baseurl}/api/v1/ml-models", path_parameters)
    
    def by_id(self,id: str) -> MlModelsItemRequestBuilder:
        """
        Gets an item from the ApiSdk.api.v1.mlModels.item collection
        param id: Unique identifier of the item
        Returns: MlModelsItemRequestBuilder
        """
        if id is None:
            raise TypeError("id cannot be null.")
        from .item.ml_models_item_request_builder import MlModelsItemRequestBuilder

        url_tpl_params = get_path_parameters(self.path_parameters)
        url_tpl_params["id"] = id
        return MlModelsItemRequestBuilder(self.request_adapter, url_tpl_params)
    
    @property
    def empty_path_segment(self) -> EmptyPathSegmentRequestBuilder:
        """
        The EmptyPathSegment property
        """
        from .empty_path_segment_request_builder import EmptyPathSegmentRequestBuilder

        return EmptyPathSegmentRequestBuilder(self.request_adapter, self.path_parameters)
    

