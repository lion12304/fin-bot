import master_agent
import warnings
import os



warnings.filterwarnings("ignore")


master_agent = master_agent.MasterAgent()

# Windows
if os.name == 'nt':
    os.system('cls')
# macOS and Linux
else:
    os.system('clear')

print(master_agent.choose_stock_and_return_result())