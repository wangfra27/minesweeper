import sys


width = 0
height = 0
grid = 0
corners = 0
squareSize = 0

cleared = []

#3d array
aPossible = []
#2d array
possible = []

bigFound = False

totalBombs = 0
flags = 0

def main():
    from main import run
    run(sys.argv)

if __name__ == "__main__":
    main()
