from __future__ import annotations
from collections.abc import Callable
from kiota_abstractions.base_request_builder import BaseRequestBuilder
from kiota_abstractions.get_path_parameters import get_path_parameters
from kiota_abstractions.request_adapter import RequestAdapter
from typing import Any, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .compose.compose_request_builder import ComposeRequestBuilder

class AnalyticalPatternsRequestBuilder(BaseRequestBuilder):
    """
    Builds and executes requests for operations under /analytical-patterns
    """
    def __init__(self,request_adapter: RequestAdapter, path_parameters: Union[str, dict[str, Any]]) -> None:
        """
        Instantiates a new AnalyticalPatternsRequestBuilder and sets the default values.
        param path_parameters: The raw url or the url-template parameters for the request.
        param request_adapter: The request adapter to use to execute the requests.
        Returns: None
        """
        super().__init__(request_adapter, "{+baseurl}/analytical-patterns", path_parameters)
    
    @property
    def compose(self) -> ComposeRequestBuilder:
        """
        The compose property
        """
        from .compose.compose_request_builder import ComposeRequestBuilder

        return ComposeRequestBuilder(self.request_adapter, self.path_parameters)
    

