#!/usr/bin/env python3
"""
Test script for Advanced Web Browsing Plugin
Tests all fallback methods for AutoRia car search
"""

import sys
import time
from pathlib import Path

#Add plugin to path
plugin_dir = Path(__file__).parent / "plugins" / "web_browsing"
sys.path.append(str(plugin_dir))

def test_basic_navigation():
    """Test basic navigation functionality"""
    print("🧪 Testing basic navigation...")

    try:
        import plugin as web_plugin

        #Test navigation to AutoRia
        result = web_plugin.navigate_to_url("https://auto.ria.com")
        print(f"Navigation result: {result}")

        #Wait a bit
        time.sleep(3)

        #Take screenshot
        screenshot_result = web_plugin.take_screenshot("autoria_homepage.png")
        print(f"Screenshot result: {screenshot_result}")

        return True

    except Exception as e:
        print(f"❌ Basic navigation test failed: {e}")
        return False

def test_car_search():
    """Test complete car search workflow"""
    print("🚗 Testing car search workflow...")

    try:
        import plugin as web_plugin

        #Navigate to AutoRia
        print("📍 Navigating to AutoRia...")
        nav_result = web_plugin.navigate_to_url("https://auto.ria.com")
        print(f"Navigation: {nav_result}")

        #Wait for page load
        print("⏳ Waiting for page to load...")
        wait_result = web_plugin.wait_for_element(".searchForm", 10)
        print(f"Wait result: {wait_result}")

        #Search for Mustang
        print("🔍 Searching for Mustang 2024...")
        search_result = web_plugin.search_on_site("Ford Mustang 2024")
        print(f"Search result: {search_result}")

        #Wait for results
        time.sleep(5)

        #Scrape results
        print("📊 Scraping search results...")
        scrape_result = web_plugin.scrape_page_content('["h3", ".price", ".item-char"]')
        print(f"Scraping result: {scrape_result}")

        #Take final screenshot
        final_screenshot = web_plugin.take_screenshot("mustang_search_results.png")
        print(f"Final screenshot: {final_screenshot}")

        return True

    except Exception as e:
        print(f"❌ Car search test failed: {e}")
        return False

def test_fallback_methods():
    """Test fallback between different automation methods"""
    print("🔄 Testing fallback methods...")

    try:
        import plugin as web_plugin

        #Get browser instance
        browser = web_plugin.get_browser()

        print(f"Available methods: {browser.available_methods}")

        #Test each method individually
        test_url = "https://httpbin.org/get"

        for method in browser.available_methods:
            print(f"Testing method: {method}")

            if method == "selenium":
                if browser._init_selenium():
                    success = browser._navigate_selenium(test_url)
                    print(f"  Selenium: {'✅ Success' if success else '❌ Failed'}")
                else:
                    print("  Selenium: ❌ Init failed")

            elif method == "playwright":
                if browser._init_playwright():
                    success = browser._navigate_playwright(test_url)
                    print(f"  Playwright: {'✅ Success' if success else '❌ Failed'}")
                else:
                    print("  Playwright: ❌ Init failed")

            elif method == "system_events":
                success = browser._navigate_system_events(test_url)
                print(f"  System Events: {'✅ Success' if success else '❌ Failed'}")

            elif method == "http_requests":
                import requests
                try:
                    response = requests.get(test_url, timeout=10)
                    success = response.status_code == 200
                    print(f"  HTTP Requests: {'✅ Success' if success else '❌ Failed'}")
                except requests.exceptions.RequestException:
                    print("  HTTP Requests: ❌ Failed")

        return True

    except Exception as e:
        print(f"❌ Fallback methods test failed: {e}")
        return False

def test_enhanced_browser_agent():
    """Test integration with Enhanced Browser Agent"""
    print("🤖 Testing Enhanced Browser Agent integration...")

    try:
        #Add Atlas agents to path
        agents_dir = Path(__file__).parent / "agents"
        sys.path.append(str(agents_dir))

        from browser_agent import BrowserAgent

        agent = BrowserAgent()

        #Test various commands
        commands = [
            "navigate to https://auto.ria.com",
            "search for Ford Mustang 2024",
            "take screenshot mustang_results.png",
            "scroll down 3 times",
            "wait for .search-results 15 seconds",
        ]

        for command in commands:
            print(f"🎯 Testing command: {command}")
            result = agent.execute_task(command, {})
            print(f"   Result: {result[:100]}...")
            time.sleep(2)

        return True

    except Exception as e:
        print(f"❌ Enhanced Browser Agent test failed: {e}")
        return False

def run_all_tests():
    """Run all tests"""
    print("🚀 Starting Advanced Web Browsing Plugin Tests")
    print("=" * 60)

    tests = [
        ("Basic Navigation", test_basic_navigation),
        ("Car Search Workflow", test_car_search),
        ("Fallback Methods", test_fallback_methods),
        ("Enhanced Browser Agent", test_enhanced_browser_agent),
    ]

    results = []

    for test_name, test_func in tests:
        print(f"\n📋 Running: {test_name}")
        print("-" * 40)

        try:
            success = test_func()
            results.append((test_name, success))
            status = "✅ PASSED" if success else "❌ FAILED"
            print(f"Result: {status}")
        except Exception as e:
            print(f"❌ FAILED with exception: {e}")
            results.append((test_name, False))

    #Print summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)

    passed = sum(1 for _, success in results if success)
    total = len(results)

    for test_name, success in results:
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{test_name:30} {status}")

    print("-" * 60)
    print(f"Total: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All tests passed! Web browsing plugin is ready!")
    else:
        print("⚠️  Some tests failed. Check setup and dependencies.")

    return passed == total

if __name__ == "__main__":
    run_all_tests()
