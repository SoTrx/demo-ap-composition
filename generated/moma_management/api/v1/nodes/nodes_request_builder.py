from __future__ import annotations
from collections.abc import Callable
from kiota_abstractions.base_request_builder import BaseRequestBuilder
from kiota_abstractions.get_path_parameters import get_path_parameters
from kiota_abstractions.request_adapter import RequestAdapter
from typing import Any, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .item.nodes_item_request_builder import NodesItemRequestBuilder

class NodesRequestBuilder(BaseRequestBuilder):
    """
    Builds and executes requests for operations under /api/v1/nodes
    """
    def __init__(self,request_adapter: RequestAdapter, path_parameters: Union[str, dict[str, Any]]) -> None:
        """
        Instantiates a new NodesRequestBuilder and sets the default values.
        param path_parameters: The raw url or the url-template parameters for the request.
        param request_adapter: The request adapter to use to execute the requests.
        Returns: None
        """
        super().__init__(request_adapter, "{+baseurl}/api/v1/nodes", path_parameters)
    
    def by_id(self,id: str) -> NodesItemRequestBuilder:
        """
        Gets an item from the ApiSdk.api.v1.nodes.item collection
        param id: Unique identifier of the item
        Returns: NodesItemRequestBuilder
        """
        if id is None:
            raise TypeError("id cannot be null.")
        from .item.nodes_item_request_builder import NodesItemRequestBuilder

        url_tpl_params = get_path_parameters(self.path_parameters)
        url_tpl_params["id"] = id
        return NodesItemRequestBuilder(self.request_adapter, url_tpl_params)
    

