import sys
import os

# Add the parent directory and specific subdirectories to sys.path
base_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(base_dir)
sys.path.append(os.path.join(base_dir, 'chat'))

try:
    from chat.chat_logic import ChatProcessor
    print('Successfully imported ChatProcessor')
except ImportError as e:
    print(f'Failed to import ChatProcessor: {e}')
