import requests
import json
import threading
import time
import sys

RED = '\033[91m'
GREEN = '\033[92m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
WHITE = '\033[97m'
CYAN = '\033[96m'
MAGENTA = '\033[95m'
RESET = '\033[0m'
BOLD = '\033[1m'

def current_time_hour():
    return time.strftime("%H:%M:%S")

def print_title():
    title = f"""
{CYAN}{BOLD}
╔════════════════════════════════════════════════════════════╗
║               Discord Webhook Spammer                      ║
║                   By Minecraft Game                        ║
╚════════════════════════════════════════════════════════════╝
{RESET}
    """
    print(title)

def check_webhook(webhook_url):
    if not webhook_url.startswith("https://discord.com/api/webhooks/"):
        return False
    try:
        response = requests.get(webhook_url, timeout=5)
        return response.status_code == 200
    except:
        return False

def error_webhook():
    print(f"\n{RED}[{current_time_hour()}]{RESET} {RED}[✗]{RESET} Invalid webhook URL!")
    print(f"{RED}[{current_time_hour()}]{RESET} {RED}[✗]{RESET} Webhook URL should start with: https://discord.com/api/webhooks/")
    sys.exit(1)

def error_number():
    print(f"\n{RED}[{current_time_hour()}]{RESET} {RED}[✗]{RESET} Invalid number! Please enter a valid integer.")
    sys.exit(1)

def error_module(e):
    print(f"\n{RED}[{current_time_hour()}]{RESET} {RED}[✗]{RESET} Missing module: {str(e)}")
    print(f"{YELLOW}[{current_time_hour()}]{RESET} {YELLOW}[!]{RESET} Install missing modules with: pip install requests")
    sys.exit(1)

def error_general(e):
    print(f"\n{RED}[{current_time_hour()}]{RESET} {RED}[✗]{RESET} Error: {str(e)}")
    sys.exit(1)

class WebhookSpammer:
    def __init__(self):
        self.sent_count = 0
        self.failed_count = 0
        self.running = True
        self.lock = threading.Lock()
        
    def send_webhook(self, webhook_url, message, thread_id):
        headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        payload = {
            'content': message,
            'username': "Minecraft Game",
            'avatar_url': "https://cdn.discordapp.com/icons/1312735304704327750/d5db6e1860dc98cfd7e9736afea035b9.png"
        }
        
        try:
            response = requests.post(
                webhook_url, 
                headers=headers, 
                data=json.dumps(payload),
                timeout=10
            )
            
            if response.status_code == 204:
                with self.lock:
                    self.sent_count += 1
                    total_sent = self.sent_count
                print(f"{GREEN}[{current_time_hour()}]{RESET} {GREEN}[✓]{RESET} Thread-{thread_id}: Message sent! (Total: {total_sent})")
                return True
            elif response.status_code == 429:
                retry_after = response.json().get('retry_after', 1)
                print(f"{YELLOW}[{current_time_hour()}]{RESET} {YELLOW}[!]{RESET} Thread-{thread_id}: Rate limited. Waiting {retry_after} seconds...")
                time.sleep(retry_after)
                return False
            else:
                with self.lock:
                    self.failed_count += 1
                print(f"{RED}[{current_time_hour()}]{RESET} {RED}[✗]{RESET} Thread-{thread_id}: Failed with status {response.status_code}")
                return False
                
        except requests.exceptions.RequestException as e:
            with self.lock:
                self.failed_count += 1
            print(f"{RED}[{current_time_hour()}]{RESET} {RED}[✗]{RESET} Thread-{thread_id}: Connection error - {str(e)[:50]}")
            return False
    
    def worker(self, webhook_url, message, thread_id, delay=0):
        while self.running:
            success = self.send_webhook(webhook_url, message, thread_id)
            if success and delay > 0:
                time.sleep(delay)
    
    def start_spamming(self, webhook_url, message, threads_number, delay=0):
        threads = []
        
        print(f"\n{BLUE}[{current_time_hour()}]{RESET} {BLUE}[i]{RESET} Starting spam with {threads_number} threads...")
        print(f"{BLUE}[{current_time_hour()}]{RESET} {BLUE}[i]{RESET} Message: {WHITE}{message}{RESET}")
        print(f"{BLUE}[{current_time_hour()}]{RESET} {BLUE}[i]{RESET} Press Ctrl+C to stop\n")
        
        try:
            for i in range(threads_number):
                thread = threading.Thread(
                    target=self.worker,
                    args=(webhook_url, message, i+1, delay),
                    daemon=True
                )
                threads.append(thread)
                thread.start()
                time.sleep(0.01)
            
            while self.running:
                time.sleep(1)
                
        except KeyboardInterrupt:
            print(f"\n{YELLOW}[{current_time_hour()}]{RESET} {YELLOW}[!]{RESET} Stopping spammer...")
            self.running = False
            
            for thread in threads:
                thread.join(timeout=2)
            
            self.print_summary()
    
    def print_summary(self):
        total = self.sent_count + self.failed_count
        
        print(f"\n{CYAN}{'='*60}{RESET}")
        print(f"{BOLD}{WHITE}SPAM SESSION SUMMARY{RESET}")
        print(f"{CYAN}{'='*60}{RESET}")
        print(f"{GREEN}[✓]{RESET} Messages sent: {GREEN}{self.sent_count}{RESET}")
        print(f"{RED}[✗]{RESET} Messages failed: {RED}{self.failed_count}{RESET}")
        print(f"{BLUE}[i]{RESET} Total attempts: {BLUE}{total}{RESET}")
        
        if total > 0:
            success_rate = (self.sent_count / total) * 100
            print(f"{YELLOW}[!]{RESET} Success rate: {YELLOW}{success_rate:.2f}%{RESET}")
        
        print(f"{CYAN}{'='*60}{RESET}")

def main():
    print_title()
    
    try:
        webhook_url = input(f"{CYAN}[{current_time_hour()}]{RESET} {CYAN}[?]{RESET} Webhook URL -> {WHITE}")
        
        if not check_webhook(webhook_url):
            error_webhook()
        
        message = input(f"{CYAN}[{current_time_hour()}]{RESET} {CYAN}[?]{RESET} Message -> {WHITE}")
        
        try:
            threads_input = input(f"{CYAN}[{current_time_hour()}]{RESET} {CYAN}[?]{RESET} Threads Number (1-1000) -> {WHITE}")
            threads_number = int(threads_input)
            
            if threads_number < 1:
                threads_number = 1
            elif threads_number > 1000:
                threads_number = 1000
                print(f"{YELLOW}[{current_time_hour()}]{RESET} {YELLOW}[!]{RESET} Thread number set to maximum 1000")
                
        except ValueError:
            error_number()
        
        delay = 0
        try:
            delay_input = input(f"{CYAN}[{current_time_hour()}]{RESET} {CYAN}[?]{RESET} Delay between messages in seconds (0 for no delay) -> {WHITE}")
            delay = float(delay_input)
            if delay < 0:
                delay = 0
        except:
            delay = 0
        
        spammer = WebhookSpammer()
        spammer.start_spamming(webhook_url, message, threads_number, delay)
        
    except KeyboardInterrupt:
        print(f"\n{YELLOW}[{current_time_hour()}]{RESET} {YELLOW}[!]{RESET} Program interrupted by user.")
        sys.exit(0)
    except Exception as e:
        error_general(e)

if __name__ == "__main__":
    try:
        import requests
    except ImportError as e:
        print(f"{RED}Error: Missing required module: {str(e)}{RESET}")
        print(f"{YELLOW}Install with: pip install requests{RESET}")
        sys.exit(1)
    
    main()