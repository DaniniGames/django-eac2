from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.contrib.auth.models import User
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class MySeleniumTests(StaticLiveServerTestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        opts = Options()
        opts.add_argument('--headless')  # Mode invisible obligatori per a GitHub Actions
        opts.add_argument('--no-sandbox')
        opts.add_argument('--disable-dev-shm-usage')
        cls.selenium = webdriver.Chrome(options=opts)
        cls.selenium.implicitly_wait(10)
        
        # 1. Superusuari inicial de l'entorn IsardVDI
        user_isard = User.objects.create_user("isard", "isard@isardvdi.com", "pirineus")
        user_isard.is_superuser = True
        user_isard.is_staff = True
        user_isard.save()

        # 2. Usuari staff personalitzat
        user_staff = User.objects.create_user("1234567", "staff@isardvdi.com", "SeguraPass2026!")
        user_staff.is_staff = True
        user_staff.save()

    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        super().tearDownClass()

    def test_staff_password_change_restrictions(self):
        driver = self.selenium
        wait = WebDriverWait(driver, 10)

        # 1. Iniciar sessió al panell d'administració amb l'usuari Staff ("1234567")
        driver.get(f"{self.live_server_url}/admin/login/")
        wait.until(EC.presence_of_element_located((By.NAME, "username"))).send_keys("1234567")
        driver.find_element(By.NAME, "password").send_keys("SeguraPass2026!")
        driver.find_element(By.XPATH, "//input[@type='submit']").click()

        # Confirmar que la sessió s'ha iniciat correctament
        wait.until(EC.presence_of_element_located((By.ID, "user-tools")))

        # 2. Accedir al formulari de canvi de contrasenya de l'usuari staff
        driver.get(f"{self.live_server_url}/admin/password_change/")

        # 3. Intentar canviar la clau introduint "1234567" per activar les 4 restriccions
        wait.until(EC.presence_of_element_located((By.NAME, "old_password"))).send_keys("SeguraPass2026!")
        driver.find_element(By.NAME, "new_password1").send_keys("1234567")
        driver.find_element(By.NAME, "new_password2").send_keys("1234567")
        driver.find_element(By.XPATH, "//input[@type='submit']").click()

        # 4. Esperar la resposta de Django i comprovar els 4 missatges d'error al codi HTML
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "errorlist")))
        page_source = driver.page_source.lower()

        # Restricció 1: Longitud mínima (mínim 8 caràcters)
        self.assertTrue("8" in page_source or "short" in page_source or "curta" in page_source or "corta" in page_source,
                        "Error: No s'ha trobat la restricció de longitud mínima")

        # Restricció 2: Similaritat amb el nom d'usuari
        self.assertTrue("similar" in page_source,
                        "Error: No s'ha trobat la restricció de similaritat")

        # Restricció 3: Contrasenya d'ús comú
        self.assertTrue("common" in page_source or "común" in page_source or "comuna" in page_source,
                        "Error: No s'ha trobat la restricció de clau comuna")

        # Restricció 4: Enterament numèrica
        self.assertTrue("numeric" in page_source or "numérica" in page_source or "numèrica" in page_source,
                        "Error: No s'ha trobat la restricció de clau enterament numèrica")
