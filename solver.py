import random
import math
import pyautogui
import minesweeper


def getColor(x,y, im1):
    #grey = (198, 198, 198)
    one = (0, 0, 255)
    two = (0, 128, 0)
    three = (255, 0, 0)
    four = (0, 0, 128)
    five = (128, 0, 0)
    six = (0, 128, 128)
    #seven = (24, 24, 24)
    #eight = (128, 128, 128)
    #print("get Color ", x, y)
    a = minesweeper.corners[y][x][0] + (minesweeper.squareSize * 1 / 2)
    b = minesweeper.corners[y][x][1] + (minesweeper.squareSize * 3 / 4)
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
    a = minesweeper.corners[y][x][0] + (minesweeper.squareSize * 3 / 4)
    b = minesweeper.corners[y][x][1] + (minesweeper.squareSize * 1 / 2)
    if (im1.getpixel((int(a), int(b))) == four):
        return 4
    a = minesweeper.corners[y][x][0] + (minesweeper.squareSize * 1 / 2)
    b = minesweeper.corners[y][x][1] + (minesweeper.squareSize * 1 / 4)
    if (im1.getpixel((int(a), int(b))) == (255, 32, 32)):
        return -1
    a = minesweeper.corners[y][x][0] + (minesweeper.squareSize * 1 / 4)
    b = minesweeper.corners[y][x][1] + (minesweeper.squareSize * 1 / 2)
    if (im1.getpixel((int(a), int(b))) == (0, 0, 0)):
        return -2
    a = minesweeper.corners[y][x][0] + 1
    b = minesweeper.corners[y][x][1] + 1
    if (im1.getpixel((int(a), int(b))) == (255, 255, 255)):
        return math.inf
    return 0

def randomClick():
    if minesweeper.bigFound:
        print("randomClick")
    #print(minesweeper.grid)
    x = random.randint(0, minesweeper.width-1)
    y = random.randint(0, minesweeper.height-1)
    while (minesweeper.grid[y][x] != math.inf):
        x = random.randint(0, minesweeper.width-1)
        y = random.randint(0, minesweeper.height-1)
    pyautogui.click(minesweeper.corners[y][x][0], minesweeper.corners[y][x][1])
    #mouse.move(minesweeper.corners[y][x][0], minesweeper.corners[y][x][1])
    #mouse.click(Button.left, 1)
    im1 = pyautogui.screenshot()
    if not updateTile(x,y,im1):
        return False
    return True

def inrange(x,y):
    if x >= 0 and y >= 0 and x < minesweeper.width and y < minesweeper.height:
        return True
    return False

def updateTile(x,y,im1):
    #print("update Tile ", x, y)
    num = getColor(x,y,im1)
    if num == -2:
        return False
    minesweeper.grid[y][x] = num
    if (num == 0):
        minesweeper.bigFound = True
        insert = (x,y)
        minesweeper.cleared.append(insert)
        for a in range (x-1, x+2):
            for b in range (y-1, y+2):
                check = (a,b)
                if inrange(a,b) and minesweeper.cleared.count(check) == 0 and minesweeper.grid[b][a] == math.inf:
                    if not updateTile(a,b,im1):
                        return False
    return True

def makeClicks():
    #print("makeClicks")
    change = False
    for x in range (0, minesweeper.width):
        for y in range (0, minesweeper.height):
            if minesweeper.grid[y][x] != 0 and minesweeper.grid[y][x] != math.inf:
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
    minesweeper.possible = []
    #3d
    minesweeper.aPossible = []

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
        tempgrid = minesweeper.grid.copy()
        possibility = [0] * len(sections[i])
        allPossible(sections[i], used[i], tempgrid, possibility, blanksFor[i], 0)
        #print("Generated ", len(possible), " possibilities") #this count doesnt do what i want, doesnt chack optimization
        minesweeper.aPossible.append(minesweeper.possible)
        minesweeper.possible = []
    #print(minesweeper.aPossible)
    
    if len(minesweeper.aPossible) == 1:
        for p in minesweeper.aPossible[0]:
            if (sum(p) > minesweeper.totalBombs):
                minesweeper.aPossible.remove(p)

    #counts how many times each square is a mine
    #2d array
    totals = []
    for i in range(0, len(minesweeper.aPossible)):
        if len(minesweeper.aPossible[i]) == 0:
            #this shouldn't happen
            print("ERROR2: NO possible ARRANGEMENT OF MINES FOR SECTION", i)
            print(sections[i])
            print()
            continue
        input = [0] * len(minesweeper.aPossible[i][0])
        for j in minesweeper.aPossible[i]:
            for k in range(0, len(j)):
                input[k] += j[k]
        input = [l / len(minesweeper.aPossible[i]) for l in input]
        totals.append(input)
    """ for x in range(0, len(minesweeper.aPossible)):
        print("Possibility ", x, ": ", minesweeper.aPossible[x]) """
    #print("Percentages:")
    print(totals)
    print()
    
    #find 0s and 100s
    for i in range(0, len(totals)):
        for j in range(0, len(totals[i])):
            if totals[i][j] == 0:
                x = sections[i][j][0]
                y = sections[i][j][1]
                pyautogui.click(minesweeper.corners[y][x][0], minesweeper.corners[y][x][1])
                #mouse.move(minesweeper.corners[y][x][0], minesweeper.corners[y][x][1])
                #mouse.click(Button.left, 1)
                im1 = pyautogui.screenshot()
                #print("Clicking: ", x, y)
                if not updateTile(x,y,im1):
                    return False
                change = True
            elif totals[i][j] == 1:
                x = sections[i][j][0]
                y = sections[i][j][1]
                #print("Flagging: ", x, y)
                if minesweeper.flags == True:
                    pyautogui.rightClick(minesweeper.corners[y][x][0], minesweeper.corners[y][x][1])
                    #mouse.move(minesweeper.corners[y][x][0], minesweeper.corners[y][x][1])
                    #mouse.click(Button.right, 1)
                minesweeper.grid[y][x] = -1
                minesweeper.totalBombs -= 1
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
            if minesweeper.flags == True:
                pyautogui.rightClick(minesweeper.corners[y][x][0], minesweeper.corners[y][x][1])
                #mouse.move(minesweeper.corners[y][x][0], minesweeper.corners[y][x][1])
                #mouse.click(Button.right, 1)
            minesweeper.grid[y][x] = -1
            minesweeper.totalBombs -= 1
        else: #click smallest
            x = sloc[0]
            y = sloc[1]
            #print("Clicking: ", x, y)
            pyautogui.click(minesweeper.corners[y][x][0], minesweeper.corners[y][x][1])
            #mouse.move(minesweeper.corners[y][x][0], minesweeper.corners[y][x][1])
            #mouse.click(Button.left, 1)
            im1 = pyautogui.screenshot()
            if not updateTile(x,y,im1):
                return False
    return True

def allPossible(section, use, tempgrid, possibility, blanksFor, it):
    #section and use are array of pairs
    if it == len(possibility):
        if checkViolations(tempgrid, use, section):
            minesweeper.possible.append(possibility.copy())
        """ else:
            print(possibility) """
        return
    possibility[it] = 0
    allPossible(section, use, tempgrid.copy(), possibility.copy(), blanksFor, it+1)

    tempgrid[section[it][1]][section[it][0]] = -1
    possibility[it] = 1
    if checkTooMany(tempgrid, use, section[0:it+1], blanksFor):
        allPossible(section, use, tempgrid.copy(), possibility.copy(), blanksFor, it+1)

# initial check for pruning purposes
# true if no violations
# IF we also input an array of already checked squares by marking squares as checked if they pass the 2nd check
def checkTooMany(tempgrid, used, soFar, blanksFor):
    x = 0
    for u in used:
        mines = 0
        check = True
        for a in range (u[0]-1, u[0]+2):
            for b in range (u[1]-1, u[1]+2):
                if inrange(a,b) and tempgrid[b][a] == -1:
                    mines += 1
        if mines > tempgrid[u[1]][u[0]]:
            #print("1 Pruned ", u, " with ", mines)
            return False
        for s in blanksFor[x]:
            if (soFar.count(s)) == 0:
                check = False
                break
        if check:
            #print("check activated")
            if mines != tempgrid[u[1]][u[0]]:
                #print("2 Pruned ", u, " with ", mines, " used ", soFar, " and ", blanksFor)
                return False
        x+=1

    return True

# final check
# true if no violations
def checkViolations(tempgrid, used, section):
    for u in used:
        blank = 0
        mines = 0
        for a in range (u[0]-1, u[0]+2):
            for b in range (u[1]-1, u[1]+2):
                if inrange(a,b) and tempgrid[b][a] == -1:
                    mines += 1
                if inrange(a,b) and tempgrid[b][a] == math.inf and section.count((a,b)) == 0:
                    blank += 1
        if mines > tempgrid[u[1]][u[0]] or tempgrid[u[1]][u[0]] > mines + blank:
            #print("Rejected! Violated ", u[0], u[1])
            return False
    return True

def divideSections(sections,used):
    #og used, contains everything in used in one container, used divides into sections, trash contains blanks
    trash = []
    #to prevent repeats
    for x in range (0, minesweeper.width):
        for y in range (0, minesweeper.height):
            if minesweeper.grid[y][x] == math.inf and active(x,y) and trash.count((x,y)) == 0:
                s=[]
                t=[]
                section(x,y,t,trash)
                # s is all numbers in the section
                # t is all blanks in the section
                for i in t:
                    for a in range (i[0]-1, i[0]+2):
                        for b in range (i[1]-1, i[1]+2):
                            if inrange(a,b) and minesweeper.grid[b][a] > 0 and minesweeper.grid[b][a] != math.inf and s.count((a,b)) == 0:
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
            if trash.count((a,b)) == 0 and inrange(a,b) and minesweeper.grid[b][a] == math.inf and active(a,b):
                section(a,b,t,trash)
            elif inrange(a,b) and minesweeper.grid[b][a] != math.inf and minesweeper.grid[b][a] > 0 and activeNum(a,b,trash):
                for c in range (a-1, a+2):
                    for d in range (b-1, b+2):
                        if inrange(a,b) and minesweeper.grid[b][a] == math.inf and trash.count((a,b)) == 0:
                            section(c,d,t,trash)

def active(x,y):
    #True if next to a number
    for a in range (x-1, x+2):
        for b in range (y-1, y+2):
            if inrange(a,b) and minesweeper.grid[b][a] > 0 and minesweeper.grid[b][a] != math.inf:
                return True
    return False

def activeNum(x,y,trash):
    #True if next to a blank
    for a in range (x-1, x+2):
        for b in range (y-1, y+2):
            if inrange(a,b) and minesweeper.grid[b][a] == math.inf and trash.count((a,b)) == 0:
                return True
    return False

def advTactics1():
    #print("advtactics1")
    change = False
    tempgrid = minesweeper.grid.copy()
    #make a tempgrid with minimized numbers
    for x in range (0, minesweeper.width):
        for y in range (0, minesweeper.height):
            if tempgrid[y][x] > 0 and tempgrid[y][x] != math.inf:
                for a in range (x-1, x+2):
                    for b in range (y-1, y+2):
                        if inrange(a,b) and tempgrid[b][a] == -1:
                            tempgrid[y][x] -= 1
    #print(tempgrid)

    # for each number
    for x in range (0, minesweeper.width):
        if change == True: 
            break
        for y in range (0, minesweeper.height):
            if change == True: 
                break
            if tempgrid[y][x] > 0 and tempgrid[y][x] != math.inf:
                #for each number touching that number
                for a in range (x-1, x+2):
                    if change == True: 
                        break
                    for b in range (y-1, y+2):
                        if change == True: 
                            break
                        if inrange(a,b) and tempgrid[b][a] > 0 and tempgrid[b][a] != math.inf:
                            #count the number of independent squares
                            ind = []
                            for c in range (a-1, a+2):
                                for d in range (b-1, b+2):
                                    if inrange(c,d) and tempgrid[d][c] == math.inf:
                                        if notTouching(x,y,c,d):
                                            ind.append((c,d))
                            #if the number of independent squares = diff between two numbers, mark all independent squares as flag
                            if len(ind) > 0 and (len(ind) == tempgrid[b][a] - tempgrid[y][x]):
                                #print("1 2 Tactics Used: (", a, ", ", b, ") and (", x, ", ", y, ")")
                                change = True
                                for i,j in ind:
                                    #print("Flagged ", i, j)
                                    if minesweeper.flags == True:
                                        pyautogui.rightClick(minesweeper.corners[j][i][0], minesweeper.corners[j][i][1])
                                        #mouse.move(minesweeper.corners[j][i][0], minesweeper.corners[j][i][1])
                                        #mouse.click(Button.right, 1)
                                    minesweeper.totalBombs -= 1
                                    minesweeper.grid[j][i] = -1
                                    tempgrid[j][i] = -1
    return change

def advTactics2():
    #print("advtactics2")
    change = False
    tempgrid = minesweeper.grid.copy()
    #make a tempgrid with minimized numbers
    for x in range (0, minesweeper.width):
        for y in range (0, minesweeper.height):
            if tempgrid[y][x] > 0 and tempgrid[y][x] != math.inf:
                for a in range (x-1, x+2):
                    for b in range (y-1, y+2):
                        if inrange(a,b) and tempgrid[b][a] == -1:
                            tempgrid[y][x] -= 1
    # for each number
    for x in range (0, minesweeper.width):
        if change == True: 
            break
        for y in range (0, minesweeper.height):
            if change == True: 
                break
            if tempgrid[y][x] > 0 and tempgrid[y][x] != math.inf:
                #for each number touching that number
                for a in range (x-1, x+2):
                    if change == True: 
                        break
                    for b in range (y-1, y+2):
                        if change == True: 
                            break
                        if inrange(a,b) and tempgrid[b][a] > 0 and tempgrid[b][a] != math.inf:
                            #count the number of independent and dependent squares
                            ind = []
                            dep = []
                            for c in range (a-1, a+2):
                                for d in range (b-1, b+2):
                                    if inrange(c,d) and tempgrid[d][c] == math.inf:
                                        if notTouching(x,y,c,d):
                                            ind.append((c,d))
                                        else: 
                                            dep.append((c,d))
                            if (not samePoint(x,y,a,b) and len(ind) == 0 and len(dep) == 2 and tempgrid[b][a] == 1 and tempgrid[y][x] == 1):
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
    if inrange(i, j) and minesweeper.grid[j][i] == math.inf:
        change = True
        #print("click ", i, j)
        pyautogui.click(minesweeper.corners[j][i][0], minesweeper.corners[j][i][1])
        #mouse.move(minesweeper.corners[j][i][0], minesweeper.corners[j][i][1])
        #mouse.click(Button.left, 1)
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
    flag = 0
    blanks = 0
    change = False
    for a in range (x-1, x+2):
        for b in range (y-1, y+2):
            if inrange(a,b):
                if minesweeper.grid[b][a] == math.inf:
                    blanks += 1
                elif minesweeper.grid[b][a] == -1:
                    flag += 1
    if (flag + blanks == minesweeper.grid[y][x]) and blanks > 0:
        #print("flagAround")
        change = True
        for a in range (x-1, x+2):
            for b in range (y-1, y+2):
                if inrange(a,b) and minesweeper.grid[b][a] == math.inf:
                    if minesweeper.flags == True:
                        pyautogui.rightClick(minesweeper.corners[b][a][0], minesweeper.corners[b][a][1])
                        #mouse.move(minesweeper.corners[b][a][0], minesweeper.corners[b][a][1])
                        #mouse.click(Button.right, 1)
                    minesweeper.grid[b][a] = -1
                    minesweeper.totalBombs -= 1
    return change

def clickAround(x,y):
    minesweeper.flags = 0
    blanks = 0
    change = False
    for a in range (x-1, x+2):
        for b in range (y-1, y+2):
            if inrange(a,b) and minesweeper.grid[b][a] == -1:
                minesweeper.flags += 1
            elif inrange(a,b) and minesweeper.grid[b][a] == math.inf:
                blanks += 1
    if minesweeper.flags == minesweeper.grid[y][x] and blanks > 0:
        #print("clickAround")
        change = True
        for a in range (x-1, x+2):
            for b in range (y-1, y+2):
                if inrange(a,b) and minesweeper.grid[b][a] == math.inf:
                    pyautogui.click(minesweeper.corners[b][a][0], minesweeper.corners[b][a][1])
                    #mouse.move(minesweeper.corners[b][a][0], minesweeper.corners[b][a][1])
                    #mouse.click(Button.left, 1)
                    im1 = pyautogui.screenshot()
                    if not updateTile(a,b,im1):
                        return False, change
    return True, change