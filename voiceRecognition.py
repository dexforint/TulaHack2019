import speech_recognition as sr
from selenium import webdriver
import re
from selenium.webdriver.common.keys import Keys

numbers = {
	'first': 0,
	'second': 1,
	'third': 2,
	'forth': 3,
	'fifth': 4,
	'sixth': 5,
	'seventh': 6,
	'eigth': 7,
	'ninth': 8,
	'tenth': 9,
	'eleventh': 10,
	'twelvth': 11
}

class Management:
	def __init__(self, lang='en-US'):	#ru-RU
		self.lang = lang
		self.launch()

	def recognize(self):
		rc = sr.Recognizer()


		with sr.Microphone() as source:
			print("Говорите!")
			rc.pause_threshold = 1
			rc.adjust_for_ambient_noise(source, duration=0.5)
			audio = rc.listen(source)


		try:
			task = rc.recognize_google(audio, language=self.lang).lower()
			print("Распознано:", task)
		except sr.UnknownValueError:
			task = None

		return task

	# def recognize(self):
	# 	return input("Введите команду: ")

	def command(self, task):
		if 'close program' in task:
			self.driver.quit()
			print("До свидания!")
			exit()

		elif 'find' in task:
				pattern = r'find [^ $]+'
				result = re.search(pattern, task)
				if result != None:
					word = result.group(0)[5:]
					input_field = self.driver.find_element_by_class_name('input__control')
					input_field.clear()
					input_field.send_keys(word, Keys.ENTER)

		elif 'close browser' in task:
			self.driver.quit()

		elif 'close tab' in task:
			self.driver.close()

		elif 'open browser' in task:
				self.driver = webdriver.Chrome()
				self.driver.get('https://yandex.ru/search/')

		elif 'open' in task:
			pattern = r'open [^ ]+ link'
			result = re.search(pattern, task)
			if result != None:
				word = result.group(0)[5:-5]
				number = numbers.get(word, None)
				if number != None:
					links = self.driver.find_elements_by_xpath('//*[@class="organic__title-wrapper typo typo_text_l typo_line_m"]/a')
					links[number].click()

		elif 'back' in task:
			self.driver.execute_script("window.history.go(-1)")
		elif 'forward' in task:
			self.driver.execute_script("window.history.go(+1)")

		elif 'test1' in task:
			print(self.driver.window_handles)
			self.driver.switch_to_window(self.driver.window_handles[1])


	def launch(self):
		while True:
			task = self.recognize()
			self.command(task)

def main():
	m = Management()
	m.launch()

if __name__ == '__main__':
	main()