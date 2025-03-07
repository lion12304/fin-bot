import master_agent
import warnings
import os

"""
This script runs the master agent, initiating the whole pipeline of our agent
"""

warnings.simplefilter("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore")
master_agent = master_agent.MasterAgent()

# Windows
if os.name == 'nt':
    os.system('cls')
# macOS and Linux
else:
    os.system('clear')

master_agent.choose_stock_and_return_result()
