"""
Test Use Case 3: VPN_SSL_RANGE to Critical Devices
"""
from test_utils import run_use_case_test

USE_CASE_ID = "uc3_vpn_to_critical"
USE_CASE_NAME = "VPN SSL Range → Critical Devices"
DESCRIPTION = "Return network paths that originate at all VPN SSL RANGE and lead to nodes classified as Critical"

QUESTION = """
Find all VPN SSL ranges that can reach critical devices (criticality level 2.0).
Show me the network paths from VPN SSL ranges to critical infrastructure.
Include all devices with criticality level 2.0 and their categories.
Limit to 50 paths.
"""

if __name__ == "__main__":
    success = run_use_case_test(
        use_case_id=USE_CASE_ID,
        use_case_name=USE_CASE_NAME,
        question=QUESTION,
        description=DESCRIPTION
    )
    
    exit(0 if success else 1)
