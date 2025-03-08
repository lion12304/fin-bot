# FinBot

## installation

First, create a new virtual environment and install the required libraries by running the following commands:

On macOS/Linux
```
python -m venv finbot
source finbot/bin/activate
pip install -r requirements.txt
```
On Windows
```
python -m venv finbot
finbot\Scripts\activate
pip install -r requirements.txt
```
## Running the code
The master agent, which initiating the whole pipline is in agents/master_agent.py. You can activate it by running agents/RunAgent.py:
```
cd agents/
python RunAgent.py
```

## Note: Available Stocks
Since this work is a proof of concept, only the following stocks are available for demonstration:

Netflix (NFLX), Apple (AAPL), Google (GOOG), Amazon (AMZN), NVIDIA (NVDA), Advanced Micro Devices (AMD), and Meta (META).
