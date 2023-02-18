import cv2
import math
import numpy as np
import pyautogui
import pytesseract
import minesweeper

def find_mode(numbers):
    # Create a dictionary to store the frequency of each number
    frequency = {}
    for number in numbers:
        if number == 0:
            break
        if number in frequency:
            frequency[number] += 1
        else:
            frequency[number] = 1
    
    # Find the number(s) with the highest frequency
    max_frequency = max(frequency.values())
    return list(frequency.keys())[list(frequency.values()).index(max_frequency)]

def readGrid():
    img = pyautogui.screenshot()
    minesweeper.totalBombs = bombsCount(img)
    img = cv2.cvtColor(np.array(img), cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(img,100,200)
    contours, _ = cv2.findContours(edges, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
    widths = np.zeros(len(contours))
    boxes = np.empty(len(contours), dtype=object)

    i = 0
    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        if w == h and w > 10:
            widths[i] = w
            boxes[i] = (x,y,w)
            i += 1
    max = find_mode(widths)

    rows = set()
    cols = set()

    for box in boxes:
        if box == None:
            break
        if box[2] == max:
            cols.add(box[0])
            rows.add(box[1])

    minesweeper.width = len(cols)
    minesweeper.height = len(rows)
    minesweeper.grid = np.full((minesweeper.height, minesweeper.width), math.inf)
    minesweeper.squareSize = max
    minesweeper.cleared = []
    minesweeper.bigFound = False
    minesweeper.corners = np.empty((minesweeper.height,minesweeper.width), dtype=object)

    cols = sorted(cols)
    rows = sorted(rows)

    for i in range(0, minesweeper.width):
        for j in range(0, minesweeper.height):
            minesweeper.corners[j][i] = (cols[i]+1,rows[j]+1)

def bombsCount(image):
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

    text = pytesseract.image_to_string(image, lang='lets', config='--psm 6')
    if text.isdigit():
        return text
    return 999