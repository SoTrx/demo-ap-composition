from __future__ import annotations
from collections.abc import Callable
from kiota_abstractions.base_request_builder import BaseRequestBuilder
from kiota_abstractions.get_path_parameters import get_path_parameters
from kiota_abstractions.request_adapter import RequestAdapter
from typing import Any, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .aps.aps_request_builder import ApsRequestBuilder
    from .datasets.datasets_request_builder import DatasetsRequestBuilder
    from .health.health_request_builder import HealthRequestBuilder
    from .ml_models.ml_models_request_builder import MlModelsRequestBuilder
    from .nodes.nodes_request_builder import NodesRequestBuilder
    from .tasks.tasks_request_builder import TasksRequestBuilder

class V1RequestBuilder(BaseRequestBuilder):
    """
    Builds and executes requests for operations under /api/v1
    """
    def __init__(self,request_adapter: RequestAdapter, path_parameters: Union[str, dict[str, Any]]) -> None:
        """
        Instantiates a new V1RequestBuilder and sets the default values.
        param path_parameters: The raw url or the url-template parameters for the request.
        param request_adapter: The request adapter to use to execute the requests.
        Returns: None
        """
        super().__init__(request_adapter, "{+baseurl}/api/v1", path_parameters)
    
    @property
    def aps(self) -> ApsRequestBuilder:
        """
        The aps property
        """
        from .aps.aps_request_builder import ApsRequestBuilder

        return ApsRequestBuilder(self.request_adapter, self.path_parameters)
    
    @property
    def datasets(self) -> DatasetsRequestBuilder:
        """
        The datasets property
        """
        from .datasets.datasets_request_builder import DatasetsRequestBuilder

        return DatasetsRequestBuilder(self.request_adapter, self.path_parameters)
    
    @property
    def health(self) -> HealthRequestBuilder:
        """
        The health property
        """
        from .health.health_request_builder import HealthRequestBuilder

        return HealthRequestBuilder(self.request_adapter, self.path_parameters)
    
    @property
    def ml_models(self) -> MlModelsRequestBuilder:
        """
        The mlModels property
        """
        from .ml_models.ml_models_request_builder import MlModelsRequestBuilder

        return MlModelsRequestBuilder(self.request_adapter, self.path_parameters)
    
    @property
    def nodes(self) -> NodesRequestBuilder:
        """
        The nodes property
        """
        from .nodes.nodes_request_builder import NodesRequestBuilder

        return NodesRequestBuilder(self.request_adapter, self.path_parameters)
    
    @property
    def tasks(self) -> TasksRequestBuilder:
        """
        The tasks property
        """
        from .tasks.tasks_request_builder import TasksRequestBuilder

        return TasksRequestBuilder(self.request_adapter, self.path_parameters)
    

