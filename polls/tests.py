from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.contrib.auth.models import User
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException

class MySeleniumTests(StaticLiveServerTestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        opts = Options()
        opts.add_argument('--headless')  # Requerido por GitHub Actions
        opts.add_argument('--no-sandbox')
        opts.add_argument('--disable-dev-shm-usage')
        cls.selenium = webdriver.Chrome(options=opts)
        cls.selenium.implicitly_wait(5)
        
        # Superusuario de pruebas obligatorio[cite: 2]
        user = User.objects.create_user("isard", "isard@isardvdi.com", "pirineus")
        user.is_superuser = True
        user.is_staff = True
        user.save()

    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        super().tearDownClass()

    def test_admin_login(self):
        driver = self.selenium
        driver.get(f"{self.live_server_url}/admin/login/")

        # Inicio de sesión automatizado con Selenium
        username_input = driver.find_element(By.NAME, "username")
        password_input = driver.find_element(By.NAME, "password")
        username_input.send_keys("isard")
        password_input.send_keys("pirineus")
        driver.find_element(By.XPATH, "//input[@type='submit']").click()

        # Verificación de inicio de sesión exitoso
        self.assertIn("Site administration", driver.page_source)
