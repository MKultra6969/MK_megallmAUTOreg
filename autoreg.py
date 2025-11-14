# +═════════════════════════════════════════════════════════════════════════+
# ║      ███▄ ▄███▓ ██ ▄█▀ █    ██  ██▓    ▄▄▄█████▓ ██▀███   ▄▄▄           ║
# ║     ▓██▒▀█▀ ██▒ ██▄█▒  ██  ▓██▒▓██▒    ▓  ██▒ ▓▒▓██ ▒ ██▒▒████▄         ║
# ║     ▓██    ▓██░▓███▄░ ▓██  ▒██░▒██░    ▒ ▓██░ ▒░▓██ ░▄█ ▒▒██  ▀█▄       ║
# ║     ▒██    ▒██ ▓██ █▄ ▓▓█  ░██░▒██░    ░ ▓██▓ ░ ▒██▀▀█▄  ░██▄▄▄▄██      ║
# ║     ▒██▒   ░██▒▒██▒ █▄▒▒█████▓ ░██████▒  ▒██▒ ░ ░██▓ ▒██▒ ▓█   ▓██▒     ║
# ║     ░ ▒░   ░  ░▒ ▒▒ ▓▒░▒▓▒ ▒ ▒ ░ ▒░▓  ░  ▒ ░░   ░ ▒▓ ░▒▓░ ▒▒   ▓▒█░     ║
# ║     ░  ░      ░░ ░▒ ▒░░░▒░ ░ ░ ░ ░ ▒  ░    ░      ░▒ ░ ▒░  ▒   ▒▒ ░     ║
# ║     ░      ░   ░ ░░ ░  ░░░ ░ ░   ░ ░     ░        ░░   ░   ░   ▒        ║
# ║            ░   ░  ░      ░         ░  ░            ░           ░  ░     ║
# ║                                                                         ║
# +═════════════════════════════════════════════════════════════════════════+
# ║                               by MKultra69                              ║
# +═════════════════════════════════════════════════════════════════════════+
# +═════════════════════════════════════════════════════════════════════════+
# ║                      https://github.com/MKultra6969                     ║
# +═════════════════════════════════════════════════════════════════════════+
# +═════════════════════════════════════════════════════════════════════════+
# ║                                  mk69.su                                ║
# +═════════════════════════════════════════════════════════════════════════+


import time
import random
import string
import re
import requests
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, ElementClickInterceptedException
from selenium.webdriver.common.action_chains import ActionChains
from faker import Faker
from dotenv import load_dotenv
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock

load_dotenv()

file_lock = Lock()

class MegaLLMRegistration:
    def __init__(self, session_id=None):
        self.base_url = "https://megallm.io/auth/signup"
        self.mail_api_base = "https://api.mail.tm"
        self.referral_code = os.getenv("REFERRAL_CODE", "")
        self.fake = Faker()
        self.email = None
        self.password = None
        self.token = None
        self.account_id = None
        self.session_id = session_id

    def log(self, message):
        prefix = f"[Сессия {self.session_id}]" if self.session_id else ""
        print(f"{prefix} {message}")

    def generate_password(self):
        chars = string.ascii_letters + string.digits
        random_part = ''.join(random.choices(chars, k=8))
        return f"1!Aa{random_part}"

    def create_temp_email(self):
        try:
            response = requests.get(f"{self.mail_api_base}/domains")
            domains = response.json()["hydra:member"]
            domain = domains[0]["domain"]
            
            username = ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))
            self.email = f"{username}@{domain}"
            self.password = self.generate_password()
            
            account_data = {
                "address": self.email,
                "password": self.password
            }
            
            response = requests.post(f"{self.mail_api_base}/accounts", json=account_data)
            
            if response.status_code == 201:
                account_info = response.json()
                self.account_id = account_info["id"]
                
                token_response = requests.post(
                    f"{self.mail_api_base}/token",
                    json={"address": self.email, "password": self.password}
                )
                self.token = token_response.json()["token"]
                self.log(f"✓ Создан временный email: {self.email}")
                return True
            else:
                self.log(f"✗ Ошибка создания email: {response.status_code}")
                return False
                
        except Exception as e:
            self.log(f"✗ Ошибка при создании временной почты: {e}")
            return False

    def wait_for_verification_code(self, timeout=120):
        headers = {"Authorization": f"Bearer {self.token}"}
        start_time = time.time()
        
        self.log("⏳ Ожидание письма с кодом верификации...")
        
        while time.time() - start_time < timeout:
            try:
                response = requests.get(f"{self.mail_api_base}/messages", headers=headers)
                
                if response.status_code == 200:
                    messages = response.json()["hydra:member"]
                    
                    if messages:
                        message_id = messages[0]["id"]
                        message_response = requests.get(
                            f"{self.mail_api_base}/messages/{message_id}",
                            headers=headers
                        )
                        
                        if message_response.status_code == 200:
                            message_data = message_response.json()
                            text = message_data.get("text", "")
                            html = message_data.get("html", [""])[0] if message_data.get("html") else ""
                            content = text + " " + html
                            
                            code_match = re.search(r'\b(\d{6})\b', content)
                            if code_match:
                                code = code_match.group(1)
                                self.log(f"✓ Получен код верификации: {code}")
                                return code
                
                time.sleep(5)
                
            except Exception as e:
                self.log(f"✗ Ошибка при получении писем: {e}")
                time.sleep(5)
        
        self.log("✗ Время ожидания кода истекло")
        return None

    def close_overlays(self, driver):
        try:
            overlays = [
                "//button[contains(text(), 'Accept')]",
                "//button[contains(text(), 'Close')]",
                "//button[contains(text(), 'Dismiss')]",
                "//button[contains(@class, 'close')]",
                "//div[contains(@class, 'modal')]//button",
                "//div[contains(@class, 'cookie')]//button"
            ]
            
            for overlay_xpath in overlays:
                try:
                    overlay_btn = driver.find_element(By.XPATH, overlay_xpath)
                    overlay_btn.click()
                    time.sleep(1)
                    self.log("✓ Закрыт overlay элемент")
                except:
                    pass
        except:
            pass

    def click_element(self, driver, element):
        try:
            wait = WebDriverWait(driver, 10)
            wait.until(EC.element_to_be_clickable(element))
            element.click()
            self.log("✓ Клик выполнен (стандартный метод)")
            return True
        except ElementClickInterceptedException:
            self.log("⚠️ Элемент перекрыт, пробуем альтернативные методы...")
            
            try:
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
                time.sleep(1)
                element.click()
                self.log("✓ Клик выполнен (после прокрутки)")
                return True
            except:
                pass
            
            try:
                driver.execute_script("arguments[0].click();", element)
                self.log("✓ Клик выполнен (JavaScript)")
                return True
            except:
                pass
            
            try:
                actions = ActionChains(driver)
                actions.move_to_element(element).click().perform()
                self.log("✓ Клик выполнен (ActionChains)")
                return True
            except:
                pass
            
            self.log("✗ Все методы клика не сработали")
            return False
        except Exception as e:
            self.log(f"✗ Ошибка при клике: {e}")
            return False

    def check_for_error_message(self, driver):
        try:
            error_texts = ["Registration failed", "Please try again", "Error", "Failed"]
            for error_text in error_texts:
                try:
                    error_element = driver.find_element(By.XPATH, f"//*[contains(text(), '{error_text}')]")
                    if error_element.is_displayed():
                        self.log(f"⚠️ Обнаружена ошибка: {error_text}")
                        return True
                except:
                    pass
            return False
        except:
            return False

    def is_registration_successful(self, driver):
        current_url = driver.current_url.lower()
        
        success_patterns = ["dashboard", "home", "overview", "profile"]
        pending_patterns = ["signup", "verify", "verification", "register"]
        
        for pattern in success_patterns:
            if pattern in current_url:
                return True, "success"
        
        for pattern in pending_patterns:
            if pattern in current_url:
                return False, "pending"
        
        return True, "unknown"

    def submit_registration_with_infinite_retry(self, driver, wait):
        attempt = 0
        backoff_base = 2
        max_backoff = 60
        
        while True:
            attempt += 1
            try:
                self.log(f"🔘 Попытка {attempt}: Нажимаем кнопку Sign Up...")
                
                current_url = driver.current_url
                self.log(f"📍 Текущий URL: {current_url}")
                
                self.close_overlays(driver)
                
                submit_button = driver.find_element(By.XPATH, "//button[@type='submit']")
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", submit_button)
                time.sleep(1)
                
                if not self.click_element(driver, submit_button):
                    self.log(f"✗ Попытка {attempt}: Не удалось нажать кнопку")
                    backoff_delay = min(backoff_base * (2 ** (attempt - 1)), max_backoff)
                    jitter = random.uniform(0, 1)
                    total_delay = backoff_delay + jitter
                    self.log(f"⏳ Ожидание {total_delay:.2f} секунд перед следующей попыткой...")
                    time.sleep(total_delay)
                    continue
                
                self.log("⏳ Ожидаем переход на страницу верификации...")
                
                try:
                    WebDriverWait(driver, 10).until(EC.url_changes(current_url))
                    new_url = driver.current_url
                    self.log(f"✓ URL изменился: {new_url}")
                    
                    if "signup" not in new_url.lower():
                        self.log("✓ Успешный переход на страницу верификации!")
                        return True
                    else:
                        self.log("⚠️ Все еще на странице регистрации")
                        
                except TimeoutException:
                    self.log("⚠️ URL не изменился, проверяем наличие ошибок...")
                    time.sleep(2)
                    
                    if self.check_for_error_message(driver):
                        backoff_delay = min(backoff_base * (2 ** (attempt - 1)), max_backoff)
                        jitter = random.uniform(0, 1)
                        total_delay = backoff_delay + jitter
                        self.log(f"🔄 Обнаружена ошибка регистрации, повторная попытка через {total_delay:.2f} секунд...")
                        time.sleep(total_delay)
                        continue
                    else:
                        try:
                            code_input = driver.find_element(
                                By.XPATH,
                                "//input[@type='text' or @type='number' or @inputmode='numeric']"
                            )
                            self.log("✓ Найдены поля для ввода кода верификации!")
                            return True
                        except:
                            self.log("⚠️ Поля для кода не найдены")
                
                backoff_delay = min(backoff_base * (2 ** (attempt - 1)), max_backoff)
                jitter = random.uniform(0, 1)
                total_delay = backoff_delay + jitter
                self.log(f"⏳ Ожидание {total_delay:.2f} секунд перед следующей попыткой...")
                time.sleep(total_delay)
                
            except Exception as e:
                self.log(f"✗ Попытка {attempt} завершилась ошибкой: {e}")
                backoff_delay = min(backoff_base * (2 ** (attempt - 1)), max_backoff)
                jitter = random.uniform(0, 1)
                total_delay = backoff_delay + jitter
                self.log(f"⏳ Ожидание {total_delay:.2f} секунд перед следующей попыткой...")
                time.sleep(total_delay)

    def register(self):
        if not self.create_temp_email():
            return False
        
        options = webdriver.ChromeOptions()
        # options.add_argument('--headless') # Раскомментировать если не хочешь чтоб в ебальник 100 chrome открылось.
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_argument('--start-maximized')
        
        driver = webdriver.Chrome(options=options)
        wait = WebDriverWait(driver, 20)
        
        try:
            self.log(f"🌐 Открываем {self.base_url}")
            driver.get(self.base_url)
            time.sleep(3)
            
            self.close_overlays(driver)
            
            full_name = self.fake.name()
            site_password = self.generate_password()
            
            self.log(f"📝 Заполняем форму регистрации...")
            
            name_field = wait.until(EC.presence_of_element_located((By.NAME, "name")))
            name_field.clear()
            name_field.send_keys(full_name)
            time.sleep(0.5)
            
            email_field = driver.find_element(By.NAME, "email")
            email_field.clear()
            email_field.send_keys(self.email)
            time.sleep(0.5)
            
            password_field = driver.find_element(By.NAME, "password")
            password_field.clear()
            password_field.send_keys(site_password)
            time.sleep(0.5)
            
            confirm_password_field = driver.find_element(By.NAME, "confirmPassword")
            confirm_password_field.clear()
            confirm_password_field.send_keys(site_password)
            time.sleep(0.5)
            
            if self.referral_code:
                try:
                    referral_field = driver.find_element(By.XPATH, "//input[@placeholder='Enter referral code']")
                    referral_field.clear()
                    referral_field.send_keys(self.referral_code)
                    self.log(f"🎟️ Реферальный код: {self.referral_code}")
                    time.sleep(0.5)
                except:
                    self.log("⚠️ Поле реферального кода не найдено")
            
            self.log(f"👤 Имя: {full_name}")
            self.log(f"📧 Email: {self.email}")
            self.log(f"🔑 Пароль: {site_password}")
            
            self.submit_registration_with_infinite_retry(driver, wait)
            
            self.log("✓ Форма отправлена, ожидаем код верификации...")
            time.sleep(3)
            
            verification_code = self.wait_for_verification_code()
            if not verification_code:
                self.log("✗ Не удалось получить код верификации")
                return False
            
            self.log("📨 Вводим код верификации...")
            time.sleep(2)
            
            code_inputs = wait.until(EC.presence_of_all_elements_located(
                (By.XPATH, "//input[@type='text' or @type='number' or @inputmode='numeric']")
            ))
            
            self.log(f"✓ Найдено {len(code_inputs)} полей для ввода кода")
            
            for i, digit in enumerate(verification_code):
                if i < len(code_inputs):
                    code_inputs[i].clear()
                    code_inputs[i].send_keys(digit)
                    time.sleep(0.3)
            
            self.log("✓ Код введен, ожидаем автоматической проверки...")
            time.sleep(5)
            
            try:
                WebDriverWait(driver, 15).until(
                    lambda d: "dashboard" in d.current_url.lower() 
                    or "home" in d.current_url.lower() 
                    or "overview" in d.current_url.lower()
                    or (d.current_url != self.base_url and "verify" not in d.current_url.lower())
                )
                self.log("✓ Обнаружен переход на новую страницу после верификации")
            except TimeoutException:
                self.log("⏳ Дополнительное ожидание завершения верификации...")
                time.sleep(3)
            
            current_url = driver.current_url
            is_success, status = self.is_registration_successful(driver)
            
            self.log(f"📍 Финальный URL: {current_url}")
            self.log(f"📊 Статус регистрации: {status}")
            
            if is_success:
                self.log("🎉 РЕГИСТРАЦИЯ УСПЕШНА!")
                self.log(f"✓ Аккаунт создан: {self.email}")
                self.log(f"✓ Пароль: {site_password}")
                
                with file_lock:
                    with open("accounts.txt", "a", encoding="utf-8") as f:
                        f.write(f"{self.email}:{site_password}\n")
                
                time.sleep(3)
                return True
            else:
                self.log("⚠️ Регистрация не завершена или требуется дополнительная верификация")
                time.sleep(5)
                return False
                
        except TimeoutException:
            self.log("✗ Превышено время ожидания элемента на странице")
            return False
        except Exception as e:
            self.log(f"✗ Ошибка при регистрации: {e}")
            import traceback
            traceback.print_exc()
            return False
        finally:
            driver.quit()


def print_banner():
    banner = """
+═════════════════════════════════════════════════════════════════════════+
║      ███▄ ▄███▓ ██ ▄█▀ █    ██  ██▓    ▄▄▄█████▓ ██▀███   ▄▄▄           ║
║     ▓██▒▀█▀ ██▒ ██▄█▒  ██  ▓██▒▓██▒    ▓  ██▒ ▓▒▓██ ▒ ██▒▒████▄         ║
║     ▓██    ▓██░▓███▄░ ▓██  ▒██░▒██░    ▒ ▓██░ ▒░▓██ ░▄█ ▒▒██  ▀█▄       ║
║     ▒██    ▒██ ▓██ █▄ ▓▓█  ░██░▒██░    ░ ▓██▓ ░ ▒██▀▀█▄  ░██▄▄▄▄██      ║
║     ▒██▒   ░██▒▒██▒ █▄▒▒█████▓ ░██████▒  ▒██▒ ░ ░██▓ ▒██▒ ▓█   ▓██▒     ║
║     ░ ▒░   ░  ░▒ ▒▒ ▓▒░▒▓▒ ▒ ▒ ░ ▒░▓  ░  ▒ ░░   ░ ▒▓ ░▒▓░ ▒▒   ▓▒█░     ║
║     ░  ░      ░░ ░▒ ▒░░░▒░ ░ ░ ░ ░ ▒  ░    ░      ░▒ ░ ▒░  ▒   ▒▒ ░     ║
║     ░      ░   ░ ░░ ░  ░░░ ░ ░   ░ ░     ░        ░░   ░   ░   ▒        ║
║            ░   ░  ░      ░         ░  ░            ░           ░  ░     ║
║                                                                         ║
+═════════════════════════════════════════════════════════════════════════+
║                               MKultra69                                 ║
+═════════════════════════════════════════════════════════════════════════+
                          by mkultra69 WITH HATE TO PEOPLES GFY
                  https://github.com/MKultra6969

"""
    print(banner)



def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')


def print_menu():
    print("\n╔═══════════════════════════════════════════════════════════╗")
    print("║                       ГЛАВНОЕ МЕНЮ                        ║")
    print("╚═══════════════════════════════════════════════════════════╝")
    print("║                                                           ║")
    print("║  [1] Единичный запуск                                     ║")
    print("║  [2] Мульти-запуск (последовательно)                      ║")
    print("║  [3] Параллельный запуск (несколько браузеров)            ║")
    print("║  [4] Задать реферальный код                               ║")
    print("║  [5] Выход                                                ║")
    print("║                                                           ║")
    print("╚═══════════════════════════════════════════════════════════╝")


def set_referral_code():
    print("\n╔═══════════════════════════════════════════════════════════╗")
    print("║              УСТАНОВКА РЕФЕРАЛЬНОГО КОДА                  ║")
    print("╚═══════════════════════════════════════════════════════════╝\n")
    
    current_code = os.getenv("REFERRAL_CODE", "")
    if current_code:
        print(f"Текущий реферальный код: {current_code}")
    else:
        print("Реферальный код не установлен")
    
    new_code = input("\nВведите новый реферальный код (или Enter для отмены): ").strip()
    
    if new_code:
        env_path = ".env"
        env_lines = []
        
        if os.path.exists(env_path):
            with open(env_path, "r", encoding="utf-8") as f:
                env_lines = f.readlines()
        
        updated = False
        for i, line in enumerate(env_lines):
            if line.startswith("REFERRAL_CODE="):
                env_lines[i] = f"REFERRAL_CODE={new_code}\n"
                updated = True
                break
        
        if not updated:
            env_lines.append(f"REFERRAL_CODE={new_code}\n")
        
        with open(env_path, "w", encoding="utf-8") as f:
            f.writelines(env_lines)
        
        load_dotenv(override=True)
        
        print(f"\n✓ Реферальный код успешно установлен: {new_code}")
    else:
        print("\n⚠️ Отменено")
    
    input("\nНажмите Enter для продолжения...")


def single_registration():
    print("\n╔═══════════════════════════════════════════════════════════╗")
    print("║                  ЕДИНИЧНАЯ РЕГИСТРАЦИЯ                     ║")
    print("╚═══════════════════════════════════════════════════════════╝\n")
    
    registration = MegaLLMRegistration(session_id=1)
    
    if registration.register():
        print("\n✅ Регистрация завершена успешно!")
    else:
        print("\n❌ Регистрация завершена с ошибками")
    
    input("\nНажмите Enter для продолжения...")


def multi_registration():
    print("\n╔═══════════════════════════════════════════════════════════╗")
    print("║                     МУЛЬТИ-РЕГИСТРАЦИЯ                     ║")
    print("╚═══════════════════════════════════════════════════════════╝\n")
    
    try:
        count = int(input("Сколько аккаунтов нужно зарегистрировать? "))
        
        if count <= 0:
            print("\n⚠️ Количество должно быть больше 0")
            input("\nНажмите Enter для продолжения...")
            return
        
        print(f"\n🚀 Начинаем регистрацию {count} аккаунтов...\n")
        
        success_count = 0
        failed_count = 0
        
        for i in range(1, count + 1):
            print(f"\n{'='*60}")
            print(f"РЕГИСТРАЦИЯ АККАУНТА {i}/{count}")
            print(f"{'='*60}\n")
            
            registration = MegaLLMRegistration(session_id=i)
            
            if registration.register():
                success_count += 1
                print(f"\n✅ Аккаунт {i}/{count} зарегистрирован успешно!")
            else:
                failed_count += 1
                print(f"\n❌ Аккаунт {i}/{count} - ошибка регистрации")
            
            if i < count:
                print("\n⏳ Пауза 5 секунд перед следующей регистрацией...")
                time.sleep(5)
        
        print(f"\n{'='*60}")
        print(f"ИТОГИ МУЛЬТИ-РЕГИСТРАЦИИ")
        print(f"{'='*60}")
        print(f"✓ Успешно зарегистрировано: {success_count}")
        print(f"✗ Ошибок: {failed_count}")
        print(f"📊 Всего попыток: {count}")
        print(f"{'='*60}\n")
        
    except ValueError:
        print("\n⚠️ Пожалуйста, введите корректное число")
    
    input("\nНажмите Enter для продолжения...")


def parallel_registration():
    print("\n╔═══════════════════════════════════════════════════════════╗")
    print("║              ПАРАЛЛЕЛЬНАЯ РЕГИСТРАЦИЯ                      ║")
    print("╚═══════════════════════════════════════════════════════════╝\n")
    
    try:
        count = int(input("Сколько аккаунтов нужно зарегистрировать параллельно? "))
        
        if count <= 0:
            print("\n⚠️ Количество должно быть больше 0")
            input("\nНажмите Enter для продолжения...")
            return
        
        max_workers = int(input(f"Сколько браузеров запускать одновременно? (рекомендуется 2-5): "))
        
        if max_workers <= 0:
            print("\n⚠️ Количество браузеров должно быть больше 0")
            input("\nНажмите Enter для продолжения...")
            return
        
        print(f"\n🚀 Начинаем параллельную регистрацию {count} аккаунтов ({max_workers} одновременно)...\n")
        
        success_count = 0
        failed_count = 0
        
        def register_account(session_id):
            registration = MegaLLMRegistration(session_id=session_id)
            return registration.register()
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {executor.submit(register_account, i): i for i in range(1, count + 1)}
            
            for future in as_completed(futures):
                session_id = futures[future]
                try:
                    result = future.result()
                    if result:
                        success_count += 1
                        print(f"\n✅ Сессия {session_id} - регистрация успешна!")
                    else:
                        failed_count += 1
                        print(f"\n❌ Сессия {session_id} - ошибка регистрации")
                except Exception as e:
                    failed_count += 1
                    print(f"\n❌ Сессия {session_id} - критическая ошибка: {e}")
        
        print(f"\n{'='*60}")
        print(f"ИТОГИ ПАРАЛЛЕЛЬНОЙ РЕГИСТРАЦИИ")
        print(f"{'='*60}")
        print(f"✓ Успешно зарегистрировано: {success_count}")
        print(f"✗ Ошибок: {failed_count}")
        print(f"📊 Всего попыток: {count}")
        print(f"⚡ Одновременных сессий: {max_workers}")
        print(f"{'='*60}\n")
        
    except ValueError:
        print("\n⚠️ Пожалуйста, введите корректное число")
    
    input("\nНажмите Enter для продолжения...")


def main():
    while True:
        clear_screen()
        print_banner()
        print_menu()
        
        choice = input("\nВыберите опцию [1-5]: ").strip()
        
        if choice == "1":
            clear_screen()
            print_banner()
            single_registration()
        elif choice == "2":
            clear_screen()
            print_banner()
            multi_registration()
        elif choice == "3":
            clear_screen()
            print_banner()
            parallel_registration()
        elif choice == "4":
            clear_screen()
            print_banner()
            set_referral_code()
        elif choice == "5":
            clear_screen()
            print_banner()
            print("\n👋 Спасибо за использование MKultra AutoReg!\n")
            break
        else:
            print("\n⚠️ Неверный выбор. Пожалуйста, выберите опцию от 1 до 5.")
            time.sleep(2)


if __name__ == "__main__":
    main()



# +═════════════════════════════════════════════════════════════════════════+
# ║      ███▄ ▄███▓ ██ ▄█▀ █    ██  ██▓    ▄▄▄█████▓ ██▀███   ▄▄▄           ║
# ║     ▓██▒▀█▀ ██▒ ██▄█▒  ██  ▓██▒▓██▒    ▓  ██▒ ▓▒▓██ ▒ ██▒▒████▄         ║
# ║     ▓██    ▓██░▓███▄░ ▓██  ▒██░▒██░    ▒ ▓██░ ▒░▓██ ░▄█ ▒▒██  ▀█▄       ║
# ║     ▒██    ▒██ ▓██ █▄ ▓▓█  ░██░▒██░    ░ ▓██▓ ░ ▒██▀▀█▄  ░██▄▄▄▄██      ║
# ║     ▒██▒   ░██▒▒██▒ █▄▒▒█████▓ ░██████▒  ▒██▒ ░ ░██▓ ▒██▒ ▓█   ▓██▒     ║
# ║     ░ ▒░   ░  ░▒ ▒▒ ▓▒░▒▓▒ ▒ ▒ ░ ▒░▓  ░  ▒ ░░   ░ ▒▓ ░▒▓░ ▒▒   ▓▒█░     ║
# ║     ░  ░      ░░ ░▒ ▒░░░▒░ ░ ░ ░ ░ ▒  ░    ░      ░▒ ░ ▒░  ▒   ▒▒ ░     ║
# ║     ░      ░   ░ ░░ ░  ░░░ ░ ░   ░ ░     ░        ░░   ░   ░   ▒        ║
# ║            ░   ░  ░      ░         ░  ░            ░           ░  ░     ║
# ║                                                                         ║
# +═════════════════════════════════════════════════════════════════════════+
# ║                               by MKultra69                              ║
# +═════════════════════════════════════════════════════════════════════════+
# +═════════════════════════════════════════════════════════════════════════+
# ║                      https://github.com/MKultra6969                     ║
# +═════════════════════════════════════════════════════════════════════════+
# +═════════════════════════════════════════════════════════════════════════+
# ║                                  mk69.su                                ║
# +═════════════════════════════════════════════════════════════════════════+