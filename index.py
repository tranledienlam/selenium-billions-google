import argparse
from selenium.webdriver.common.by import By

from browser_automation import BrowserManager, Node
from utils import Utility
from googl import Auto as GoogleAuto, Setup as GoogleSetup

class Auto:
    def __init__(self, node: Node, profile: dict) -> None:
        self.driver = node._driver
        self.node = node
        self.profile_name = profile.get('profile_name')
        self.email = profile.get('email')
        self.google = GoogleAuto(node, profile)
    
    def _run(self):
        if not self.google._run():
            return False
        self.node.go_to('https://signup.billions.network/?rc=WGIG2OST', 'get')

        # Kiểm tra xem trang đăng nhập hay không
        text_h2 = self.node.get_text(By.TAG_NAME, 'h2')
        if text_h2.lower() == 'Sign in to Billions'.lower():
            self.node.find_and_click(By.XPATH, '//span[contains(text(),"Accept")]', None, None, 10)
            self.node.log('Cần đăng nhập Google để tiếp tục')
                    # Click vào nút Google để đăng nhập
            self.node.find_and_click(By.XPATH, '//span[contains(text(),"Continue with Google")]')
            
            # Kiểm tra xem có bị reCaptcha không
            if self.node.find(By.XPATH, '//span[contains(text(),"CAPTCHA")]', None, 0, 10):
                self.node.snapshot('⚠️ Phát hiện lỗi reCaptcha')
                return False
            
            # Đăng nhập Google
            self.google.sign_in_google()
        elif text_h2.lower() == "Upcoming rewards".lower():
            text_h1 = self.node.get_text(By.TAG_NAME, 'h1')

        # Check-in
        if 'Level' in text_h2:
            self.node.log('Đang ở Dashboard')
            self.node.find_and_click(By.XPATH, '//span[contains(text(),"Accept")]', None, None, 10)
            self.node.find_and_click(By.XPATH, '//button[contains(text(),"Click & Earn")]', timeout=20)

        else:
            self.node.snapshot(f'Không tìm thấy {text_h1}')
            return False
        
        if self.node.find(By.XPATH, '//span[contains(text(),"Come back in")]'):
            self.node.snapshot('Đã check-in hôm nay')
        else:
            self.node.snapshot('Không thể check-in')
            return False
                
        return True

class Setup:
    def __init__(self, node: Node, profile) -> None:
        self.node = node
        self.profile = profile
        self.google = GoogleSetup(node, profile)

    def _run(self):
        self.google._run()
        self.node.new_tab('https://signup.billions.network/?rc=WGIG2OST')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--auto', action='store_true', help="Chạy ở chế độ tự động")
    parser.add_argument('--headless', action='store_true', help="Chạy trình duyệt ẩn")
    parser.add_argument('--disable-gpu', action='store_true', help="Tắt GPU")
    args = parser.parse_args()

    profiles = Utility.get_data('profile_name', 'email', 'password')
    if not profiles:
        print("Không có dữ liệu để chạy")
        exit()

    browser_manager = BrowserManager(AutoHandlerClass=Auto, SetupHandlerClass=Setup)
    # browser_manager.config_extension('meta-wallet-*.crx')
    # browser_manager.run_browser(profiles[1])
    browser_manager.run_terminal(
        profiles=profiles,
        max_concurrent_profiles=4,
        block_media=False,
        auto=args.auto,
        headless=args.headless,
        disable_gpu=args.disable_gpu,
    )