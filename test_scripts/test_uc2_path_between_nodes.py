"""
Test Use Case 2: Paths between 2 Nodes (MTL_VPN_SSL_RANGE & VwLogibecDCR01)
"""
from test_utils import run_use_case_test

USE_CASE_ID = "uc2_path_between_nodes"
USE_CASE_NAME = "Paths: MTL_VPN_SSL_RANGE ↔ VwLogibecDCR01"
DESCRIPTION = "Find paths between the MTL_VPN_SSL_RANGE and the device with id VwLogibecDCR01"

QUESTION = """
Find the shortest path between MTL_VPN_SSL_RANGE and the device VwLogibecDCR01.
Show me all the network hops, including VPN connections, firewalls, and any IPSEC tunnels.
Display the complete connectivity path with all relationship types.
"""

if __name__ == "__main__":
    success = run_use_case_test(
        use_case_id=USE_CASE_ID,
        use_case_name=USE_CASE_NAME,
        question=QUESTION,
        description=DESCRIPTION
    )
    
    exit(0 if success else 1)
