import random
import time
import asyncio
import json
import os
import subprocess
import sys
from flask import Flask, render_template, request, jsonify
import threading
import logging
from datetime import datetime
import re

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Global variables
PLAYWRIGHT_AVAILABLE = False
BROWSER_INSTALLED = False
app = Flask(__name__)
livelogs = []
tasks_data = {}
task_lock = threading.Lock()

# Emoji ranges for message enhancement
EMOJI_RANGES = [
    (0x1F600, 0x1F64F), (0x1F300, 0x1F5FF), (0x1F680, 0x1F6FF),
    (0x1F1E0, 0x1F1FF), (0x2600, 0x26FF), (0x2700, 0x27BF)
]

def log_console(msg):
    """Thread-safe logging"""
    timestamp = datetime.now().strftime('%H:%M:%S')
    formatted_msg = f"[{timestamp}] {msg}"
    print(formatted_msg)
    
    with task_lock:
        livelogs.append(formatted_msg)
        if len(livelogs) > 1000:
            livelogs.pop(0)

def install_playwright_and_browser():
    """Install Playwright and Chromium browser"""
    global PLAYWRIGHT_AVAILABLE, BROWSER_INSTALLED
    
    try:
        log_console("🚀 Installing Playwright...")
        
        # Install Playwright via pip
        result = subprocess.run([
            sys.executable, "-m", "pip", "install", 
            "playwright==1.47.0", "flask==2.3.3"
        ], capture_output=True, text=True, timeout=600)
        
        if result.returncode == 0:
            PLAYWRIGHT_AVAILABLE = True
            log_console("✅ Playwright installed successfully!")
        else:
            log_console(f"❌ Playwright installation failed: {result.stderr[:500]}")
            return False

        # Install Chromium browser
        log_console("📦 Installing Chromium browser...")
        install_result = subprocess.run([
            sys.executable, "-m", "playwright", "install", "chromium"
        ], capture_output=True, text=True, timeout=1800)
        
        if install_result.returncode == 0:
            BROWSER_INSTALLED = True
            log_console("✅ Chromium installed successfully!")
        else:
            log_console(f"⚠️ Chromium installation warning: {install_result.stderr[:500]}")
            # Try to continue anyway

        # Test imports
        try:
            from playwright.async_api import async_playwright
            log_console("🎉 Playwright imports successful!")
            return True
        except ImportError as e:
            log_console(f"❌ Playwright import test failed: {e}")
            return False
            
    except subprocess.TimeoutExpired:
        log_console("❌ Installation timed out")
        return False
    except Exception as e:
        log_console(f"❌ Installation error: {str(e)}")
        return False

def generate_random_emoji():
    """Generate a random emoji"""
    start, end = random.choice(EMOJI_RANGES)
    return chr(random.randint(start, end))

def enhance_message(message):
    """Add random emojis to message"""
    if not message or len(message.strip()) == 0:
        return message
        
    words = message.split()
    if len(words) <= 1:
        return f"{generate_random_emoji()} {message} {generate_random_emoji()}"
    
    # Add emojis randomly
    enhanced_words = []
    for i, word in enumerate(words):
        enhanced_words.append(word)
        if random.random() < 0.3 and i < len(words) - 1:
            enhanced_words.append(generate_random_emoji())
    
    # Add prefix/suffix emojis
    if random.random() < 0.4:
        enhanced_words.insert(0, generate_random_emoji())
    if random.random() < 0.4:
        enhanced_words.append(generate_random_emoji())
    
    return ' '.join(enhanced_words)

def parse_cookies(cookie_input):
    """Parse cookies from various formats"""
    cookies = []
    
    if not cookie_input or not cookie_input.strip():
        return cookies
    
    log_console(f"🔍 Parsing cookies input (length: {len(cookie_input)})")
    
    # Clean input
    cookie_input = cookie_input.strip()
    
    # Method 1: JSON array format
    if cookie_input.startswith('[') and cookie_input.endswith(']'):
        try:
            data = json.loads(cookie_input)
            if isinstance(data, list):
                for item in data:
                    if isinstance(item, dict) and 'name' in item and 'value' in item:
                        cookies.append({
                            'name': str(item['name']),
                            'value': str(item['value']),
                            'domain': item.get('domain', '.facebook.com'),
                            'path': item.get('path', '/'),
                            'secure': item.get('secure', True),
                            'httpOnly': item.get('httpOnly', False)
                        })
                if cookies:
                    log_console(f"✅ Parsed {len(cookies)} cookies from JSON array")
                    return cookies
        except json.JSONDecodeError:
            pass
    
    # Method 2: Key=value format (most common)
    lines = cookie_input.split('\n')
    for line in lines:
        line = line.strip()
        if '=' in line and not line.startswith('#') and not line.startswith('//'):
            # Handle key=value pairs
            parts = line.split('=', 1)
            if len(parts) == 2:
                name = parts[0].strip()
                value = parts[1].strip()
                
                # Remove quotes and semicolons
                name = name.replace('"', '').replace("'", "").replace(';', '')
                value = value.split(';')[0].replace('"', '').replace("'", "")
                
                if name and value and len(name) > 1 and len(value) > 1:
                    cookies.append({
                        'name': name,
                        'value': value,
                        'domain': '.facebook.com',
                        'path': '/',
                        'secure': True,
                        'httpOnly': False
                    })
    
    # Remove duplicates
    unique_cookies = []
    seen = set()
    for cookie in cookies:
        key = (cookie['name'].lower(), cookie['value'])
        if key not in seen:
            unique_cookies.append(cookie)
            seen.add(key)
    
    log_console(f"✅ Final parsed cookies: {len(unique_cookies)}")
    return unique_cookies[:20]  # Limit to 20 cookies

def get_input_data(req, field_name):
    """Extract input data from request"""
    data = []
    
    # Try text input first
    text_input = req.form.get(field_name, '').strip()
    if text_input:
        lines = [line.strip() for line in text_input.split('\n') if line.strip()]
        data.extend(lines)
    
    # Try file upload
    file = req.files.get(f'{field_name}_file')
    if file and file.filename:
        try:
            content = file.read().decode('utf-8')
            lines = [line.strip() for line in content.split('\n') if line.strip()]
            data.extend(lines)
            log_console(f"📁 Loaded {len(lines)} items from {file.filename}")
        except Exception as e:
            log_console(f"❌ File read error: {e}")
    
    return data

async def send_facebook_message_playwright(cookies, conversation_id, message, task_id):
    """Send message using Playwright"""
    if not PLAYWRIGHT_AVAILABLE:
        log_console(f"[{task_id}] ❌ Playwright not available")
        return False
    
    try:
        from playwright.async_api import async_playwright
        
        log_console(f"[{task_id}] 🚀 Starting browser...")
        
        async with async_playwright() as p:
            # Launch browser with options
            browser = await p.chromium.launch(
                headless=True,
                args=[
                    '--no-sandbox',
                    '--disable-setuid-sandbox',
                    '--disable-dev-shm-usage',
                    '--disable-accelerated-2d-canvas',
                    '--no-first-run',
                    '--no-zygote',
                    '--disable-gpu',
                    '--disable-web-security',
                    '--disable-features=VizDisplayCompositor',
                    '--disable-background-timer-throttling',
                    '--disable-backgrounding-occluded-windows',
                    '--disable-renderer-backgrounding'
                ],
                timeout=60000
            )
            
            # Create context with realistic user agent
            context = await browser.new_context(
                viewport={'width': 1280, 'height': 720},
                user_agent='Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                ignore_https_errors=True
            )
            
            # Add cookies to context
            if cookies:
                await context.add_cookies(cookies)
                log_console(f"[{task_id}] ✅ Loaded {len(cookies)} cookies")
            
            page = await context.new_page()
            
            # Navigate to Facebook messages
            url = f"https://www.facebook.com/messages/t/{conversation_id}"
            log_console(f"[{task_id}] 🌐 Navigating to {url}")
            
            try:
                await page.goto(url, wait_until='networkidle', timeout=45000)
            except Exception as e:
                log_console(f"[{task_id}] ⚠️ Page load timeout, continuing...")
            
            # Wait for page to settle
            await page.wait_for_timeout(5000)
            
            # Check if we're logged in by looking for login elements or message input
            login_indicators = await page.query_selector('input[name="email"], input[name="pass"], #loginform')
            if login_indicators:
                log_console(f"[{task_id}] ❌ Not logged in - invalid cookies")
                await browser.close()
                return False
            
            # Try multiple selectors for message input
            input_selectors = [
                'div[contenteditable="true"][role="textbox"]',
                'div[aria-label*="Message"][contenteditable="true"]',
                'div[aria-label*="message"][contenteditable="true"]',
                'div[data-lexical-editor="true"]',
                '[contenteditable="true"]',
                'div[role="textbox"]'
            ]
            
            message_input = None
            for selector in input_selectors:
                message_input = await page.query_selector(selector)
                if message_input:
                    log_console(f"[{task_id}] ✅ Found message input with: {selector}")
                    break
            
            if not message_input:
                log_console(f"[{task_id}] ❌ Could not find message input")
                # Take screenshot for debugging
                try:
                    await page.screenshot(path=f"/tmp/error_{task_id}.png")
                    log_console(f"[{task_id}] 📸 Screenshot saved to /tmp/error_{task_id}.png")
                except:
                    pass
                await browser.close()
                return False
            
            # Type and send message
            await message_input.click()
            await page.wait_for_timeout(1000)
            await message_input.fill('')
            await page.wait_for_timeout(500)
            
            # Type message character by character for realism
            for char in message:
                await message_input.press(char)
                await page.wait_for_timeout(random.randint(50, 150))
            
            await page.wait_for_timeout(1000)
            
            # Press Enter to send
            await message_input.press('Enter')
            log_console(f"[{task_id}] ✅ Message sent!")
            
            # Wait for send to complete
            await page.wait_for_timeout(3000)
            
            await browser.close()
            return True
            
    except Exception as e:
        log_console(f"[{task_id}] ❌ Error: {str(e)}")
        return False

def run_async_task(coro):
    """Run async task in background thread"""
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        return loop.run_until_complete(coro)
    except Exception as e:
        log_console(f"Async task error: {e}")
        return False
    finally:
        loop.close()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/status')
def api_status():
    return jsonify({
        'playwright': PLAYWRIGHT_AVAILABLE,
        'browser': BROWSER_INSTALLED,
        'active_tasks': sum(1 for t in tasks_data.values() if t.get('active', False)),
        'total_tasks': len(tasks_data),
        'logs_count': len(livelogs)
    })

@app.route('/api/logs')
def api_logs():
    return jsonify({'logs': livelogs[-100:]})

@app.route('/api/start', methods=['POST'])
def api_start():
    global PLAYWRIGHT_AVAILABLE, BROWSER_INSTALLED
    
    # Auto-install if needed
    if not PLAYWRIGHT_AVAILABLE or not BROWSER_INSTALLED:
        log_console("🔄 Auto-installing dependencies...")
        success = install_playwright_and_browser()
        if not success:
            return jsonify({'success': False, 'message': 'Installation failed'})
    
    # Get input data
    cookies_list = get_input_data(request, 'cookies')
    messages_list = get_input_data(request, 'messages')
    conversations_list = get_input_data(request, 'conversations')
    
    if not cookies_list:
        return jsonify({'success': False, 'message': 'No cookies provided'})
    if not messages_list:
        return jsonify({'success': False, 'message': 'No messages provided'})
    if not conversations_list:
        return jsonify({'success': False, 'message': 'No conversations provided'})
    
    # Create task
    task_id = f"task_{int(time.time())}_{random.randint(1000, 9999)}"
    
    tasks_data[task_id] = {
        'cookies': cookies_list,
        'messages': messages_list,
        'conversations': conversations_list,
        'current_index': 0,
        'active': True,
        'success_count': 0,
        'total_count': len(messages_list) * len(conversations_list) * len(cookies_list),
        'start_time': time.time()
    }
    
    def task_worker():
        task = tasks_data[task_id]
        
        while task['active'] and task['current_index'] < task['total_count']:
            try:
                # Calculate indices
                msg_idx = task['current_index'] % len(task['messages'])
                conv_idx = (task['current_index'] // len(task['messages'])) % len(task['conversations'])
                cookie_idx = (task['current_index'] // (len(task['messages']) * len(task['conversations']))) % len(task['cookies'])
                
                if cookie_idx >= len(task['cookies']):
                    break
                
                message = task['messages'][msg_idx]
                conversation = task['conversations'][conv_idx]
                cookie_input = task['cookies'][cookie_idx]
                
                # Enhance message
                enhanced_msg = enhance_message(message)
                
                # Parse cookies
                cookies = parse_cookies(cookie_input)
                
                if not cookies:
                    log_console(f"[{task_id}] ❌ No valid cookies parsed")
                    task['current_index'] += 1
                    continue
                
                # Send message
                log_console(f"[{task_id}] Sending: '{enhanced_msg}' → {conversation}")
                
                success = run_async_task(
                    send_facebook_message_playwright(cookies, conversation, enhanced_msg, task_id)
                )
                
                if success:
                    task['success_count'] += 1
                    log_console(f"[{task_id}] ✅ Success! Total: {task['success_count']}")
                else:
                    log_console(f"[{task_id}] ❌ Failed to send message")
                
                task['current_index'] += 1
                
                # Random delay between messages (3-8 seconds)
                delay = random.uniform(3, 8)
                time.sleep(delay)
                
            except Exception as e:
                log_console(f"[{task_id}] ❌ Worker error: {e}")
                task['current_index'] += 1
                time.sleep(2)
        
        task['active'] = False
        log_console(f"[{task_id}] 🏁 Task completed! Success: {task['success_count']}/{task['total_count']}")
    
    # Start worker thread
    thread = threading.Thread(target=task_worker, daemon=True)
    thread.start()
    
    return jsonify({
        'success': True, 
        'task_id': task_id,
        'message': f'Task {task_id} started successfully!'
    })

@app.route('/api/stop/<task_id>', methods=['POST'])
def api_stop(task_id):
    if task_id in tasks_data:
        tasks_data[task_id]['active'] = False
        return jsonify({'success': True, 'message': f'Task {task_id} stopped'})
    return jsonify({'success': False, 'message': 'Task not found'})

@app.route('/api/tasks')
def api_tasks():
    task_list = []
    for task_id, task in tasks_data.items():
        task_list.append({
            'id': task_id,
            'active': task.get('active', False),
            'success_count': task.get('success_count', 0),
            'total_count': task.get('total_count', 0),
            'current_index': task.get('current_index', 0),
            'progress': min(100, (task.get('current_index', 0) / task.get('total_count', 1)) * 100)
        })
    return jsonify({'tasks': task_list})

def init_app():
    """Initialize the application"""
    log_console("🚀 Neural Messenger 2030 Initializing...")
    log_console("📦 Checking dependencies...")
    
    # Try to import playwright
    try:
        from playwright.async_api import async_playwright
        global PLAYWRIGHT_AVAILABLE
        PLAYWRIGHT_AVAILABLE = True
        log_console("✅ Playwright is available")
    except ImportError:
        log_console("⚠️ Playwright not installed, will auto-install on first use")
    
    # Check if browser is installed
    try:
        subprocess.run([sys.executable, "-m", "playwright", "list-browsers"], 
                      capture_output=True, timeout=30)
        global BROWSER_INSTALLED
        BROWSER_INSTALLED = True
        log_console("✅ Browser is installed")
    except:
        log_console("⚠️ Browser not installed, will auto-install on first use")

# Initialize the app
init_app()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))  # Ensure this is 10000
    log_console(f"🌐 Starting server on port {port}...")
    app.run(host='0.0.0.0', port=port, debug=False)
