#!/usr/bin/env python3
"""
Rentry Content Explorer

Discover what's actually posted on rentry.co through random URL exploration.
Works on Windows, Mac, and Linux with Python 3.6+
"""

import requests
import webbrowser
import time
import random
import string
import re
import sys
import os
from typing import List

# Check Python version compatibility
if sys.version_info < (3, 6):
    print("❌ This script requires Python 3.6 or higher")
    print(f"   You're running Python {sys.version_info.major}.{sys.version_info.minor}")
    sys.exit(1)

class RentryLinkGenerator:
    """Generator for random rentry.co link patterns"""
    
    def __init__(self):
        # Common words for potential future use
        self.words = [
            'cat', 'dog', 'blue', 'red', 'sun', 'moon', 'star', 'sky', 'sea', 'tree',
            'book', 'code', 'data', 'file', 'game', 'home', 'keys', 'lamp', 'note', 'page',
            'bird', 'fish', 'rock', 'wind', 'fire', 'rain', 'snow', 'leaf', 'rose', 'gold',
            'cool', 'fast', 'slow', 'big', 'tiny', 'new', 'old', 'hot', 'cold', 'nice',
            'link', 'test', 'demo', 'temp', 'work', 'play', 'time', 'date', 'word', 'text'
        ]
    
    def generate_random(self, length: int = 6) -> str:
        """Generate a random alphanumeric string"""
        chars = string.ascii_lowercase + string.digits
        return ''.join(random.choice(chars) for _ in range(length))

class RentryContentExplorer:
    """Main content discovery and exploration engine"""
    
    def __init__(self):
        self.generator = RentryLinkGenerator()
        self.session = requests.Session()
        # Cross-platform user agent
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
    
    def analyze_page_content(self, url: str) -> dict:
        """Analyze the page content to determine its status"""
        try:
            response = self.session.get(url, timeout=10)
            
            result = {
                'status_code': response.status_code,
                'url': url,
                'is_available': False,
                'is_error_page': False,
                'has_content': False,
                'content_type': 'unknown',
                'title': '',
                'should_open': False
            }
            
            content = response.text.lower()
            
            # Check for error pages
            error_indicators = [
                'error',
                '404 not found',
                'page not found',
                'not found',
                'oops',
                'something went wrong'
            ]
            
            # Check if it's an error page
            if any(indicator in content for indicator in error_indicators):
                result['is_error_page'] = True
                result['content_type'] = 'error_page'
            
            # Check for rentry-specific content
            rentry_indicators = [
                'rentry',
                'markdown paste service',
                'edit code',
                'custom url',
                'paste',
                'markdown'
            ]
            
            # Extract title
            title_match = re.search(r'<title>(.*?)</title>', content)
            if title_match:
                result['title'] = title_match.group(1).strip()
            
            # Determine if URL is available for use
            if response.status_code == 404:
                result['is_available'] = True
                result['content_type'] = 'available'
                result['should_open'] = False
            elif response.status_code == 200:
                # URL is taken, but check if it has actual content
                if any(indicator in content for indicator in rentry_indicators):
                    result['has_content'] = True
                    result['content_type'] = 'taken_with_content'
                    result['should_open'] = False
                else:
                    result['content_type'] = 'unknown_content'
                    result['should_open'] = False
            
            return result
            
        except requests.RequestException as e:
            return {
                'status_code': 0,
                'url': url,
                'is_available': False,
                'is_error_page': True,
                'has_content': False,
                'content_type': 'request_error',
                'title': f'Error: {str(e)}',
                'should_open': False
            }
    
    def test_url_availability(self, url_id: str) -> bool:
        """Test if URL returns 404 (available for use)"""
        full_url = f"https://rentry.co/{url_id}"
        
        try:
            response = self.session.head(full_url, timeout=5, allow_redirects=True)
            if response.status_code == 405:  # Method not allowed, try GET
                response = self.session.get(full_url, timeout=5)
            
            return response.status_code == 404
                
        except requests.RequestException:
            return False
    
    def explore_content(self, count, open_browser: bool = True, max_attempts: int = None):
        """Main content exploration function"""
        
        if max_attempts is None:
            if count == float('inf'):
                max_attempts = float('inf')
            else:
                max_attempts = count * 10
        
        if count == float('inf'):
            print(f"🔍 Exploring UNLIMITED rentry.co content...")
            print(f"📝 Method: random")
            print(f"🎯 Max attempts: UNLIMITED (Press Ctrl+C to stop)")
        else:
            print(f"🔍 Exploring rentry.co content (looking for {count} available URLs)...")
            print(f"📝 Method: random")
            print(f"🎯 Max attempts: {max_attempts}")
        print("=" * 60)
        
        available_urls = []
        attempts = 0
        
        try:
            while len(available_urls) < count and attempts < max_attempts:
                attempts += 1
                
                # Generate random URL
                url_id = self.generator.generate_random(random.randint(4, 8))
                full_url = f"https://rentry.co/{url_id}"
                
                print(f"🔄 Attempt {attempts:2d}: Testing {full_url}...", end=" ", flush=True)
                
                # Test URL status
                is_available = self.test_url_availability(url_id)
                
                if is_available:
                    print("🔍 Available (404)")
                    available_urls.append(full_url)
                else:
                    print("📄 Taken - ", end="", flush=True)
                    
                    # This URL has content, open it to see what's there
                    if open_browser:
                        print("Opening in browser...")
                        try:
                            webbrowser.open(full_url)
                            time.sleep(1.5)  # Delay between browser opens
                        except Exception as e:
                            print(f"Could not open browser: {e}")
                    else:
                        print("Has content")
                
                # Small delay to be respectful
                time.sleep(0.3)
                
        except KeyboardInterrupt:
            print(f"\n\n⛔ Stopped by user after {attempts} attempts")
        
        taken_count = attempts - len(available_urls)
        print("=" * 60)
        print(f"📊 Results: {len(available_urls)} available URLs | {taken_count} taken URLs | {attempts} total attempts")
        
        if available_urls:
            print(f"\n📋 Available URLs (ready to use for creating pastes):")
            for i, url in enumerate(available_urls, 1):
                print(f"   {i:2d}. {url}")
            
            # Save to file with cross-platform timestamp
            timestamp = int(time.time())
            filename = f"available_rentry_urls_{timestamp}.txt"
            
            try:
                with open(filename, "w", encoding='utf-8') as f:
                    f.write("Available Rentry.co URLs\n")
                    f.write("=" * 30 + "\n")
                    f.write(f"Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                    f.write(f"Method: random\n")
                    f.write(f"Total attempts: {attempts}\n")
                    f.write(f"Success rate: {len(available_urls)/attempts*100:.1f}%\n\n")
                    
                    f.write("Available URLs (copy these to create new rentry.co pastes):\n")
                    f.write("-" * 50 + "\n")
                    for i, url in enumerate(available_urls, 1):
                        f.write(f"{i:2d}. {url}\n")
                
                print(f"\n💾 Saved results to '{filename}'")
                
            except Exception as e:
                print(f"\n❌ Could not save to file: {e}")
        else:
            print("\n❌ No available URLs found. Try again or run longer.")
        
        return available_urls

def check_dependencies():
    """Check if required dependencies are installed"""
    try:
        import requests
        return True
    except ImportError:
        print("❌ Missing required dependency: requests")
        print("\n📦 Please install it:")
        print("   pip install requests")
        print("   (or pip3 install requests)")
        return False

def get_user_input():
    """Get user preferences with cross-platform input handling"""
    print("🚀 === Rentry Content Explorer ===\n")
    
    # Get number of URLs or unlimited mode
    while True:
        try:
            count_input = input("🔢 How many available URLs to find? (Enter number or 'unlimited'): ").strip()
            if count_input.lower() in ['unlimited', 'infinite', 'inf', 'u']:
                count = float('inf')
                print("🚀 Unlimited mode activated! Press Ctrl+C to stop when ready.")
                break
            else:
                count = int(count_input)
                if count > 0:
                    break
                else:
                    print("❌ Please enter a positive number.")
        except ValueError:
            print("❌ Please enter a valid number or 'unlimited'.")
        except (EOFError, KeyboardInterrupt):
            print("\n\n⛔ Cancelled by user.")
            sys.exit(0)
    
    # Ask about opening browser
    while True:
        try:
            open_choice = input("🌐 Open taken URLs in browser to see content? (y/n): ").strip().lower()
            if open_choice in ['y', 'yes', '1', 'true']:
                open_browser = True
                break
            elif open_choice in ['n', 'no', '0', 'false']:
                open_browser = False
                break
            else:
                print("❌ Please enter 'y' or 'n'.")
        except (EOFError, KeyboardInterrupt):
            print("\n\n⛔ Cancelled by user.")
            sys.exit(0)
    
    return count, open_browser

def main():
    """Main function with universal compatibility"""
    # Check dependencies first
    if not check_dependencies():
        sys.exit(1)
    
    try:
        # Get user preferences
        count, open_browser = get_user_input()
        
        print(f"\n🚀 Starting content exploration...")
        if open_browser:
            print("💡 Note: Available URLs (404) = ready to use | Taken URLs = will open to discover content!")
        else:
            print("💡 Note: Available URLs (404) = ready to use | Taken URLs = reported but not opened")
        print()
        
        # Start exploration
        explorer = RentryContentExplorer()
        available_urls = explorer.explore_content(
            count=count,
            open_browser=open_browser
        )
        
        if available_urls:
            print(f"\n🎉 Exploration complete! Found {len(available_urls)} available URLs.")
            if open_browser:
                print("📝 Check your browser tabs for discovered content!")
        
    except KeyboardInterrupt:
        print("\n\n⛔ Operation cancelled by user.")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        print("💡 Try running the script again or check your internet connection.")

if __name__ == "__main__":
    main() 