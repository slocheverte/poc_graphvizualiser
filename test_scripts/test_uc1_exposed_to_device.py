"""
Test Use Case 1: Exposed Device that can reach a specific Device
"""
from test_utils import run_use_case_test

USE_CASE_ID = "uc1_exposed_to_device"
USE_CASE_NAME = "Exposed Device to Specific Device"
DESCRIPTION = "Find every Internet Exposed Device that has a reachable path to the device whose id is VwLogibecDCR01"

QUESTION = """
Find all Internet-exposed devices that can reach the device VwLogibecDCR01.
Show me the complete path from Internet exposure through VIPs and mapped devices to the target device.
Include all intermediate devices and their relationships.
"""

if __name__ == "__main__":
    success = run_use_case_test(
        use_case_id=USE_CASE_ID,
        use_case_name=USE_CASE_NAME,
        question=QUESTION,
        description=DESCRIPTION
    )
    
    exit(0 if success else 1)
