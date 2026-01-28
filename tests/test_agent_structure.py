import unittest
from unittest.mock import MagicMock, patch
import sys
import os

sys.path.append('/workspace')

class TestAgentStructure(unittest.TestCase):
    
    @patch.dict(os.environ, {"OPENAI_API_KEY": "sk-fake-key-for-testing"})
    def test_graph_compilation(self):
        # We need to ensure panelin.agent.graph is not already imported
        if 'panelin.agent.graph' in sys.modules:
            del sys.modules['panelin.agent.graph']
            
        from panelin.agent.graph import app
        
        self.assertIsNotNone(app)
        print("Agent Graph compiled successfully in test.")

if __name__ == '__main__':
    unittest.main()
