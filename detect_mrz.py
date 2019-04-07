from os import listdir
import numpy as np
from imutils import grab_contours, resize
import cv2
from pytesseract import image_to_string
import re

folder = './samples'

string = ""

# инициализировать прямоугольное и квадратное структурирующее ядро
rectKernel = cv2.getStructuringElement(cv2.MORPH_RECT, (13, 5))
sqKernel = cv2.getStructuringElement(cv2.MORPH_RECT, (21, 21))

# цикл по входным путям изображения
for imageName in listdir(folder):
	# загрузить изображение, изменить его размер и преобразовать его в оттенки серого
	image = cv2.imread(folder + '/' + imageName)
	image = resize(image, width=600)

	# в чёрно-белое
	gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

	# cv2.imshow("gray", gray)
	# cv2.waitKey(0)

	# морфологический оператор для поиска темных областей на светлом фоне

	blackhat = cv2.morphologyEx(gray, cv2.MORPH_BLACKHAT, rectKernel)

	# cv2.imshow("blackhat0", blackhat)
	# cv2.waitKey(0)
	
	# вычислить градиент Шарра изображения черной шляпы и масштабировать
	# результат в диапазоне [0, 255]
	gradX = cv2.Sobel(blackhat, ddepth=cv2.CV_32F, dx=1, dy=0, ksize=-1)

	# cv2.imshow("gradX1", gradX)
	# cv2.waitKey(0)

	gradX = np.absolute(gradX)

	# cv2.imshow("gradX2", gradX)
	# cv2.waitKey(0)
	
	(minVal, maxVal) = (np.min(gradX), np.max(gradX))
	gradX = (255 * ((gradX - minVal) / (maxVal - minVal))).astype("uint8")


	# cv2.imshow("gradX3", gradX)
	# cv2.waitKey(0)

	# применить операцию закрытия, используя прямоугольное ядро, чтобы закрыть
	# промежутки между буквами - затем примените метод определения порога Оцу
	gradX = cv2.morphologyEx(gradX, cv2.MORPH_CLOSE, rectKernel)

	# cv2.imshow("gradX4", gradX)
	# cv2.waitKey(0)

	thresh = cv2.threshold(gradX, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]

	# cv2.imshow("thresh5", thresh)
	# cv2.waitKey(0)

	# выполнить еще одну операцию закрытия, на этот раз используя квадрат
	# ядро, чтобы закрыть пробелы между линиями MRZ, а затем выполнить
	# Serieso эрозии, чтобы разбить соединенные компоненты
	thresh = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, sqKernel)

	# cv2.imshow("thresh6", thresh)
	# cv2.waitKey(0)

	# найти контуры в пороговом изображении и отсортировать их по размеру
	cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,
		cv2.CHAIN_APPROX_SIMPLE)
	cnts = grab_contours(cnts)
	cnts = sorted(cnts, key=cv2.contourArea, reverse=True)

	# петля по контурам
	for c in cnts:
		# рассчитать ограничивающий прямоугольник контура и использовать контур
		# для вычисления соотношения сторон и коэффициента покрытия ширины 
		# ограничивающего прямоугольника к ширине изображения
		(x, y, w, h) = cv2.boundingRect(c)
		ar = w / float(h)
		crWidth = w / float(gray.shape[1])

		# проверьте, соответствуют ли пропорции и ширина покрытия приемлемым критериям
		if ar > 5 and crWidth > 0.75:
			# дополнить ограничивающий прямоугольник, так как мы применили эрозию и теперь нужно заново ее растить
			pX = int((x + w) * 0.03)
			pY = int((y + h) * 0.03)
			(x, y) = (x - pX, y - pY)
			(w, h) = (w + (pX * 2), h + (pY * 2))

			# извлеките ROI из изображения и нарисуйте ограничивающую рамку, окружающую MRZ
			roi = image[y:y + h, x:x + w].copy()
			roi_gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
			s = image_to_string(roi_gray).strip().replace(' ', '')
			results = re.findall(r'<K+', s)
			for result in results:
				s = s.replace(result, '<' * len(result), 1)
			string += imageName + '\n' + s + '\n\n'
			cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)
			break

	# cv2.imshow("ROI", roi)
	# cv2.waitKey(0)

file = open('answers.txt', 'w')
file.write(string)
file.close()