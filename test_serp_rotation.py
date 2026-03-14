import os
import sys
from unittest.mock import MagicMock, patch

# Add current dir to path
sys.path.append(os.getcwd())

# Mock SerpAPI package before importing
mock_serp = MagicMock()
sys.modules["serpapi"] = mock_serp

from antigravity_deal_score import SerpKeyManager, serp_manager, serpapi_check_rank

def test_rotation():
    print("Testing SerpAPI Key Rotation...")
    
    # Setup manager with mock keys
    serp_manager.keys = ["KEY_EXHAUSTED", "KEY_VALID"]
    serp_manager.exhausted_keys = set()
    serp_manager.current_index = 0
    
    print(f"Initial Keys: {serp_manager.keys}")
    
    # Mock GoogleSearch to return quota error for the first key
    with patch("antigravity_deal_score.GoogleSearch") as MockSearch:
        search_instance = MockSearch.return_value
        
        # Generator for side effects: 1st call returns quota error, 2nd call returns success
        def mock_get_dict():
            current_key = MockSearch.call_args[0][0]["api_key"]
            print(f"Calling SerpAPI with: {current_key}")
            if current_key == "KEY_EXHAUSTED":
                return {"error": "Your SerpAPI quota is exhausted"}
            return {"organic_results": [{"link": "example.com"}]}
            
        search_instance.get_dict.side_effect = mock_get_dict
        
        print("\nTriggering rank check for domain 'example'...")
        rank = serpapi_check_rank("example.com", "epoxy")
        
        print(f"\nResult Rank: {rank}")
        print(f"Exhausted Keys: {serp_manager.exhausted_keys}")
        
        if rank == 1 and "KEY_EXHAUSTED" in serp_manager.exhausted_keys:
            print("\n✅ SUCCESS: Key rotation worked perfectly!")
        else:
            print("\n❌ FAILED: Key rotation did not achieve expected result.")

if __name__ == "__main__":
    test_rotation()
