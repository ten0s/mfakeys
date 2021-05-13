import os
import sys
import argparse
import subprocess
import configparser

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import TimeoutException

# Don't print exception stack trace
sys.tracebacklimit = 0

# TODO: Upgrade to Selenium 4+ and use EC.any_of()
class EC_OR:
   def __init__(self, *args):
      self.ecs = args

   def __call__(self, driver):
      for ec in self.ecs:
         try:
            if ec(driver): return True
         except:
            pass

CONFIG_FILE_NAME = os.getenv("HOME") + "/" + ".mfakeysrc"

DEBUG = 0
try:
  DEBUG = int(os.getenv("DEBUG"))
except:
   pass

def read_config(section, key):
   config = configparser.ConfigParser()
   config.read(CONFIG_FILE_NAME)
   return config.get(section, key)

def get_arg(argsd, name, required):
   arg = argsd[name]
   if arg != "":
      return arg
   try:
      return read_config("default", name)
   except:
      if required:
         raise Exception("argument '" + name + "' is required")
      else:
         return ""

def base_dir():
   try:
      # Under PyInstaler
      return sys._MEIPASS
   except:
      return os.getcwd()

def eprint(*args, **kwargs):
   """ Print to standard error """
   print(*args, file=sys.stderr, **kwargs)

def do_auth(driver, username, password, code):
   # Wait for username form
   WebDriverWait(driver, 60).until(
      EC.element_to_be_clickable((By.ID, "username-submit-button"))
   )
   input =  WebDriverWait(driver, 60).until(
      EC.element_to_be_clickable((By.ID, "awsui-input-0"))
   )
   input.send_keys(username)
   input.submit()

   # Wait for password form
   WebDriverWait(driver, 60).until(
      EC.element_to_be_clickable((By.ID, "password-submit-button"))
   )
   input =  WebDriverWait(driver, 60).until(
      EC.element_to_be_clickable((By.ID, "awsui-input-1"))
   )
   input.send_keys(password)
   input.submit()

   # Wait for MFA code form
   WebDriverWait(driver, 60).until(
      EC.element_to_be_clickable((By.XPATH, "//awsui-button[@data-testid='test-primary-button']/button"))
   )
   input =  WebDriverWait(driver, 60).until(
      EC.element_to_be_clickable((By.ID, "awsui-input-0"))
   )

   if os.path.isfile(os.path.expanduser(code)):
      out = subprocess.check_output([code])
      code = out.split()[0].decode("utf-8")

   input.send_keys(code)
   input.submit()

def do_account(driver, username, password, code, url):
   # If Account ID is not given then print accounts
   list_accounts = False
   if not account:
      list_accounts = True

   # If Profile ID is not given then print account's profiles
   list_profiles = False
   if not profile:
      list_profiles = True

   driver.get(url)
   do_auth(driver, username, password, code)

   # Wait for auth result
   WebDriverWait(driver, 60).until(EC_OR(
      # Some error
      EC.visibility_of_element_located((By.XPATH, "//*[@id='alertFrame']/div/*[normalize-space()]")),
      # Credentials
      EC.element_to_be_clickable((By.XPATH, "//portal-application"))
   ))

   # Some error?
   try:
      alert = driver.find_element_by_xpath("//*[@id='alertFrame']/div/*[normalize-space()]")
      raise Exception(alert.text)
   except NoSuchElementException:
      # If not alert then auth is successful, go to the next page
      pass

   if list_accounts:
      print(driver.find_element_by_xpath("//portal-application").text + ":")
      print()

   driver.find_element_by_xpath("//portal-application").click()
   elements = driver.find_elements_by_xpath("//portal-instance-list/*")
   accounts = list(filter(lambda x: x != "", map(lambda x: x.text, elements)))

   account_found = False
   profile_found = False
   for i in range(len(accounts)):
      if list_accounts:
         print(accounts[i])

      if not list_accounts and accounts[i].find(f"#{account} ") != -1:
         account_found = True
         account_instance = driver.find_elements_by_tag_name("portal-instance")[i]
         account_instance.click()
         WebDriverWait(driver, 15).until(
            # Look for any.
            EC.element_to_be_clickable((By.ID, "temp-credentials-button"))
         )

         elements = driver.find_elements_by_xpath("//portal-profile/*")
         profiles = list(filter(lambda x: x != "", map(lambda x: x.text.split("\n")[0], elements)))

         profile_found = False
         for j in range(len(profiles)):
            if list_profiles:
               print(profiles[j])

            if not list_profiles and profiles[j].find(profile) != -1:
               profile_found = True
               profile_instance = driver.find_elements_by_tag_name("portal-profile")[j]
               profile_instance.find_element_by_id("temp-credentials-button").click()
               WebDriverWait(driver, 30).until(
                  EC.element_to_be_clickable((By.ID, "env-var-linux"))
               )
               print(driver.find_element_by_id("env-var-linux").text.replace("\"", ""))
               break
            if profile_found:
               break

      if list_accounts:
        print()

   if not list_accounts and not account_found:
      raise Exception(f"Account {account} not found")
   if not list_profiles and not profile_found:
      raise Exception(f"Profile {profile} not found")

def parse_url_with_user_code(url_with_user_code):
   from urllib.parse import urlparse, urljoin, parse_qs
   parts = urlparse(url_with_user_code)
   qs = parse_qs(parts.query)

   url = urljoin(url_with_user_code, parts.path)
   user_code = qs['user_code'][0]
   return (url, user_code)

def do_login(driver, username, password, code, url_with_user_code):
   (url, user_code) = parse_url_with_user_code(url_with_user_code)

   driver.get(url)

   # Wait for user_code form
   button = WebDriverWait(driver, 60).until(
      EC.element_to_be_clickable((By.ID, "cli_verfication_btn"))
   )
   input =  WebDriverWait(driver, 60).until(
      EC.element_to_be_clickable((By.ID, "verification_code"))
   )
   input.send_keys(user_code)
   button.click()

   # Wait for user_code result
   WebDriverWait(driver, 60).until(EC_OR(
      # Some error
      EC.visibility_of_element_located((By.XPATH, "//*[@id='alertFrame']/div/*[normalize-space()]")),
      # Already Logged in
      EC.element_to_be_clickable((By.ID, "cli_login_button")),
      # Auth
      EC.element_to_be_clickable((By.ID, "username-submit-button"))
   ))

   # Some error?
   try:
      alert = driver.find_element_by_xpath("//*[@id='alertFrame']/div/*[normalize-space()]")
      raise Exception(alert.text)
   except NoSuchElementException:
      # If not alert or empty then user_code is correct, fall through
      pass

   # Already Logged in?
   try:
      button = driver.find_element_by_id("cli_login_button")
      button.click()
      return
   except NoSuchElementException:
      # If login button is not found then is not logged in, fall through
      pass

   # Auth
   do_auth(driver, username, password, code)

   # Wait for auth result
   WebDriverWait(driver, 60).until(EC_OR(
      # Some error
      EC.visibility_of_element_located((By.XPATH, "//*[@id='alertFrame']/div/*[normalize-space()]")),
      # Log in
      EC.element_to_be_clickable((By.ID, "cli_login_button"))
   ))

   # Some error?
   try:
      alert = driver.find_element_by_xpath("//*[@id='alertFrame']/div/*[normalize-space()]")
      raise Exception(alert.text)
   except NoSuchElementException:
      # If not alert or empty then auth is correct, fall through
      pass

   # Log in
   button = driver.find_element_by_id("cli_login_button")
   button.click()

   # Wait for either success or try again
   while True:
      WebDriverWait(driver, 10).until(EC_OR(
         # Success
         EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'success-icon')]")),
         # Log in
         EC.element_to_be_clickable((By.ID, "cli_login_button"))
      ))
      try:
         driver.find_element_by_xpath("//div[contains(@class, 'success-icon')]")
         break
      except NoSuchElementException:
         pass

      try:
         button = driver.find_element_by_id("cli_login_button")
         button.click()
      except NoSuchElementException:
         pass

if __name__ == "__main__":
   if DEBUG == 3: import pdb; pdb.set_trace()
   parser = argparse.ArgumentParser(description="AWS MFA Keys Fetcher")
   parser.add_argument("-U", "--username",
                       help="User name. Read from '" + CONFIG_FILE_NAME + "' if not provided",
                       default="")
   parser.add_argument("-P", "--password",
                       help="Password. Read from '" + CONFIG_FILE_NAME + "' if not provided",
                       default="")
   parser.add_argument("-C", "--code",
                       help="MFA Code. Read from '" + CONFIG_FILE_NAME + "' if not provided",
                       default="")

   # account specific
   parser.add_argument("-a", "--account",
                       help="Account ID. List accounts if not provided",
                       default="")
   parser.add_argument("-p", "--profile",
                       help="Profile ID for Account ID. List account's profiles if not provided",
                       default="")
   parser.add_argument("--url",
                       help="Auth URL. Read from '" + CONFIG_FILE_NAME + "' if not provided",
                       default="")
   # login specific
   parser.add_argument("-l", "--login",
                       help="Automatic SSO Login",
                       default="")

   parser.add_argument("--version",
                       help="Version",
                       action="version",
                       version="Schema: 2021-05-06 Code: 2021-05-13")
   args = parser.parse_args()
   argsd = vars(args)

   # generic
   username = get_arg(argsd, "username", True)
   password = get_arg(argsd, "password", True)
   code     = get_arg(argsd, "code",     True)
   # account specific
   account  = get_arg(argsd, "account",  False)
   profile  = get_arg(argsd, "profile",  False)
   url      = get_arg(argsd, "url",      True)
   # login specific
   login    = get_arg(argsd, "login",    False)

   base_dir = base_dir()

   if DEBUG > 0:
      print("Python: " + sys.version.split('\n')[0])
      print("Username: " + username)
      print("Password: " + "*" * len(password))
      print("Code: " + code)
      print("Account: " + account)
      print("Profile: " + profile)
      print("Url: " + url)
      print("Login: " + login)
      print("Dir: " + base_dir)

   chrome_options = webdriver.ChromeOptions()
   if DEBUG < 2:
      chrome_options.add_argument("--headless")
   chrome_options.add_argument("--disable-gpu")
   driver = webdriver.Chrome(
      executable_path=os.path.join(base_dir, "bin/chromedriver"),
      chrome_options=chrome_options
   )
   try:
      if login:
         do_login(driver, username, password, code, login)
      else:
         do_account(driver, username, password, code, url)

   except TimeoutException:
      eprint("Error: Timeout")
      sys.exit(1)
   except Exception as e:
      eprint("Error: " + str(e))
      sys.exit(1)
   finally:
      if DEBUG < 2:
         driver.quit()
