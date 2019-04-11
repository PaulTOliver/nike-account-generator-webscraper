import colored
import lxml.html
import names
import random
import re
import requests
import string
import time
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.firefox.options import Options

def to_bool(message):
	while True:
		answer = input(message)
		if answer == "y": return True
		if answer == "n": return False

def get_proxy_list():
	response = requests.get("https://free-proxy-list.net/")
	parser   = lxml.html.fromstring(response.text)
	result   = []

	for i in parser.xpath("//tbody/tr"):
		if i.xpath(".//td[7][contains(text(),\"yes\")]"):
			proxy_url = ":".join([i.xpath(".//td[1]/text()")[0], i.xpath(".//td[2]/text()")[0]])
			result.append(proxy_url)

	return result

def create_valid_password():
	header1 = random.choice(string.ascii_uppercase)
	header2 = random.choice(string.ascii_lowercase)
	volume  = "".join(random.choice(string.ascii_letters + string.digits) for _ in range(6))
	footer  = "".join(random.choice(string.digits) for _ in range(4))
	return header1 + header2 + volume + footer

def create_random_user():
	print("")
	print("{}Creating random user...{}".format(colored.fg(11), colored.attr(0)))
	user           = {}
	user["gender"] = random.choice(["male", "female"])
	user["name"]   = names.get_full_name(user["gender"])
	user["email"]  = "".join(random.choice(string.ascii_letters + string.digits) for _ in range(10)) + "@gmail.com"
	user["passwd"] = create_valid_password()
	user["bmonth"] = "{:02}".format(random.choice(range(1, 13)))
	user["bday"]   = "{:02}".format(random.choice(range(1, 29)))
	user["byear"]  = str(random.choice(range(1960, 2001)))
	print("Name:     {}".format(user["name"]))
	print("email:    {}".format(user["email"]))
	print("passwd:   {}".format(user["passwd"]))
	print("gender:   {}".format(user["gender"]))
	print("birthday: {}".format(user["bmonth"] + "/" + user["bday"] + "/" + user["byear"]))
	print("")
	return user

def create_new_account():
	while True:
		try:
			user    = create_random_user()
			options = Options()
			profile = webdriver.FirefoxProfile()
			caps    = None
			profile.set_preference("permissions.default.image", 2)

			if headless:
				options.add_argument("--headless")

			if use_proxies:
				sel_proxy = random.choice(proxy_list)
				print("Using proxy {}".format(sel_proxy))
				caps               = DesiredCapabilities.FIREFOX
				caps["marionette"] = True
				caps["proxy"]      = {
					 "proxyType": "MANUAL",
					 "httpProxy": sel_proxy,
					 "ftpProxy":  sel_proxy,
					 "sslProxy":  sel_proxy
				}

			br = webdriver.Firefox(firefox_options = options, firefox_profile = profile, capabilities = caps)
			br.implicitly_wait(30)
			br.set_page_load_timeout(60)

			print("Loading website...")
			br.get("https://www.nike.com/launch/")
			time.sleep(2)

			def open_element(path):
				link = br.find_element_by_xpath(path)
				link.click()

			def fill_input(path, data):
				input_box = br.find_element_by_xpath(path)
				input_box.send_keys(data)

			print("Opening account creation form...")
			open_element("//button[@data-qa='join-login']")
			open_element("//form[@id='nike-unite-loginForm']/div[7]/a")

			print("Filling form with data...")
			fill_input("//input[@name='emailAddress']", user["email"])
			fill_input("//input[@name='password']", user["passwd"])
			fill_input("//input[@name='firstName']", user["name"].split()[0])
			fill_input("//input[@name='lastName']", user["name"].split()[1])
			open_element("//select[@id='nike-unite-date-id-mm']/option[@value='" + user["bmonth"] + "']")
			open_element("//select[@id='nike-unite-date-id-dd']/option[@value='" + user["bday"] + "']")
			open_element("//select[@id='nike-unite-date-id-yyyy']/option[@value='" + user["byear"] + "']")

			if user["gender"] == "male":
				open_element("//ul[@data-componentname='gender']/li[1]/span")
			else:
				open_element("//ul[@data-componentname='gender']/li[2]/span")

			if not test_run:
				print("Submitting form...")
				open_element("//input[@value='CREATE ACCOUNT']")
				open_element("//input[@placeholder='Enter Code']")
			else:
				print("This is a test run. No submission will be made.")

			print("{}Account generated succesfully!{}".format(colored.fg(10), colored.attr(0)))

			with open("output.data", "a") as f:
				if use_proxies:
					f.write("{}:{} {}\n".format(user["email"], user["passwd"], sel_proxy))
				else:
					f.write("{}:{}\n".format(user["email"], user["passwd"]))

			print("Account credentials appended to 'output.data'.")
			br.quit()
			break
		except KeyboardInterrupt:
			if br: br.quit()
			quit()
		except:
			if br: br.quit()
			print("{}Encountered a problem. Let's try again...{}".format(colored.fg(9), colored.attr(0)))

if __name__ == "__main__":
	print("")
	print("{}Nike-scrapper Account Generator{}".format(colored.fg(11), colored.attr(0)))
	print("Let's set some options...")

	while True:
		ac_count    = int(input("How many accounts would you like to generate?: "))
		headless    = to_bool("Would you like to run headless? [y/n]: ")
		test_run    = to_bool("Would you like to make this a test-run? [y/n]: ")
		use_proxies = to_bool("Utilize proxy servers? [y/n]: ")
		print("---")
		print("No. of accounts: {}".format(ac_count))
		print("Run headless:    {}".format(headless))
		print("Test run:        {}".format(test_run))
		print("Use proxy:       {}".format(use_proxies))
		print("---")

		if to_bool("Is all this correct? [y/n]: "):
			break

	for i in range(ac_count):
		if use_proxies and i % 10 == 0:
			print("")
			print("{}Getting proxy list...{}".format(colored.fg(11), colored.attr(0)))
			proxy_list = get_proxy_list()
			for i in proxy_list: print(i)

		create_new_account()
