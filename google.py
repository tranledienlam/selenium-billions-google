#version browser_automation 04/04/2025
import argparse
from selenium.webdriver.common.by import By

from browser_automation import BrowserManager, Node
from utils import Utility

class Auto:
    def __init__(self, node: Node, profile: dict) -> None:
        self.driver = node._driver
        self.node = node
        self.profile_name = profile.get('profile_name')
        self.email = profile.get('email')
        self.password = profile.get('password')

    def sign_in_google(self):
        '''Thực hiện đăng nhập Google sau khi click nút Sign in with Google trên trang dự án'''
            
        # Chuyển sang tab xác nhận Google
        if not self.node.switch_tab('https://accounts.google.com'):
            self.node.snapshot('Không chuyển được trang xác nhận đăng nhập Google')
            return False
            
        # Chọn email
        if not self.node.find_and_click(By.XPATH, f'//div[contains(text(),"{self.email}")]'):
            self.node.snapshot('Không tìm thấy email trong danh sách email')
            return False
            
        # Click nút Tiếp tục/Continue
        if not self.node.find_and_click(By.XPATH, '//div[div[div[div[button]]]]//div[2]//button'):
            self.node.snapshot('Không tìm thấy nút Tiếp tục/Continue')
            return False

        return True
    
    def _run(self):
        '''Thực hiện đăng nhập tài khoản Google'''
        self.node.go_to('https://accounts.google.com/signin')
        
        # Đợi và kiểm tra xem đã đăng nhập chưa bằng cách tìm avatar hoặc email hiển thị
        if self.node.find(By.CSS_SELECTOR, '[aria-label*="@gmail.com"]'):
            self.node.log('✅ Đã đăng nhập Google')
            return True
            
        # Nếu chưa đăng nhập, thực hiện đăng nhập
        self.node.log('⚠️ Chưa đăng nhập Google, đang thực hiện đăng nhập...')
        
        if not self.password:
            self.node.snapshot('⚠️ không có mật khẩu Google, không thực hiện đăng nhập')
            return True
        
        # Nhập email
        if not self.node.find_and_input(By.CSS_SELECTOR, 'input[type="email"]', self.email, None, 0.1):
            self.node.snapshot('Không tìm thấy ô nhập email')
            return False
            
        # Click nút Next
        if not self.node.press_key('Enter'):
            self.node.snapshot('Không thể nhấn nút Enter')
            return False
            
        # Đợi và nhập mật khẩu
        if not self.node.find_and_input(By.CSS_SELECTOR, 'input[type="password"]', self.password, None, 0.1):
            self.node.snapshot('Không tìm thấy ô nhập mật khẩu')
            return False
            
        # Click nút Next
        if not self.node.press_key('Enter'):
            self.node.snapshot('Không thể nhấn nút Enter')
            return False
        
        # di chuyển đến trang đăng nhập và kiểm tra lại
        self.node.go_to('https://accounts.google.com/signin')
        # Thỉnh thoảng nó sẽ hỏi đoạn này passkeys
        # if self.node.find(By.XPATH, '//div[text()="With passkeys, your device will simply ask you for your Windows PIN or biometric and let Google know it\'s really you signing in"]', timeout=15):
        #     self.node.log('🔄 Đang thực hiện xác thực bằng passkey...')
        #     if not self.node.find_and_click(By.XPATH, '//button[text()="Skip"]'):
        #         self.node.snapshot('Không tìm thấy nút "Skip"')
        #         return

        # Đợi và kiểm tra đăng nhập thành công
        if self.node.find(By.CSS_SELECTOR, '[aria-label*="@gmail.com"]'):
            self.node.log('✅ Đăng nhập Google thành công')
        else:
            self.node.snapshot('Không thể xác nhận đăng nhập thành công')
            return False
        
        return True
class Setup:
    def __init__(self, node: Node, profile) -> None:
        self.node = node
        self.profile = profile
        
    def _run(self):
        # Kiểm tra đăng nhập Google
        self.node.go_to('https://accounts.google.com/signin')

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
    browser_manager.run_terminal(
        profiles=profiles,
        max_concurrent_profiles=1,
        block_media=True,
        auto=args.auto,
        headless=args.headless,
        disable_gpu=args.disable_gpu,
    )