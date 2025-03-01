from agents.agent import *
import json

class QuarterlyReportAgent(Agent):
    def __init__(self):
        super().__init__()
        self.system = """
            You are finBot, an AI-driven finance agent. Your role is to predict a stock's future performence in the following quarter based on it's last 3 quarterly reports.

            ### **Input Sources:**  
            1. **1st quarterly report** - the latest quarterly report for the stock.  
            2. **2nd quarterly report** - the second latest quarterly report for the stock.  
            3. **3rd quarterly report** - the third latest quarterly report for the stock.  

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

    def generate_response(self, quarterly_report_1: str, quarterly_report_2: str, quarterly_report_3: str):

        formatted_prompt = f"""
            **latest quarterly report:**
            {quarterly_report_1}
            ---
            **second latest quarterly report:**
            {quarterly_report_2}
            ---
            **third latest quarterly report:**
            {quarterly_report_3}
        """
        response = super().generate_response(formatted_prompt)

        # extract feedback and decision from the response using json (TODO: check this)
        result_data = json.loads(response)
        prediction = result_data["prediction"]
        confidence = result_data["confidence"]
        return prediction, confidence

