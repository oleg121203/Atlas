#!/usr/bin/env python3
import os
import sys
from pathlib import Path

#Set up logging to file for debugging
import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(message)s',
    handlers=[
        logging.FileHandler('/workspaces/autoclicker/debug_test.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

def main():
    logger.info("🚀 Starting Atlas verification test")
    
    #Check .env file exists
    env_file = Path('/workspaces/autoclicker/.env')
    logger.info(f"📁 .env file exists: {env_file.exists()}")
    
    if env_file.exists():
        logger.info(f"📄 .env file size: {env_file.stat().st_size} bytes")
        with open(env_file, 'r') as f:
            content = f.read()
            logger.info(f"📋 .env content preview: {content[:100]}...")
    
    #Load environment
    try:
        from dotenv import load_dotenv
        load_dotenv()
        logger.info("✅ dotenv loaded successfully")
        
        #Check specific variables
        gemini_key = os.getenv('GEMINI_API_KEY', '')
        provider = os.getenv('DEFAULT_LLM_PROVIDER', '')
        
        logger.info(f"🔑 GEMINI_API_KEY length: {len(gemini_key) if gemini_key else 0}")
        logger.info(f"⚙️ DEFAULT_LLM_PROVIDER: {provider}")
        
    except Exception as e:
        logger.error(f"❌ Error loading dotenv: {e}")
        return False
    
    #Test config manager
    try:
        sys.path.insert(0, '/workspaces/autoclicker')
        from config_manager import ConfigManager
        config = ConfigManager()
        
        gemini_key = config.get_gemini_api_key()
        provider = config.get_current_provider()
        
        logger.info(f"🔧 Config Manager - Gemini key: {'✓' if gemini_key else '✗'}")
        logger.info(f"🔧 Config Manager - Provider: {provider}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error with ConfigManager: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False

if __name__ == "__main__":
    result = main()
    print(f"🎯 Final result: {'SUCCESS' if result else 'FAILED'}")
