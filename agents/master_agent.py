from agents.agent import *
import json

class MasterAgent(Agent):
    def __init__(self):
        super().__init__()
        self.system = """
            You are finBot, an AI-driven finance agent. Your role is to predict a stock's future performence in the following quarter by aggregating the predictions of a few different agents.

            ### **Input Sources:**  
            1. **numerical quarterly report agent results** - prediction of the agent and a confidence score between 1 and 10.  
            2. **literal quarterly report agent results** - prediction of the agent and a confidence score between 1 and 10.  
            3. **stock price agent results** - prediction of the agent and a confidence score between 1 and 10.  

            ### **Responsibilities:**  
            1. **aggregate the results for a final verdict** - "stock price up" or "stock price down".
              

            ### **Output Format:**  
            Your output should be structured in **JSON format** as follows:
            ```json
            {
                "prediction": "stock price up" or "stock price down"
            }
            ```
            Your output should be as precise as possible.
        """
    
    # TODO: maybe add all of the agents as variables to the class and call their generate_response methods to get their predictions

    def generate_response(self, pred1: str, conf1: int, pred2: str, conf2: int, pred3: str, conf3: int):

        formatted_prompt = f"""
            **numerical quarterly report agent results:**
            {pred1} with confidence {conf1}
            ---
            **literal quarterly report agent results:**
            {pred2} with confidence {conf2}
            ---
            **stock price agent results:**
            {pred3} with confidence {conf3}
        """
        response = super().generate_response(formatted_prompt)

        # extract feedback and decision from the response using json (TODO: check this)
        result_data = json.loads(response)
        prediction = result_data["prediction"]
        return prediction

