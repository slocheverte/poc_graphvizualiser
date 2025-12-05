"""
Test Use Case 5: Top N subnets with the most devices
"""
from test_utils import run_use_case_test

USE_CASE_ID = "uc5_top_subnets"
USE_CASE_NAME = "Top Subnets by Device Count"
DESCRIPTION = "Top 10 subnets ordered by device count"

QUESTION = """
Show me the top 10 subnets with the most devices.
For each subnet, show the device count and subnet details.
Order by device count in descending order.
This helps identify the most populated network segments.
"""

if __name__ == "__main__":
    success = run_use_case_test(
        use_case_id=USE_CASE_ID,
        use_case_name=USE_CASE_NAME,
        question=QUESTION,
        description=DESCRIPTION
    )
    
    exit(0 if success else 1)
