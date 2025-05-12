import pytest
import kubernetes as k8s
from unittest.mock import patch, MagicMock
from illuminatio.illuminatio_runner import get_docker_network_namespace


class TestKubernetesClientCompatibility:
    """
    Test case to verify and reproduce Kubernetes client compatibility issues
    with the 'exact' and 'export' parameters in recent Kubernetes client versions.
    """

    def test_read_namespaced_pod_with_exact_param_fails(self):
        """
        Test that directly reproduces the error:
        kubernetes.client.exceptions.ApiTypeError: Got an unexpected keyword argument 'exact'
        
        This test specifically shows how the call to read_namespaced_pod fails
        when using parameters removed in k8s client >=28.1.0.
        """
        # Create K8s client instance
        api = k8s.client.CoreV1Api()
        
        # Call the API method with the 'exact' parameter (which is not supported in newer versions)
        with pytest.raises(k8s.client.exceptions.ApiTypeError) as excinfo:
            api.read_namespaced_pod(
                name="test-pod", 
                namespace="default",
                pretty="true",
                exact=False,  # This parameter was removed in k8s client >=28.1.0
                export=False  # This parameter was removed in k8s client >=28.1.0
            )
        
        # Verify the error message mentions 'exact'
        assert "unexpected keyword argument 'exact'" in str(excinfo.value)
        

if __name__ == "__main__":
    # This allows running this test file directly
    pytest.main(["-v", __file__])
