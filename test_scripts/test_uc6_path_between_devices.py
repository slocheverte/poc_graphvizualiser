"""
Test Use Case 6: Path between 2 Devices
"""
from test_utils import run_use_case_test

USE_CASE_ID = "uc6_path_between_devices"
USE_CASE_NAME = "Path Between Two Specific Devices"
DESCRIPTION = "Shortest path between w1clictxxa2301.aepc.com and s1clisgbd60434.aepc.com"

QUESTION = """
Find the shortest path between the devices w1clictxxa2301.aepc.com and s1clisgbd60434.aepc.com.
Show me all the intermediate network devices, firewalls, and connections.
Include all relationship types like membership, source/target relationships, and VPN tunnels.
"""

if __name__ == "__main__":
    success = run_use_case_test(
        use_case_id=USE_CASE_ID,
        use_case_name=USE_CASE_NAME,
        question=QUESTION,
        description=DESCRIPTION
    )
    
    exit(0 if success else 1)
