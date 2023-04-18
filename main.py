import easyocr
import textblob
import colorama
from colorama import Fore
import requests
import json
import random
import datetime
import time
from openpyxl import load_workbook
import numpy as np
from sklearn.linear_model import LinearRegression

random.seed(a = None)
colorama.init(autoreset = True)

reader = easyocr.Reader(['en'])

image_location = 'test.png'
extracted_text = reader.readtext(image_location, detail = 0, paragraph = 0)
text_str = ""

for i in extracted_text:
		text_str += i
		text_str += '\n'

def IsItCorrect(word):
	if word == 'i': return 0

	corrected = textblob.Word(word).spellcheck()
	for i in corrected:
		if i[0] == word:
			return 1
	
	return 0

def show_grammar_errors(text):
	for word in text:
		if IsItCorrect(word.strip(',')) == 0:
			print(Fore.RED + word, end = ' ')
		else:
			print(Fore.GREEN + word, end = ' ')

def summarize(text_to_sum):
	url = "https://gpt-summarization.p.rapidapi.com/summarize"

	payload = {
		"text": text_to_sum,
		"num_sentences": 3
	}
	headers = {
		"content-type": "application/json",
		"X-RapidAPI-Key": "031d7e874fmsh1345fd6f317bdc8p186083jsn60a6b31a04ba",
		"X-RapidAPI-Host": "gpt-summarization.p.rapidapi.com"
	}

	response = requests.request("POST", url, json=payload, headers=headers)

	return json.loads(response.text)['summary']

def check_similarity(word1, word2):
	word1 = word1.lower().strip(',').strip('.').strip('\'')
	word2 = word2.lower().strip(',').strip('.').strip('\'')
	return word1 == word2

def test_student(study_material, question_amount = 3):

	summary = summarize(study_material)
	summary_words = summary.split(' ')

	words_to_ask = {}

	reps = 0
	while reps < 1000 and len(words_to_ask) != question_amount:
		reps += 1
		ind = random.randrange(0, len(summary_words))
		cur_word = summary_words[ind].lower().strip(',').strip('.').strip('\'')

		not_important = ['such', 'of', 'and', 'or', 'as', 'the', 'in', 'at', 'on', 'into', 'a', 'who', 'where', 'which', 'what', 'why']

		if cur_word not in not_important:
			words_to_ask.update({ind: cur_word})


	answers = {}
	for ind in range(0, len(summary_words)):
		if ind in words_to_ask.keys():
			print("*" * len(summary_words[ind]), end = ' ')

			answers.update({ind: ""})
		else:
			print(summary_words[ind], end = ' ')

	print('\n')

	question_ind = 0
	for ind in answers.keys():
		question_ind += 1
		answers[ind] = input(f"Question {question_ind}: ")

	question_ind = 0

	right_amount = 0
	wrong_amount = 0

	for ind in answers.keys():
		question_ind += 1
		if check_similarity(answers[ind], words_to_ask[ind]):
			print(f"Question {question_ind}: " + Fore.GREEN + words_to_ask[ind])
			right_amount += 1

		else:
			print(f"Question {question_ind}: " + Fore.RED + words_to_ask[ind])
			wrong_amount += 1

	print("Your result: ", right_amount / question_amount * 100.0)
	return right_amount / question_amount * 100.0

def Timer(h, m, s):
	total_seconds = h * 60 * 60 +  m * 60 + s
	while total_seconds: 
		timer = datetime.timedelta(seconds = total_seconds)

		print(timer, end = '\r')

		time.sleep(1.0)

		total_seconds -= 1

	print("Time's Up")

def update_data(result, time):
	data = open('previous_results.txt', 'a')
	data.write(f"\n{result} {time}")

	data.close()

def predict_time():
	data = open('previous_results.txt', 'r')

	x = []
	y = []

	model = LinearRegression()

	for line in data:
		if line.strip():
			a, b = line.split()

			a = float(a)
			b = int(b)
			
			x.append(a)
			y.append(b)

	
	data.close()

	x = np.array(x).reshape((-1, 1)) #score
	y = np.array(y) #time
	model.fit(x, y)

	return int(model.predict(np.array([100.0]).reshape(-1, 1))[0])

def YesOrNo(message):
	while 1:
		answer = input(message)
		if answer.lower() == "yes" or answer.lower() == "y":
			return True
		
	return False

def main():
		
	while 1:
		#print("Insert materials that you want to study or write stop to close the program")
		#study_material = str(input())

		study_material = text_str

		if study_material.lower() == "stop":
			break

		time = int(predict_time())
		h = int(time / 3600)
		m = int((time % 3600) / 60)
		s = int(time % 60)

		print(f"For the best results, you will be given {h} hours : {m} minutes : {s} seconds")

		YesOrNo("Do you want to start [Yes/No]: ")
		
		Timer(0, 0, 5)

		YesOrNo("Are you ready to take a test? [Yes/No]: ")

		result = test_student(study_material)

		update_data(result, time)


main()
