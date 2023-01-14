#for minesweeper.online
import pyautogui
import numpy as np
import cv2
import random
import math
import sys
import time
from pynput.mouse import Button, Controller as MouseController
from pynput.keyboard import Listener, Controller as KeyboardController
import threading
#screenWidth = 1920
#screenHeight = 1080

global width
global height
global grid
global corners
global squareSize

global cleared
cleared = []

#3d array
global aPossible
aPossible = []
#2d array
global possible
possible = []

global bigFound
bigFound = False

global bombsFound
bombsFound = 0
global flags
global games

global grey
global one
global two
global three
global four
global five
global six
grey = (198, 198, 198)
one = (0, 0, 255)
two = (0, 128, 0)
three = (255, 0, 0)
four = (0, 0, 128)
five = (128, 0, 0)
six = (0, 128, 128)
#seven = (24, 24, 24)
#eight = (128, 128, 128)
#17,20
#flag = -1, blank = inf
#read num total bombs
#should prioritize random clicking on the left at the begnining because it searches left to right
# maybe save defined sections so that if it finds the same section it doesnt have to recalculate? 

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
    global width
    global height
    global grid
    global corners
    global squareSize
    global cleared
    global bigFound
    global bombsFound
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

    width = len(cols)
    height = len(rows)
    grid = np.full((height, width), math.inf)
    squareSize = max
    cleared = []
    bigFound = False
    bombsFound = 0
    corners = np.empty((height,width), dtype=object)

    cols = sorted(cols)
    rows = sorted(rows)

    for i in range(0, width):
        for j in range(0, height):
            corners[j][i] = (cols[i]+1,rows[j]+1)

def getColor(x,y, im1):
    #print("get Color ", x, y)
    a = corners[y][x][0] + (squareSize * 1 / 2)
    b = corners[y][x][1] + (squareSize * 3 / 4)
    pix = im1.getpixel((int(a), int(b)))
    if (pix == one):
        return 1
    if (pix == two):
        return 2
    if (pix == three):
        return 3
    if (pix == five):
        return 5
    if (pix == six):
        return 6
    a = corners[y][x][0] + (squareSize * 3 / 4)
    b = corners[y][x][1] + (squareSize * 1 / 2)
    if (im1.getpixel((int(a), int(b))) == (0, 0, 128)):
        return 4
    a = corners[y][x][0] + (squareSize * 1 / 2)
    b = corners[y][x][1] + (squareSize * 1 / 4)
    if (im1.getpixel((int(a), int(b))) == (255, 32, 32)):
        return -1
    a = corners[y][x][0] + (squareSize * 1 / 4)
    b = corners[y][x][1] + (squareSize * 1 / 2)
    if (im1.getpixel((int(a), int(b))) == (0, 0, 0)):
        return -2
    a = corners[y][x][0] + 1
    b = corners[y][x][1] + 1
    if (im1.getpixel((int(a), int(b))) == (255, 255, 255)):
        return math.inf
    return 0

def randomClick():
    global bigFound
    if bigFound:
        print("randomClick")
    #print(grid)
    x = random.randint(0, width-1)
    y = random.randint(0, height-1)
    while (grid[y][x] != math.inf):
        x = random.randint(0, width-1)
        y = random.randint(0, height-1)
    #pyautogui.click(corners[y][x][0], corners[y][x][1])
    mouse.move(corners[y][x][0], corners[y][x][1])
    mouse.click(Button.left, 1)
    im1 = pyautogui.screenshot()
    if not updateTile(x,y,im1):
        return False
    return True

def inrange(x,y):
    if x >= 0 and y >= 0 and x < width and y < height:
        return True
    return False

def updateTile(x,y,im1):
    global cleared
    global bigFound
    #print("update Tile ", x, y)
    num = getColor(x,y,im1)
    if num == -2:
        return False
    grid[y][x] = num
    if (num == 0):
        bigFound = True
        insert = (x,y)
        cleared.append(insert)
        for a in range (x-1, x+2):
            for b in range (y-1, y+2):
                check = (a,b)
                if inrange(a,b) and cleared.count(check) == 0 and grid[b][a] == math.inf:
                    if not updateTile(a,b,im1):
                        return False
    return True

def makeClicks():
    #print("makeClicks")
    change = False
    for x in range (0, width):
        for y in range (0, height):
            if grid[y][x] != 0 and grid[y][x] != math.inf:
                fchange = flagAround(x,y)
                a, cchange = clickAround(x,y)
                if not a:
                    return False
                if change == False and (fchange or cchange):
                    change = True

    if change == False:
        change = advTactics1()
    if change == False:
        a, change = advTactics2()
        if not a:
            return False
    if change == False:
        if not educatedGuess():
            return False
    return True

def educatedGuess():
    print("educatedGuess")
    #IMPLEMENT ERROR CHECKING FOR EMPTY LISTS
    #2d-temp for inserting
    global possible
    global bombsFound
    possible = []
    #3d
    global aPossible
    aPossible = []

    #2d
    sections = []
    #2d
    used = []

    change = False
    #divides Sections into sections
    divideSections(sections,used)

    i = 0
    while i < len(used):
        if len(used[i]) == 1 or len(used[i]) > 15:
            used.pop(i)
            sections.pop(i)
        else:
            i += 1
    if len(used) == 0:
        print("TOO Hard")
        if not randomClick():
            return False
        return True
    #print(sections)

    #3d
    blanksFor = saveBlanks(sections, used)

    if len(sections) == 0:
        #this shouldn't happen
        print("ERROR1: SECTIONS IS EMPTY")
        if not randomClick():
            return False

    #generates all possible combinations of mines into aPossible
    for i in range(0, len(sections)):
        tempGrid = grid.copy()
        possibility = [0] * len(sections[i])
        allPossible(sections[i], used[i], tempGrid, possibility, blanksFor[i], 0)
        #print("Generated ", len(possible), " possibilities") #this count doesnt do what i want, doesnt chack optimization
        aPossible.append(possible)
        possible = []
    #print(aPossible)
    
    #counts how many times each square is a mine
    #2d array
    totals = []
    for i in range(0, len(aPossible)):
        if len(aPossible[i]) == 0:
            #this shouldn't happen
            print("ERROR2: NO POSSIBLE ARRANGEMENT OF MINES FOR SECTION", i)
            print(sections[i])
            print()
            continue
        input = [0] * len(aPossible[i][0])
        for j in aPossible[i]:
            for k in range(0, len(j)):
                input[k] += j[k]
        input = [l / len(aPossible[i]) for l in input]
        totals.append(input)
    """ for x in range(0, len(aPossible)):
        print("Possibility ", x, ": ", aPossible[x]) """
    #print("Percentages:")
    print(totals)
    print()
    
    #find 0s and 100s
    for i in range(0, len(totals)):
        for j in range(0, len(totals[i])):
            if totals[i][j] == 0:
                x = sections[i][j][0]
                y = sections[i][j][1]
                #pyautogui.click(corners[y][x][0], corners[y][x][1])
                mouse.move(corners[y][x][0], corners[y][x][1])
                mouse.click(Button.left, 1)
                im1 = pyautogui.screenshot()
                #print("Clicking: ", x, y)
                if not updateTile(x,y,im1):
                    return False
                change = True
            elif totals[i][j] == 1:
                x = sections[i][j][0]
                y = sections[i][j][1]
                #print("Flagging: ", x, y)
                if flags == True:
                    #pyautogui.rightClick(corners[y][x][0], corners[y][x][1])
                    mouse.move(corners[y][x][0], corners[y][x][1])
                    mouse.click(Button.right, 1)
                grid[y][x] = -1
                bombsFound += 1
                change = True

    #if there are no ones or zeros, find the most extreme
    if change == False:
        smallest = 1
        biggest = 0
        for i in range(0, len(totals)):
            for j in range(0, len(totals[i])):
                if totals[i][j] < smallest:
                    smallest = totals[i][j]
                    sloc = (sections[i][j][0],sections[i][j][1])
                if totals[i][j] > biggest:
                    biggest = totals[i][j]
                    bloc = (sections[i][j][0],sections[i][j][1])
        if (1-biggest < smallest - 0): #right click biggest
            x = bloc[0]
            y = bloc[1]
            #print("Flagging: ", x, y)
            if flags == True:
                #pyautogui.rightClick(corners[y][x][0], corners[y][x][1])
                mouse.move(corners[y][x][0], corners[y][x][1])
                mouse.click(Button.right, 1)
            grid[y][x] = -1
            bombsFound += 1
        else: #click smallest
            x = sloc[0]
            y = sloc[1]
            #print("Clicking: ", x, y)
            #pyautogui.click(corners[y][x][0], corners[y][x][1])
            mouse.move(corners[y][x][0], corners[y][x][1])
            mouse.click(Button.left, 1)
            im1 = pyautogui.screenshot()
            if not updateTile(x,y,im1):
                return False
    return True

def allPossible(section, use, tempGrid, possibility, blanksFor, it):
    #section and use are array of pairs
    global possible
    if it == len(possibility):
        if checkViolations(tempGrid, use, section):
            possible.append(possibility.copy())
        """ else:
            print(possibility) """
        return
    possibility[it] = 0
    allPossible(section, use, tempGrid.copy(), possibility.copy(), blanksFor, it+1)

    tempGrid[section[it][1]][section[it][0]] = -1
    possibility[it] = 1
    if checkTooMany(tempGrid, use, section[0:it+1], blanksFor):
        allPossible(section, use, tempGrid.copy(), possibility.copy(), blanksFor, it+1)

# initial check for pruning purposes
# true if no violations
# IF we also input an array of already checked squares by marking squares as checked if they pass the 2nd check
def checkTooMany(tempGrid, used, soFar, blanksFor):
    x = 0
    for u in used:
        mines = 0
        check = True
        for a in range (u[0]-1, u[0]+2):
            for b in range (u[1]-1, u[1]+2):
                if inrange(a,b) and tempGrid[b][a] == -1:
                    mines += 1
        if mines > tempGrid[u[1]][u[0]]:
            #print("1 Pruned ", u, " with ", mines)
            return False
        for s in blanksFor[x]:
            if (soFar.count(s)) == 0:
                check = False
                break
        if check:
            #print("check activated")
            if mines != tempGrid[u[1]][u[0]]:
                #print("2 Pruned ", u, " with ", mines, " used ", soFar, " and ", blanksFor)
                return False
        x+=1

    return True

# final check
# true if no violations
def checkViolations(tempGrid, used, section):
    for u in used:
        blank = 0
        mines = 0
        for a in range (u[0]-1, u[0]+2):
            for b in range (u[1]-1, u[1]+2):
                if inrange(a,b) and tempGrid[b][a] == -1:
                    mines += 1
                if inrange(a,b) and tempGrid[b][a] == math.inf and section.count((a,b)) == 0:
                    blank += 1
        if mines > tempGrid[u[1]][u[0]] or tempGrid[u[1]][u[0]] > mines + blank:
            #print("Rejected! Violated ", u[0], u[1])
            return False
    return True

def divideSections(sections,used):
    #og used, contains everything in used in one container, used divides into sections, trash contains blanks
    trash = []
    #to prevent repeats
    for x in range (0, width):
        for y in range (0, height):
            if grid[y][x] == math.inf and active(x,y) and trash.count((x,y)) == 0:
                s=[]
                t=[]
                section(x,y,t,trash)
                # s is all numbers in the section
                # t is all blanks in the section
                for i in t:
                    for a in range (i[0]-1, i[0]+2):
                        for b in range (i[1]-1, i[1]+2):
                            if inrange(a,b) and grid[b][a] > 0 and grid[b][a] != math.inf and s.count((a,b)) == 0:
                                s.append((a,b))
                sections.append(t)
                used.append(s)
    
def saveBlanks(sections, used):
    blanksFor = []
    input1 = []
    input2 = []
    for i in range(0, len(used)):
        for u in used[i]:
            for a in range (u[0]-1, u[0]+2):
                for b in range (u[1]-1, u[1]+2):
                    if inrange(a,b) and (sections[i].count((a,b)) == 1):
                        input1.append((a,b))
            input2.append(input1)
        blanksFor.append(input2)
        
    return blanksFor

def section(x,y,t,trash):
    t.append((x,y))
    trash.append((x,y))
    for a in range (x-1, x+2):
        for b in range (y-1, y+2):
            if trash.count((a,b)) == 0 and inrange(a,b) and grid[b][a] == math.inf and active(a,b):
                section(a,b,t,trash)
            elif inrange(a,b) and grid[b][a] != math.inf and grid[b][a] > 0 and activeNum(a,b,trash):
                for c in range (a-1, a+2):
                    for d in range (b-1, b+2):
                        if inrange(a,b) and grid[b][a] == math.inf and trash.count((a,b)) == 0:
                            section(c,d,t,trash)

def active(x,y):
    #True if next to a number
    for a in range (x-1, x+2):
        for b in range (y-1, y+2):
            if inrange(a,b) and grid[b][a] > 0 and grid[b][a] != math.inf:
                return True
    return False

def activeNum(x,y,trash):
    #True if next to a blank
    for a in range (x-1, x+2):
        for b in range (y-1, y+2):
            if inrange(a,b) and grid[b][a] == math.inf and trash.count((a,b)) == 0:
                return True
    return False

def advTactics1():
    #print("advtactics1")
    global flags
    global bombsFound
    change = False
    tempGrid = grid.copy()
    #make a tempgrid with minimized numbers
    for x in range (0, width):
        for y in range (0, height):
            if tempGrid[y][x] > 0 and tempGrid[y][x] != math.inf:
                for a in range (x-1, x+2):
                    for b in range (y-1, y+2):
                        if inrange(a,b) and tempGrid[b][a] == -1:
                            tempGrid[y][x] -= 1
    #print(tempGrid)

    # for each number
    for x in range (0, width):
        if change == True: 
            break
        for y in range (0, height):
            if change == True: 
                break
            if tempGrid[y][x] > 0 and tempGrid[y][x] != math.inf:
                #for each number touching that number
                for a in range (x-1, x+2):
                    if change == True: 
                        break
                    for b in range (y-1, y+2):
                        if change == True: 
                            break
                        if inrange(a,b) and tempGrid[b][a] > 0 and tempGrid[b][a] != math.inf:
                            #count the number of independent squares
                            ind = []
                            for c in range (a-1, a+2):
                                for d in range (b-1, b+2):
                                    if inrange(c,d) and tempGrid[d][c] == math.inf:
                                        if notTouching(x,y,c,d):
                                            ind.append((c,d))
                            #if the number of independent squares = diff between two numbers, mark all independent squares as flag
                            if len(ind) > 0 and (len(ind) == tempGrid[b][a] - tempGrid[y][x]):
                                #print("1 2 Tactics Used: (", a, ", ", b, ") and (", x, ", ", y, ")")
                                change = True
                                for i,j in ind:
                                    #print("Flagged ", i, j)
                                    if flags == True:
                                        #pyautogui.rightClick(corners[j][i][0], corners[j][i][1])
                                        mouse.move(corners[j][i][0], corners[j][i][1])
                                        mouse.click(Button.right, 1)
                                    bombsFound += 1
                                    grid[j][i] = -1
                                    tempGrid[j][i] = -1
    return change

def advTactics2():
    #print("advtactics2")
    change = False
    tempGrid = grid.copy()
    #make a tempgrid with minimized numbers
    for x in range (0, width):
        for y in range (0, height):
            if tempGrid[y][x] > 0 and tempGrid[y][x] != math.inf:
                for a in range (x-1, x+2):
                    for b in range (y-1, y+2):
                        if inrange(a,b) and tempGrid[b][a] == -1:
                            tempGrid[y][x] -= 1
    # for each number
    for x in range (0, width):
        if change == True: 
            break
        for y in range (0, height):
            if change == True: 
                break
            if tempGrid[y][x] > 0 and tempGrid[y][x] != math.inf:
                #for each number touching that number
                for a in range (x-1, x+2):
                    if change == True: 
                        break
                    for b in range (y-1, y+2):
                        if change == True: 
                            break
                        if inrange(a,b) and tempGrid[b][a] > 0 and tempGrid[b][a] != math.inf:
                            #count the number of independent and dependent squares
                            ind = []
                            dep = []
                            for c in range (a-1, a+2):
                                for d in range (b-1, b+2):
                                    if inrange(c,d) and tempGrid[d][c] == math.inf:
                                        if notTouching(x,y,c,d):
                                            ind.append((c,d))
                                        else: 
                                            dep.append((c,d))
                            if (not samePoint(x,y,a,b) and len(ind) == 0 and len(dep) == 2 and tempGrid[b][a] == 1 and tempGrid[y][x] == 1):
                                #print("1 1 Tactics Used: (", a, ", ", b, ") and (", x, ", ", y, ")")
                                #print(dep)
                                if dep[0][0] == dep[1][0]:
                                    i = dep[0][0]
                                    if dep[0][1] < dep[1][1] and dep[1][1] - dep[0][1] == 1:
                                        j = dep[0][1]-1
                                        q, change = click11(i,j)
                                        if not q:
                                            return False, change
                                        j = dep[1][1]+1
                                        q, change = click11(i,j)
                                        if not q:
                                            return False, change
                                elif dep[0][1] == dep[1][1]:
                                    j = dep[0][1]
                                    if dep[0][0] < dep[1][0] and dep[1][0] - dep[0][0] == 1:
                                        i = dep[0][0]-1
                                        q, change = click11(i,j)
                                        if not q:
                                            return False, change
                                        i = dep[1][0]+1
                                        q, change = click11(i,j)
                                        if not q:
                                            return False, change
    return True, change

def click11(i,j):
    change = False
    if inrange(i, j) and grid[j][i] == math.inf:
        change = True
        #print("click ", i, j)
        #pyautogui.click(corners[j][i][0], corners[j][i][1])
        mouse.move(corners[j][i][0], corners[j][i][1])
        mouse.click(Button.left, 1)
        im1 = pyautogui.screenshot()
        if not updateTile(i,j,im1): 
            return False, change
    return True, change

def samePoint(x,y,a,b):
    if x==a and y==b:
        return True
    return False

# false = touching
def notTouching(x,y,c,d):
    if c < x+2 and c > x-2 and d < y+2 and d > y-2:
        return False
    return True

def flagAround(x,y):
    global flags
    global bombsFound
    flag = 0
    blanks = 0
    change = False
    for a in range (x-1, x+2):
        for b in range (y-1, y+2):
            if inrange(a,b):
                if grid[b][a] == math.inf:
                    blanks += 1
                elif grid[b][a] == -1:
                    flag += 1
    if (flag + blanks == grid[y][x]) and blanks > 0:
        #print("flagAround")
        change = True
        for a in range (x-1, x+2):
            for b in range (y-1, y+2):
                if inrange(a,b) and grid[b][a] == math.inf:
                    if flags == True:
                        #pyautogui.rightClick(corners[b][a][0], corners[b][a][1])
                        mouse.move(corners[b][a][0], corners[b][a][1])
                        mouse.click(Button.right, 1)
                    grid[b][a] = -1
                    bombsFound += 1
    return change

def clickAround(x,y):
    flags = 0
    blanks = 0
    change = False
    for a in range (x-1, x+2):
        for b in range (y-1, y+2):
            if inrange(a,b) and grid[b][a] == -1:
                flags += 1
            elif inrange(a,b) and grid[b][a] == math.inf:
                blanks += 1
    if flags == grid[y][x] and blanks > 0:
        #print("clickAround")
        change = True
        for a in range (x-1, x+2):
            for b in range (y-1, y+2):
                if inrange(a,b) and grid[b][a] == math.inf:
                    #pyautogui.click(corners[b][a][0], corners[b][a][1])
                    mouse.move(corners[b][a][0], corners[b][a][1])
                    mouse.click(Button.left, 1)
                    im1 = pyautogui.screenshot()
                    if not updateTile(a,b,im1):
                        return False, change
    return True, change

def on_press(key):
    global paused
    global thread

    paused = not paused
    if thread is None:
        # run long-running `function` in separated thread
        thread = threading.Thread(target=function)
        thread.start()

def main():
    global flags
    global games
    global sleep
    global paused

    keyboard = KeyboardController()

    if str(sys.argv[1]) == 'f':
        flags = True
    elif str(sys.argv[1]) == 'nf':
        flags = False
    else:
        print("error1")
        exit(1)

    if str(sys.argv[2]) == 'one':
        games = 'o'
    elif str(sys.argv[2]) == 'win':
        games = 'w'
    elif str(sys.argv[2]) == 'infinite':
        games = 'i'
    else:
        print("error2")
        exit(1)
    
    sleep = int(sys.argv[3])

    x,y = pyautogui.locateCenterOnScreen('online/smile.png', confidence=0.9)
    losses = 0
    wins = 0
    unlucky = 0

    if games == 'o':#play once
        while not bigFound:
            readGrid()
            while(True):
                if not randomClick():
                    unlucky += 1
                    #pyautogui.click(x,y)
                    mouse.move(x,y)
                    mouse.click(Button.left, 1)
                    time.sleep(sleep)
                    break
                if bigFound:
                    break

        while(pyautogui.locateOnScreen('online/smile.png', confidence=0.9) is not None):
            if not makeClicks():
                break

        if pyautogui.locateOnScreen('online/sad.png', confidence=0.9) is not None:
            print("Oops I messed up")
        if pyautogui.locateOnScreen('online/win.png', confidence=0.9) is not None:
            print("I won GGEZ")
        print("Unlucky: ", unlucky)
        print("Bombs Found: ", bombsFound)

    if games == 'w':#play til win
        while(pyautogui.locateOnScreen('online/win.png', confidence=0.9) is None):
            restart = False
            readGrid()
            while(bigFound == False):
                if not randomClick():
                    unlucky += 1
                    #pyautogui.click(x,y)
                    mouse.move(x,y)
                    mouse.click(Button.left, 1)
                    time.sleep(sleep)
                    #print("Oops I messed up")
                    restart = True
                    break
            if restart:
                continue

            while(pyautogui.locateOnScreen('online/smile.png', confidence=0.9) is not None):
                if not makeClicks():
                    break
            if pyautogui.locateOnScreen('online/sad.png', confidence=0.9) is not None:
                losses += 1
                print("Bombs Found: ", bombsFound)
                #pyautogui.click(x,y)
                mouse.move(x,y)
                mouse.click(Button.left, 1)
                time.sleep(sleep)
                #print("Oops I messed up")
        print("I won GGEZ")
        print("Losses: ", losses)
        print("Unlucky: ", unlucky)

    if games == 'i':
        while(True):
            if not paused:
                restart = False
                readGrid()
                while(bigFound == False):
                    if not randomClick():
                        print("Oops I messed up")
                        unlucky += 1
                        print("Unlucky: ", unlucky, "Losses: ", losses, " Wins: ", wins)
                        #pyautogui.click(x,y)
                        mouse.move(x,y)
                        mouse.click(Button.left, 1)
                        time.sleep(sleep)
                        restart = True
                        break
                if restart:
                    continue

                while(pyautogui.locateOnScreen('online/smile.png', confidence=0.9) is not None):
                    if not makeClicks():
                        break

                if pyautogui.locateOnScreen('online/sad.png', confidence=0.9) is not None:
                    #pyautogui.click(x,y)
                    mouse.move(x,y)
                    mouse.click(Button.left, 1)
                    time.sleep(sleep)
                    losses += 1
                    print("Bombs Found: ", bombsFound)
                    print("Oops I messed up")
                    print("Unlucky: ", unlucky, "Losses: ", losses, " Wins: ", wins)
                if pyautogui.locateOnScreen('online/win.png', confidence=0.9) is not None:
                    #pyautogui.click(x,y)
                    mouse.move(x,y)
                    mouse.click(Button.left, 1)
                    time.sleep(sleep)
                    wins += 1
                    print("Bombs Found: ", bombsFound)
                    print("I won GGEZ")
                    print("Unlucky: ", unlucky, "Losses: ", losses, " Wins: ", wins)
            #time.sleep(0.1)


mouse = MouseController()
paused = True
thread = None

with Listener(on_press=on_press) as listener:
    listener.join()

if __name__ == "__main__":
    main()