# macOS Screenshot Fix Documentation

## Problem Description

The Atlas application was experiencing issues with screenshot functionality on macOS, specifically with the Quartz (Core Graphics) API implementation. The error encountered was:

```
'CGImageRef' object has no attribute 'width'
```

This error occurred because the code was mixing old and new pyobjc API calls, attempting to use deprecated object methods alongside modern function-based API.

## Root Cause Analysis

1. **Mixed API Usage**: The code attempted to use both legacy object methods (`image_ref.width()`) and modern function-based API (`CGImageGetWidth(image_ref)`) simultaneously.

2. **pyobjc Version Compatibility**: Modern versions of pyobjc have moved away from object-based methods to function-based API for Core Graphics operations.

3. **Fallback Logic Issues**: The error handling wasn't properly falling back to alternative screenshot methods when Quartz failed.

## Solution Implemented

### 1. Modern Quartz API Implementation

Updated `tools/screenshot_tool.py` to use only the modern pyobjc API:

```python
def _capture_quartz() -> Image.Image:
    """Capture the full screen via Quartz and return a PIL Image."""
    try:
        # Create screenshot using Quartz API
        image_ref = CGWindowListCreateImage(
            CGRectInfinite, kCGWindowListOptionOnScreenOnly, CGMainDisplayID(), kCGWindowImageDefault
        )
        
        if not image_ref:
            raise Exception("Failed to create CGImage")
        
        # Use modern pyobjc API exclusively
        from Quartz import CGImageGetWidth, CGImageGetHeight, CGImageGetBytesPerRow
        from Quartz import CGImageGetDataProvider, CGDataProviderCopyData
        
        width = CGImageGetWidth(image_ref)
        height = CGImageGetHeight(image_ref)
        bytes_per_row = CGImageGetBytesPerRow(image_ref)
        data_provider = CGImageGetDataProvider(image_ref)
        data = CGDataProviderCopyData(data_provider)
        
        # Convert CFData to bytes
        if hasattr(data, 'bytes'):
            buffer = data.bytes()
        else:
            buffer = bytes(data)
        
        # Create PIL Image from buffer (Quartz returns BGRA format)
        img = Image.frombuffer("RGBA", (width, height), buffer, "raw", "BGRA", bytes_per_row, 1)
        
        # Convert to RGB for consistency
        if img.mode == "RGBA":
            rgb_img = Image.new("RGB", img.size, (255, 255, 255))
            rgb_img.paste(img, mask=img.split()[-1])  # Use alpha channel as mask
            return rgb_img
        
        return img
        
    except Exception as e:
        raise Exception(f"Quartz capture failed: {e}")
```

### 2. Enhanced Fallback System

The screenshot system now uses a robust fallback hierarchy:

1. **Native screencapture** (most reliable on macOS)
2. **AppleScript** (alternative native method)
3. **Quartz API** (programmatic access)
4. **PyAutoGUI** (cross-platform fallback)
5. **Dummy image** (last resort)

### 3. Comprehensive Testing

Created multiple testing tools:

- `test_screenshot_complete.py` - Comprehensive diagnostic tool
- `quick_test_macos.sh` - Enhanced quick testing script
- `test_screenshot_macos.py` - Original focused test

### 4. Better Error Handling

Improved error reporting and diagnostics:
- Detailed error messages for each screenshot method
- Platform-specific error handling
- Graceful fallbacks with user feedback

## Key Changes Made

### In `tools/screenshot_tool.py`:
- Removed mixed API usage
- Implemented modern pyobjc function-based API exclusively
- Added proper RGBA to RGB conversion
- Enhanced error handling and fallback logic

### In `utils/macos_screenshot.py`:
- Added native screencapture implementation
- Added AppleScript-based screenshot method
- Included comprehensive testing functions

### Testing Infrastructure:
- `test_screenshot_complete.py` - Full diagnostic suite
- `quick_test_macos.sh` - Enhanced quick testing
- Multiple validation scenarios

## Verification Steps

To verify the fix works on macOS:

1. **Quick Test**:
   ```bash
   chmod +x quick_test_macos.sh
   ./quick_test_macos.sh
   ```

2. **Comprehensive Test**:
   ```bash
   python3 test_screenshot_complete.py
   ```

3. **Integration Test**:
   ```bash
   python3 -c "from tools.screenshot_tool import capture_screen; img = capture_screen(); print(f'Success: {img.size}')"
   ```

## Expected Results

After the fix:
- ✅ Native screencapture should work (primary method)
- ✅ Quartz API should work without errors (fallback)
- ✅ AppleScript method should work (alternative)
- ✅ At least 2-3 screenshot methods should be functional
- ✅ No more `'CGImageRef' object has no attribute 'width'` errors

## Platform Compatibility

This solution maintains compatibility with:
- **macOS 10.15+** (modern API support)
- **macOS 11.0+** (full native feature support)
- **macOS 12.0+** (optimal performance)

## Dependencies Required

For full functionality on macOS:
```
Pillow>=9.5.0
pyobjc-framework-Quartz>=9.0
pyobjc-framework-ApplicationServices>=9.0
pyautogui>=0.9.54
```

## Troubleshooting

If issues persist:

1. **Check pyobjc installation**:
   ```bash
   pip install --upgrade pyobjc-framework-Quartz pyobjc-framework-ApplicationServices
   ```

2. **Verify macOS permissions**:
   - System Preferences → Security & Privacy → Privacy → Screen Recording
   - Add Terminal/Python to allowed applications

3. **Test individual methods**:
   ```bash
   python3 test_screenshot_complete.py
   ```

4. **Check for Homebrew Python issues**:
   - If using Homebrew Python, ensure tkinter is available
   - Consider using system Python or pyenv for GUI applications

## Future Improvements

- Add support for selective screen capture (specific displays)
- Implement screenshot caching for performance
- Add support for different image formats
- Enhance error recovery mechanisms
