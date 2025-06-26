"""
Enterprise Integration Module for Workflows

This module provides integration capabilities for connecting workflows
with enterprise systems like ERP, CRM, and external APIs.
"""

import logging
import requests
from typing import Dict, Any, Optional, Callable
import json
from abc import ABC, abstractmethod

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class IntegrationAdapter(ABC):
    """Abstract base class for integration adapters to enterprise systems."""
    def __init__(self, config: Dict[str, Any]):
        """Initialize the integration adapter with configuration.

        Args:
            config (Dict[str, Any]): Configuration dictionary for the adapter.
        """
        self.config = config
        self.is_connected = False

    @abstractmethod
    def connect(self) -> bool:
        """Establish connection to the enterprise system.

        Returns:
            bool: True if connection is successful, False otherwise.
        """
        pass

    @abstractmethod
    def disconnect(self) -> None:
        """Disconnect from the enterprise system."""
        pass

    @abstractmethod
    def send_data(self, data: Dict[str, Any], endpoint: Optional[str] = None) -> Dict[str, Any]:
        """Send data to the enterprise system.

        Args:
            data (Dict[str, Any]): Data payload to send.
            endpoint (Optional[str]): Specific endpoint to send data to, if applicable.

        Returns:
            Dict[str, Any]: Response from the system.
        """
        pass

    @abstractmethod
    def receive_data(self, query: Optional[str] = None, endpoint: Optional[str] = None) -> Dict[str, Any]:
        """Receive or fetch data from the enterprise system.

        Args:
            query (Optional[str]): Query string or identifier for specific data.
            endpoint (Optional[str]): Specific endpoint to fetch data from, if applicable.

        Returns:
            Dict[str, Any]: Data received from the system.
        """
        pass

class RESTApiAdapter(IntegrationAdapter):
    """Adapter for integrating with RESTful APIs."""
    def __init__(self, config: Dict[str, Any]):
        """Initialize the REST API adapter.

        Args:
            config (Dict[str, Any]): Configuration including base_url, api_key, etc.
        """
        super().__init__(config)
        self.base_url = config.get('base_url', '')
        self.api_key = config.get('api_key', '')
        self.headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.api_key}' if self.api_key else ''
        }
        self.session = requests.Session()

    def connect(self) -> bool:
        """Establish connection to the REST API by testing with a simple request.

        Returns:
            bool: True if connection test is successful, False otherwise.
        """
        try:
            response = self.session.get(f"{self.base_url}/health", headers=self.headers, timeout=5)
            if response.status_code == 200:
                self.is_connected = True
                logger.info(f"Connected to REST API at {self.base_url}")
                return True
            else:
                logger.error(f"Failed to connect to REST API at {self.base_url}: Status {response.status_code}")
                return False
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to connect to REST API at {self.base_url}: {str(e)}")
            return False

    def disconnect(self) -> None:
        """Disconnect from the REST API by closing the session."""
        self.session.close()
        self.is_connected = False
        logger.info(f"Disconnected from REST API at {self.base_url}")

    def send_data(self, data: Dict[str, Any], endpoint: Optional[str] = None) -> Dict[str, Any]:
        """Send data to the REST API.

        Args:
            data (Dict[str, Any]): Data payload to send.
            endpoint (Optional[str]): Specific endpoint to send data to.

        Returns:
            Dict[str, Any]: Response from the API.
        """
        if not self.is_connected and not self.connect():
            raise ConnectionError(f"Not connected to REST API at {self.base_url}")

        target_url = f"{self.base_url}/{endpoint}" if endpoint else self.base_url
        try:
            response = self.session.post(target_url, json=data, headers=self.headers, timeout=10)
            response.raise_for_status()
            logger.info(f"Data sent to {target_url} successfully")
            return response.json() if response.text else {}
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to send data to {target_url}: {str(e)}")
            raise

    def receive_data(self, query: Optional[str] = None, endpoint: Optional[str] = None) -> Dict[str, Any]:
        """Fetch data from the REST API.

        Args:
            query (Optional[str]): Query string or identifier for specific data.
            endpoint (Optional[str]): Specific endpoint to fetch data from.

        Returns:
            Dict[str, Any]: Data received from the API.
        """
        if not self.is_connected and not self.connect():
            raise ConnectionError(f"Not connected to REST API at {self.base_url}")

        target_url = f"{self.base_url}/{endpoint}" if endpoint else self.base_url
        if query:
            target_url = f"{target_url}?{query}" if '?' not in target_url else f"{target_url}&{query}"
        try:
            response = self.session.get(target_url, headers=self.headers, timeout=10)
            response.raise_for_status()
            logger.info(f"Data received from {target_url} successfully")
            return response.json() if response.text else {}
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to receive data from {target_url}: {str(e)}")
            raise

class WorkflowIntegrator:
    """Manages integration of workflows with external enterprise systems."""
    def __init__(self):
        """Initialize the Workflow Integrator."""
        self.adapters: Dict[str, IntegrationAdapter] = {}
        logger.info("Workflow Integrator initialized")

    def register_adapter(self, system_id: str, adapter: IntegrationAdapter) -> None:
        """Register an integration adapter for a specific system.

        Args:
            system_id (str): Unique identifier for the enterprise system.
            adapter (IntegrationAdapter): Adapter instance for connecting to the system.
        """
        self.adapters[system_id] = adapter
        logger.info(f"Registered integration adapter for system {system_id}")

    def connect_to_system(self, system_id: str) -> bool:
        """Connect to a specific enterprise system using its adapter.

        Args:
            system_id (str): Identifier of the system to connect to.

        Returns:
            bool: True if connection is successful, False otherwise.
        """
        if system_id not in self.adapters:
            logger.error(f"No adapter registered for system {system_id}")
            return False

        return self.adapters[system_id].connect()

    def disconnect_from_system(self, system_id: str) -> None:
        """Disconnect from a specific enterprise system.

        Args:
            system_id (str): Identifier of the system to disconnect from.
        """
        if system_id in self.adapters:
            self.adapters[system_id].disconnect()
            logger.info(f"Disconnected from system {system_id}")
        else:
            logger.warning(f"No adapter found for system {system_id} to disconnect")

    def send_to_system(self, system_id: str, data: Dict[str, Any], endpoint: Optional[str] = None) -> Dict[str, Any]:
        """Send data to a specific enterprise system.

        Args:
            system_id (str): Identifier of the target system.
            data (Dict[str, Any]): Data payload to send.
            endpoint (Optional[str]): Specific endpoint in the system.

        Returns:
            Dict[str, Any]: Response from the system.
        """
        if system_id not in self.adapters:
            raise ValueError(f"No adapter registered for system {system_id}")

        return self.adapters[system_id].send_data(data, endpoint)

    def receive_from_system(self, system_id: str, query: Optional[str] = None, endpoint: Optional[str] = None) -> Dict[str, Any]:
        """Receive or fetch data from a specific enterprise system.

        Args:
            system_id (str): Identifier of the source system.
            query (Optional[str]): Query string or identifier for specific data.
            endpoint (Optional[str]): Specific endpoint in the system.

        Returns:
            Dict[str, Any]: Data received from the system.
        """
        if system_id not in self.adapters:
            raise ValueError(f"No adapter registered for system {system_id}")

        return self.adapters[system_id].receive_data(query, endpoint)

    def execute_workflow_with_integration(self, workflow_engine, workflow_id: str, initial_state: Dict[str, Any], integrations: Dict[str, Dict[str, Any]]) -> None:
        """Execute a workflow with integrated actions to external systems.

        Args:
            workflow_engine: Workflow engine instance to execute the workflow.
            workflow_id (str): Unique identifier for the workflow.
            initial_state (Dict[str, Any]): Initial state for the workflow.
            integrations (Dict[str, Dict[str, Any]]): Mapping of action names to integration details.
        """
        workflow_engine.start_workflow(workflow_id, initial_state)
        logger.info(f"Starting workflow {workflow_id} with integrations")

        for action_name, integration_info in integrations.items():
            system_id = integration_info.get('system_id')
            action_type = integration_info.get('action_type', 'send')
            endpoint = integration_info.get('endpoint')
            data_func = integration_info.get('data_func')

            try:
                if action_type == 'send':
                    data = data_func() if callable(data_func) else data_func
                    response = self.send_to_system(system_id, data, endpoint)
                    workflow_engine.execute_action(lambda: response, action_name)
                    logger.info(f"Integrated send action {action_name} to system {system_id} in workflow {workflow_id}")
                else:  # receive
                    response = self.receive_from_system(system_id, endpoint=endpoint)
                    workflow_engine.execute_action(lambda: response, action_name)
                    logger.info(f"Integrated receive action {action_name} from system {system_id} in workflow {workflow_id}")
            except Exception as e:
                logger.error(f"Integration action {action_name} failed for system {system_id}: {str(e)}")
                raise

        workflow_engine.complete_workflow()
        logger.info(f"Completed workflow {workflow_id} with integrations")
