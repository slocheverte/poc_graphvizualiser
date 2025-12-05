"""
Test Use Case 4: SSL VPN ranges with broad reach
"""
from test_utils import run_use_case_test

USE_CASE_ID = "uc4_ssl_vpn_broad_reach"
USE_CASE_NAME = "SSL VPN Ranges with Broad Reach"
DESCRIPTION = "SSL pools that can reach many targets (potential lateral-movement risk)"

QUESTION = """
Find all SSL VPN ranges that have broad reach across the network.
Identify SSL VPN pools that can reach many different targets.
Show me the number of reachable targets for each SSL range and the types of targets.
This helps identify potential lateral movement risks.
Order by reach count descending.
"""

if __name__ == "__main__":
    success = run_use_case_test(
        use_case_id=USE_CASE_ID,
        use_case_name=USE_CASE_NAME,
        question=QUESTION,
        description=DESCRIPTION
    )
    
    exit(0 if success else 1)
