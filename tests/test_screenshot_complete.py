#!/usr/bin/env python3
"""Complete screenshot testing script for macOS with detailed diagnostics."""

import sys
import traceback
from pathlib import Path
from PIL import Image
import tempfile
import subprocess

def test_imports():
    """Test if required modules can be imported."""
    print("=" * 60)
    print("TESTING IMPORTS")
    print("=" * 60)
    
    #Test basic imports
    modules = [
        ('PIL', 'from PIL import Image'),
        ('pathlib', 'from pathlib import Path'),
        ('tempfile', 'import tempfile'),
        ('subprocess', 'import subprocess'),
    ]
    
    for name, import_str in modules:
        try:
            exec(import_str)
            print(f"✅ {name}: Available")
        except Exception as e:
            print(f"❌ {name}: {e}")
    
    #Test macOS specific imports
    print("\nmacOS-specific imports:")
    try:
        from Quartz import (
            CGWindowListCreateImage, CGRectInfinite, kCGWindowListOptionOnScreenOnly,
            CGMainDisplayID, kCGWindowImageDefault, CGImageGetWidth, CGImageGetHeight,
            CGImageGetBytesPerRow, CGImageGetDataProvider, CGDataProviderCopyData
        )
        print("✅ Quartz: All functions available")
        return True
    except ImportError as e:
        print(f"❌ Quartz: {e}")
        return False

def test_native_screencapture():
    """Test native macOS screencapture command."""
    print("\n" + "=" * 60)
    print("TESTING NATIVE SCREENCAPTURE")
    print("=" * 60)
    
    try:
        #Check if screencapture command exists
        result = subprocess.run(['which', 'screencapture'], capture_output=True, text=True)
        if result.returncode != 0:
            print("❌ screencapture command not found")
            return False
        
        print(f"✅ screencapture found at: {result.stdout.strip()}")
        
        #Test actual screenshot
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_file:
            tmp_path = tmp_file.name
        
        result = subprocess.run([
            'screencapture', '-x', '-t', 'png', tmp_path
        ], capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"❌ screencapture failed: {result.stderr}")
            return False
        
        #Check if file was created and load it
        if not Path(tmp_path).exists():
            print("❌ Screenshot file was not created")
            return False
        
        img = Image.open(tmp_path)
        print(f"✅ Screenshot captured: {img.size[0]}x{img.size[1]} pixels")
        
        #Clean up
        Path(tmp_path).unlink(missing_ok=True)
        return True
        
    except Exception as e:
        print(f"❌ Native screencapture error: {e}")
        traceback.print_exc()
        return False

def test_quartz_capture():
    """Test Quartz-based screenshot."""
    print("\n" + "=" * 60)
    print("TESTING QUARTZ CAPTURE")
    print("=" * 60)
    
    try:
        from Quartz import (
            CGWindowListCreateImage, CGRectInfinite, kCGWindowListOptionOnScreenOnly,
            CGMainDisplayID, kCGWindowImageDefault, CGImageGetWidth, CGImageGetHeight,
            CGImageGetBytesPerRow, CGImageGetDataProvider, CGDataProviderCopyData
        )
        
        print("✅ Quartz imports successful")
        
        #Create screenshot
        image_ref = CGWindowListCreateImage(
            CGRectInfinite, kCGWindowListOptionOnScreenOnly, CGMainDisplayID(), kCGWindowImageDefault
        )
        
        if not image_ref:
            print("❌ Failed to create CGImage")
            return False
        
        print("✅ CGImage created successfully")
        
        #Get image properties
        width = CGImageGetWidth(image_ref)
        height = CGImageGetHeight(image_ref)
        bytes_per_row = CGImageGetBytesPerRow(image_ref)
        
        print(f"✅ Image properties: {width}x{height}, bytes_per_row: {bytes_per_row}")
        
        #Get image data
        data_provider = CGImageGetDataProvider(image_ref)
        data = CGDataProviderCopyData(data_provider)
        
        #Convert to bytes
        if hasattr(data, 'bytes'):
            buffer = data.bytes()
        else:
            buffer = bytes(data)
        
        print(f"✅ Image data extracted: {len(buffer)} bytes")
        
        #Create PIL Image
        img = Image.frombuffer("RGBA", (width, height), buffer, "raw", "BGRA", bytes_per_row, 1)
        print(f"✅ PIL Image created: {img.size[0]}x{img.size[1]} pixels, mode: {img.mode}")
        
        #Convert to RGB
        if img.mode == "RGBA":
            rgb_img = Image.new("RGB", img.size, (255, 255, 255))
            rgb_img.paste(img, mask=img.split()[-1])
            img = rgb_img
            
        print(f"✅ Converted to RGB: {img.mode}")
        return True
        
    except ImportError as e:
        print(f"❌ Quartz import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Quartz capture error: {e}")
        traceback.print_exc()
        return False

def test_applescript_capture():
    """Test AppleScript-based screenshot."""
    print("\n" + "=" * 60)
    print("TESTING APPLESCRIPT CAPTURE")  
    print("=" * 60)
    
    try:
        #Check if osascript exists
        result = subprocess.run(['which', 'osascript'], capture_output=True, text=True)
        if result.returncode != 0:
            print("❌ osascript command not found")
            return False
        
        print(f"✅ osascript found at: {result.stdout.strip()}")
        
        #Create temporary file
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_file:
            tmp_path = tmp_file.name
        
        #Simple AppleScript that just calls screencapture
        applescript = f'do shell script "screencapture -x \\"{tmp_path}\\""'
        
        result = subprocess.run([
            'osascript', '-e', applescript
        ], capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"❌ AppleScript failed: {result.stderr}")
            return False
        
        #Check file and load image
        if not Path(tmp_path).exists():
            print("❌ AppleScript screenshot file not created")
            return False
        
        img = Image.open(tmp_path)
        print(f"✅ AppleScript screenshot: {img.size[0]}x{img.size[1]} pixels")
        
        #Clean up
        Path(tmp_path).unlink(missing_ok=True)
        return True
        
    except Exception as e:
        print(f"❌ AppleScript error: {e}")
        traceback.print_exc()
        return False

def test_pyautogui():
    """Test PyAutoGUI screenshot (if available)."""
    print("\n" + "=" * 60)
    print("TESTING PYAUTOGUI")
    print("=" * 60)
    
    try:
        import pyautogui
        print("✅ PyAutoGUI imported successfully")
        
        #Test screenshot
        screenshot = pyautogui.screenshot()
        print(f"✅ PyAutoGUI screenshot: {screenshot.size[0]}x{screenshot.size[1]} pixels")
        return True
        
    except ImportError as e:
        print(f"❌ PyAutoGUI not available: {e}")
        return False
    except Exception as e:
        print(f"❌ PyAutoGUI error: {e}")
        traceback.print_exc()
        return False

def test_integrated_screenshot():
    """Test the integrated screenshot function from our tool."""
    print("\n" + "=" * 60)
    print("TESTING INTEGRATED SCREENSHOT TOOL")
    print("=" * 60)
    
    try:
        #Add current directory to path to import our module
        sys.path.insert(0, str(Path(__file__).parent))
        from tools.screenshot_tool import capture_screen
        
        print("✅ Screenshot tool imported")
        
        #Test capture
        img = capture_screen()
        print(f"✅ Integrated screenshot: {img.size[0]}x{img.size[1]} pixels, mode: {img.mode}")
        
        #Test saving
        test_file = Path("test_screenshot.png")
        img.save(test_file)
        print(f"✅ Screenshot saved to {test_file}")
        
        #Clean up
        test_file.unlink(missing_ok=True)
        return True
        
    except Exception as e:
        print(f"❌ Integrated screenshot error: {e}")
        traceback.print_exc()
        return False

def main():
    """Run all tests."""
    print("macOS Screenshot Testing Suite")
    print(f"Python version: {sys.version}")
    print(f"Platform: {sys.platform}")
    
    if sys.platform != 'darwin':
        print("❌ This script is designed for macOS (darwin)")
        return
    
    #Run all tests
    results = []
    
    results.append(("Imports", test_imports()))
    results.append(("Native screencapture", test_native_screencapture()))
    results.append(("Quartz capture", test_quartz_capture()))
    results.append(("AppleScript", test_applescript_capture()))
    results.append(("PyAutoGUI", test_pyautogui()))
    results.append(("Integrated tool", test_integrated_screenshot()))
    
    #Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\nPassed: {passed}/{len(results)} tests")
    
    if passed >= 2:  #At least 2 methods working
        print("🎉 Screenshot functionality should work!")
    else:
        print("⚠️  Limited screenshot functionality available")

if __name__ == "__main__":
    main()
