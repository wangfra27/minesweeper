import cv2
import numpy as np
import math
from matplotlib import pyplot as plt
import pyautogui
from PIL import Image
import pytesseract


image = pyautogui.screenshot()
gray = cv2.cvtColor(np.array(image), cv2.COLOR_BGR2GRAY)
ret, thresh = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
kernel = np.ones((3,3), np.uint8)
erosion = cv2.erode(thresh, kernel, iterations=1)
dilation = cv2.dilate(erosion, kernel, iterations=1)
edges = cv2.Canny(dilation, 100, 200)

contours, hierarchy = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
loc = (math.inf, math.inf, math.inf, math.inf)
for contour in contours:
    x, y, w, h = cv2.boundingRect(contour)
    if w >= 50 and w <= 100 and h >= 30 and h <= 70:
        if x < loc[0]:
            loc = (x,y,w,h)

img = np.array(image)
image = img[loc[1]+1:loc[1]+loc[3], loc[0]+1:loc[0]+loc[2]]

#image = image[0:loc[3], 0:int(loc[2]/3)]

temp = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
low = (0, 0, 0)
high = (0, 0, 0)
mask=cv2.inRange(temp,low,high)
image[mask>0]=(255,255,255)

temp = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
low = (100, 0, 0)
high = (140, 255, 100)
mask=cv2.inRange(temp,low,high)
image[mask>0]=(255,255,255)

temp = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
image[mask>0]=(255,255,255)
low = (100, 10, 0)
high = (140, 255, 255)
mask=cv2.inRange(temp,low,high)
image[mask>0]=(0,0,0)

kerneli = np.ones((3,3),np.uint8)
image = cv2.erode(image, kerneli)
kernele = np.ones((5,5),np.uint8)
image = cv2.dilate(image, kernele)
image = cv2.erode(image, kerneli)
image = cv2.dilate(image, kernele)

text = pytesseract.image_to_string(image, lang='lets', config='--psm 6') #6 or 7, 10 for single digit
print(text)

#cv2.imwrite("out.png", image)
cv2.imshow("Display window", image)
k = cv2.waitKey(0)