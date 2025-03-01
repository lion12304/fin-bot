from agents.agent import *
import json

class StockPriceAgent(Agent):
    def __init__(self):
        super().__init__()
        # TODO: check whether we want to use an image of a graph as input or statistics about the historical stock prices
        self.system = """
            You are finBot, an AI-driven finance agent. Your role is to predict a stock's future performence in the following quarter based on it's historical stock prices.

            ### **Input Sources:**  
            1. **statistics** - the statistics about the stock prices over time.  
            

            ### **Responsibilities:**  
            1. **predict performence in the following quarter** - "stock price up" or "stock price down" or "stock price same".
            1. **say how confident you are in your prediction** - an integer betweeen 1 and 10.  
              

            ### **Output Format:**  
            Your output should be structured in **JSON format** as follows:
            ```json
            {
                "prediction": "stock price up" or "stock price down" or "stock price same",
                "confidence": an integer between 1 and 10.
            }
            ```
            Your output should be as precise as possible.
        """

    def generate_response(self, statistics: str):

        formatted_prompt = f"""
            **statistics:**
            {statistics}
            ---
        """
        response = super().generate_response(formatted_prompt)

        # extract feedback and decision from the response using json (TODO: check this)
        result_data = json.loads(response)
        prediction = result_data["prediction"]
        confidence = result_data["confidence"]
        return prediction, confidence