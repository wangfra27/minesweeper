import pyautogui
import time
import solver
import gridInit
import minesweeper

def run(argv):

    #keyboard = KeyboardController()

    if str(argv[1]) == 'f':
        minesweeper.flags = True
    elif str(argv[1]) == 'nf':
        minesweeper.flags = False
    else:
        print("error1")
        exit(1)

    if str(argv[2]) == 'one':
        games = 'o'
    elif str(argv[2]) == 'win':
        games = 'w'
    elif str(argv[2]) == 'infinite':
        games = 'i'
    else:
        print("error2")
        exit(1)
    
    minesweeper.sleep = int(argv[3])

    x,y = pyautogui.locateCenterOnScreen('smile.png', confidence=0.9)
    losses = 0
    wins = 0
    unlucky = 0

    if games == 'o':#play once
        while not minesweeper.bigFound:
            gridInit.readGrid()
            while(True):
                if not solver.randomClick():
                    unlucky += 1
                    pyautogui.click(x,y)
                    #mouse.move(x,y)
                    #mouse.click(Button.left, 1)
                    time.sleep(minesweeper.sleep)
                    break
                if minesweeper.bigFound:
                    break

        while True:
            if not solver.makeClicks():
                print("Oops I messed up")
                losses += 1
                break

        if losses == 0:
            print("I won GGEZ")
        print("Unlucky: ", unlucky)

    if games == 'w':#play til win
        while wins == 0:
            restart = False
            gridInit.readGrid()
            while(minesweeper.bigFound == False):
                if not solver.randomClick():
                    unlucky += 1
                    pyautogui.click(x,y)
                    #mouse.move(x,y)
                    #mouse.click(Button.left, 1)
                    time.sleep(minesweeper.sleep)
                    #print("Oops I messed up")
                    restart = True
                    break
            if restart:
                continue

            while(pyautogui.locateOnScreen('smile.png', confidence=0.9) is not None):
                if not solver.makeClicks():
                    break
            if pyautogui.locateOnScreen('online/sad.png', confidence=0.9) is not None:
                losses += 1
                print("Bombs Left: ", minesweeper.totalBombs)
                pyautogui.click(x,y)
                #mouse.move(x,y)
                #mouse.click(Button.left, 1)
                time.sleep(minesweeper.sleep)
                #print("Oops I messed up")
        print("I won GGEZ")
        print("Losses: ", losses)
        print("Unlucky: ", unlucky)

    if games == 'i':
        while(True):
            if not minesweeper.paused:
                restart = False
                gridInit.readGrid()
                while(minesweeper.bigFound == False):
                    if not solver.randomClick():
                        print("Oops I messed up")
                        unlucky += 1
                        print("Unlucky: ", unlucky, "Losses: ", losses, " Wins: ", wins)
                        pyautogui.click(x,y)
                        #mouse.move(x,y)
                        #mouse.click(Button.left, 1)
                        time.sleep(minesweeper.sleep)
                        restart = True
                        break
                if restart:
                    continue

                while(pyautogui.locateOnScreen('smile.png', confidence=0.9) is not None):
                    if not solver.makeClicks():
                        break

                if pyautogui.locateOnScreen('online/sad.png', confidence=0.9) is not None:
                    pyautogui.click(x,y)
                    #mouse.move(x,y)
                    #mouse.click(Button.left, 1)
                    time.sleep(minesweeper.sleep)
                    losses += 1
                    print("Bombs Left: ", minesweeper.totalBombs)
                    print("Oops I messed up")
                    print("Unlucky: ", unlucky, "Losses: ", losses, " Wins: ", wins)
                if pyautogui.locateOnScreen('online/win.png', confidence=0.9) is not None:
                    pyautogui.click(x,y)
                    #mouse.move(x,y)
                    #mouse.click(Button.left, 1)
                    time.sleep(minesweeper.sleep)
                    wins += 1
                    print("I won GGEZ")
                    print("Unlucky: ", unlucky, "Losses: ", losses, " Wins: ", wins)
            #time.sleep(0.1)