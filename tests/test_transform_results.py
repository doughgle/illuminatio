#!/usr/bin/env python3
"""
Tests for the transform_results function in illuminatio.py
"""
import json
import logging
import pytest

from illuminatio.illuminatio import transform_results

# Configure logging
LOGGER = logging.getLogger(__name__)


class TestTransformResults:
    """Test suite for the transform_results function in illuminatio.py"""

    def test_transform_results_with_missing_receiver(self):
        """
        Test the transform_results function with a missing receiver pod in the raw_results.
        This test verifies that the function handles the case where a mapped_receiver_pod
        is not found in raw_results[mapped_sender_pod].
        """
        # Sample data that reproduces the issue
        raw_results = {
            "default:apiserver-774f4d67fc-vpvd5": {
                "10.108.171.237": {
                    "56427": {
                        "nmap-state": "open",
                        "string": "Test succeeded",
                        "success": True
                    }
                }
            }
        }
        
        sender_pod_mappings = {
            "default:app=bookstore": "default:apiserver-774f4d67fc-vpvd5"
        }
        
        receiver_pod_mappings = {
            "default:app=bookstore": {
                "default:app=bookstore,role=api": "10.104.245.132"  # This doesn't exist in raw_results
            }
        }
        
        port_mappings = {
            "default:app=bookstore": {
                "default:app=bookstore,role=api": {
                    "*": "80"
                }
            }
        }
        
        # This would fail before the fix
        transformed = transform_results(raw_results, sender_pod_mappings, receiver_pod_mappings, port_mappings)
        
        # Verify the function doesn't crash and returns a properly formed dictionary
        assert isinstance(transformed, dict)
        assert "default:app=bookstore" in transformed
        
        # The receiver pod should have an empty dictionary due to the missing mapping
        assert "default:app=bookstore,role=api" in transformed["default:app=bookstore"]
        assert transformed["default:app=bookstore"]["default:app=bookstore,role=api"] == {}
        
        LOGGER.debug("Test passed! The function now handles missing receiver pods correctly.")

    def test_transform_results_normal_case(self):
        """
        Test the transform_results function with a normal case where all mappings exist.
        """
        # Sample data for a normal case
        raw_results = {
            "default:sender-pod-123": {
                "10.108.171.237": {
                    "80": {
                        "nmap-state": "open",
                        "string": "Test succeeded",
                        "success": True
                    }
                }
            }
        }
        
        sender_pod_mappings = {
            "default:app=frontend": "default:sender-pod-123"
        }
        
        receiver_pod_mappings = {
            "default:app=frontend": {
                "default:app=backend": "10.108.171.237"
            }
        }
        
        port_mappings = {
            "default:app=frontend": {
                "default:app=backend": {
                    "8080": "80"
                }
            }
        }
        
        transformed = transform_results(raw_results, sender_pod_mappings, receiver_pod_mappings, port_mappings)
        
        # Verify the transformation worked correctly
        assert isinstance(transformed, dict)
        assert "default:app=frontend" in transformed
        assert "default:app=backend" in transformed["default:app=frontend"]
        assert "8080" in transformed["default:app=frontend"]["default:app=backend"]
        assert transformed["default:app=frontend"]["default:app=backend"]["8080"] == {
            "nmap-state": "open",
            "string": "Test succeeded",
            "success": True
        }
