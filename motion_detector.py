from imutils.video import VideoStream
import imutils
import cv2
from time import sleep

# Чтение видеопотока с веб-камеры
vs = VideoStream(src=0).start()
sleep(1.0)

firstFrame = None

reg1 = 500 # минимальный размер контуров разницы
reg2 = 50 # отвечает за минимальный размер детекции

# видеострим
while True:
	# захват кадра
	frame = vs.read()
	text = ""
	# изменить размер
	frame = imutils.resize(frame, width=900)
	# превратить в чёрно-белое изображение (так легче анализировать)
	gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
 
	# первый кадр как эталонный
	if firstFrame is None:
		firstFrame = gray
		continue

	# разница между текущим кадром и эталонным
	framesDelta = cv2.absdiff(firstFrame, gray)
	#cv2.imshow("framesDelta", framesDelta)
	# для чёткости
	thresh = cv2.threshold(framesDelta, 25, 255, cv2.THRESH_BINARY)[1]
	cv2.imshow("thresh", thresh)

	# контуры
	cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,
		cv2.CHAIN_APPROX_SIMPLE)
	cnts = imutils.grab_contours(cnts)

	# анализ контуров
	for i, c in enumerate(cnts):
		# удаление недостаточно больших контуров
		if cv2.contourArea(c) < reg1:
			continue

		# рамка для контура (сама детекция)
		(x, y, w, h) = cv2.boundingRect(c)
		if w > reg2 and h > reg2:
			cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)
			text = "Motion is detected!"

	# текст
	cv2.putText(frame, text, (250, 20),
		cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
	
	key = cv2.waitKey(1) & 0xFF

	if key == ord("q"):		# закрыть программу
		break
	elif key == ord("u"):	# обновить (данный кадр как эталон)
		firstFrame = gray

	cv2.imshow("Camera", frame)

vs.stop()
cv2.destroyAllWindows()