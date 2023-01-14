import cv2
import math

# Read in the image and convert it to grayscale
image = cv2.imread('example.png')
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

# Detect edges in the image
edges = cv2.Canny(gray, 50, 150)

# Detect lines in the image
lines = cv2.HoughLinesP(edges, 1, math.pi / 180, 100, minLineLength=100, maxLineGap=10)

# Iterate over the lines and draw them on the image
for line in lines:
    x1, y1, x2, y2 = line[0]
    cv2.line(image, (x1, y1), (x2, y2), (0, 0, 255), 2)

# Show the image
cv2.imshow('Image with lines', image)
cv2.waitKey(0)
