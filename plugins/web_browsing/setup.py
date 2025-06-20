#!/usr/bin/env python3
"""
Setup script for Advanced Web Browsing Plugin
Installs required dependencies and browser drivers
"""

import subprocess
import sys
import os
import platform
from pathlib import Path

def run_command(command, description=""):
    """Run a shell command with error handling"""
    print(f"🔧 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        print(f"Output: {e.stdout}")
        print(f"Error: {e.stderr}")
        return False

def install_python_dependencies():
    """Install Python dependencies"""
    plugin_dir = Path(__file__).parent
    requirements_file = plugin_dir / "requirements.txt"
    
    if requirements_file.exists():
        return run_command(
            f"{sys.executable} -m pip install -r {requirements_file}",
            "Installing Python dependencies"
        )
    else:
        print("❌ requirements.txt not found")
        return False

def install_playwright_browsers():
    """Install Playwright browsers"""
    return run_command(
        f"{sys.executable} -m playwright install",
        "Installing Playwright browsers"
    )

def install_chrome_driver():
    """Install Chrome WebDriver using webdriver-manager"""
    try:
        from webdriver_manager.chrome import ChromeDriverManager
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        
        print("🔧 Setting up Chrome WebDriver...")
        ChromeDriverManager().install()
        
        #Test Chrome driver
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        
        driver = webdriver.Chrome(options=options)
        driver.get("https://www.google.com")
        driver.quit()
        
        print("✅ Chrome WebDriver setup completed successfully")
        return True
        
    except Exception as e:
        print(f"❌ Chrome WebDriver setup failed: {e}")
        return False

def setup_macos_permissions():
    """Setup macOS specific permissions"""
    if platform.system() != "Darwin":
        return True
        
    print("🔧 Setting up macOS permissions...")
    print("⚠️  You may need to grant accessibility permissions to your terminal/IDE")
    print("   Go to: System Preferences > Security & Privacy > Privacy > Accessibility")
    print("   Add your terminal application (Terminal, iTerm, VS Code, etc.)")
    return True

def verify_installation():
    """Verify that everything is installed correctly"""
    print("\n🧪 Verifying installation...")
    
    #Test imports
    test_imports = [
        ("selenium", "Selenium WebDriver"),
        ("playwright", "Playwright"),
        ("bs4", "BeautifulSoup"),
        ("requests", "Requests"),
        ("pyautogui", "PyAutoGUI")
    ]
    
    for module, name in test_imports:
        try:
            __import__(module)
            print(f"✅ {name} imported successfully")
        except ImportError as e:
            print(f"❌ {name} import failed: {e}")
            return False
    
    return True

def main():
    """Main setup function"""
    print("🚀 Setting up Advanced Web Browsing Plugin...")
    print("=" * 50)
    
    success_count = 0
    total_steps = 5
    
    #Step 1: Install Python dependencies
    if install_python_dependencies():
        success_count += 1
    
    #Step 2: Install Playwright browsers
    if install_playwright_browsers():
        success_count += 1
    
    #Step 3: Install Chrome WebDriver
    if install_chrome_driver():
        success_count += 1
    
    #Step 4: Setup macOS permissions
    if setup_macos_permissions():
        success_count += 1
    
    #Step 5: Verify installation
    if verify_installation():
        success_count += 1
    
    print("\n" + "=" * 50)
    print(f"📊 Setup completed: {success_count}/{total_steps} steps successful")
    
    if success_count == total_steps:
        print("🎉 Advanced Web Browsing Plugin setup completed successfully!")
        print("\n📋 Available automation methods:")
        print("   1. Selenium WebDriver (Chrome, Firefox, Safari)")
        print("   2. Playwright (Chromium, Firefox, WebKit)")
        print("   3. System Events + PyAutoGUI")
        print("   4. Direct HTTP requests")
        print("\n✨ The plugin will automatically fallback between methods for maximum reliability!")
    else:
        print("⚠️  Some setup steps failed. The plugin may have limited functionality.")
    
    return success_count == total_steps

if __name__ == "__main__":
    main()
