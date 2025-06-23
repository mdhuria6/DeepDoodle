#from sarvam import SarvamAgent

# Create agent instance
# agent = SarvamAgent()
# print(agent.run("convert  - two hedgehogs", target_language="Hindi"))
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.sarvam import sarvam_agent

def test_sarvam_translation():
    test_state = {
        "prompt": "Did it hear me?",
        "target_language": "Hindi"
    }
    result = sarvam_agent(test_state)
    print("Sarvam Hindi translation:", result["sarvam_output"])

if __name__ == "__main__":
    test_sarvam_translation()