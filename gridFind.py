import numpy as np
import cv2
import pyautogui
import math

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
    print(frequency)
    return list(frequency.keys())[list(frequency.values()).index(max_frequency)]

img = pyautogui.screenshot()
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

cols = sorted(cols)
rows = sorted(rows)
x = 0
#debuggin var
removed = 0
while x < len(cols) - 1:
    if (cols[x+1] - cols[x]) < (max / 2):
        cols.pop(x+1)
        removed += 1
    else:
        x += 1
x = 0
while x < len(rows) - 1:
    if (rows[x+1] - rows[x]) < (max / 2):
        rows.pop(x+1)
        removed += 1
    else:
        x += 1
#debugging var
count = 0
for i, contour in enumerate(contours):
    x, y, w, h = cv2.boundingRect(contour)
    if cols.count(x) == 1 and rows.count(y) == 1 and w == max:
        cv2.drawContours(img, contours, i, (0,0,255), 3)
        count += 1

width = len(cols)
height = len(rows)
grid = np.full((height, width), math.inf)
squareSize = max
cleared = []
bigFound = False
bombsFound = 0
corners = np.empty((height,width), dtype=object)

for i in range(0, width):
    for j in range(0, height):
        corners[j][i] = (cols[i]+1,rows[j]+1)

print(width, "times", height, "is", width * height)
print(squareSize)
print(count)
print("Removed: ", removed)
#pyautogui.moveTo(corners[2][2])
cv2.imshow("Display window", img)
k = cv2.waitKey(0)