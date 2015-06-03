#requires python3

from random import randrange as rand

import sys

################################################################################
#http://code.activestate.com/recipes/577977-get-single-keypress/
# try:
#     import tty, termios
# except ImportError:
#     # Probably Windows.
#     try:
#         import msvcrt
#     except ImportError:
#         # FIXME what to do on other platforms?
#         # Just give up here.
#         raise ImportError('getch not available')
#     else:
#         getch = msvcrt.getch
# else:
#     def getch():
#         """getch() -> key character

#         Read a single keypress from stdin and return the resulting character. 
#         Nothing is echoed to the console. This call will block if a keypress 
#         is not already available, but will not wait for Enter to be pressed. 

#         If the pressed key was a modifier key, nothing will be detected; if
#         it were a special function key, it may return the first character of
#         of an escape sequence, leaving additional characters in the buffer.
#         """
#         fd = sys.stdin.fileno()
#         old_settings = termios.tcgetattr(fd)
#         try:
#             tty.setraw(fd)
#             ch = sys.stdin.read(1)
#         finally:
#             termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
#         return ch

import tty
import termios
import fcntl
import os
import time

#http://ballingt.com/nonblocking-stdin-in-python-3
class raw(object):
    def __init__(self, stream):
        self.stream = stream
        self.fd = self.stream.fileno()
    def __enter__(self):
        self.original_stty = termios.tcgetattr(self.stream)
        tty.setcbreak(self.stream)
    def __exit__(self, type, value, traceback):
        termios.tcsetattr(self.stream, termios.TCSANOW, self.original_stty)

class nonblocking(object):
    def __init__(self, stream):
        self.stream = stream
        self.fd = self.stream.fileno()
    def __enter__(self):
        self.orig_fl = fcntl.fcntl(self.fd, fcntl.F_GETFL)
        fcntl.fcntl(self.fd, fcntl.F_SETFL, self.orig_fl | os.O_NONBLOCK)
    def __exit__(self, *args):
        fcntl.fcntl(self.fd, fcntl.F_SETFL, self.orig_fl)
################################################################################

class Maze(object):

	def __init__(self):
		try:
			self.width = (int(input('Enter width: ')) * 2 + 1)
			self.height = (int(input('Enter height: ')) * 2 + 1)
		except ValueError:
			print('Invalid size. Dimensions must be integers.')
			sys.exit()

		self.maze = []
		for y in range(self.height):
			row = []
			for x in range(self.width):
				row.append(False)
			self.maze.append(row)

		#Position of player. Begins at impossible value so it will not print if not set correctly.
		self.xPos = -1
		self.yPos = -1

	def isPath(self, x, y):
		return self.maze[y][x]

	def fillmaze(self, x, y):
		path = [(x, y)]

		while len(path) > 0:
			x = path[len(path) - 1][0]
			y = path[len(path) - 1][1]
			self.maze[y][x] = True

			#Get unassigned neighbors
			neighbours = []
			if (x > 1) and (self.isPath(x - 2, y) == False):
				neighbours.append((x - 2, y))
			if (x < self.width - 2) and (self.isPath(x + 2, y) == False):
				neighbours.append((x + 2, y))
			if (y > 1) and (self.isPath(x, y - 2) == False):
				neighbours.append((x, y - 2))
			if (y < self.height - 2) and (self.isPath(x, y + 2) == False):
				neighbours.append((x, y + 2))

			#Make path to random neighbour if one exists
			if len(neighbours) > 0:
				nextTile = neighbours[rand(len(neighbours))]
				self.maze[int((y + nextTile[1]) / 2)][int((x + nextTile[0]) / 2)] = True
				path.append(nextTile)
			#Else remove current tile from stack
			else:
				path.pop()

	def play(self):
		self.xPos = 1
		self.yPos = 1
		os.system('clear')
		print("Use arrow keys to move. Win by reaching the (En)d.")
		time.sleep(3)
		while (True):
			print(self)

			#Check if you reached finish
			if (self.xPos == self.width - 2 and self.yPos == self.height - 2):
				return

			#Get nonblocking input
			with raw(sys.stdin):
				with nonblocking(sys.stdin):
					command = ""
					current = sys.stdin.read(1)
					while not current:
						time.sleep(.05)
						current = sys.stdin.read(1)
					while current:
						command += current
						current = sys.stdin.read(1)

			#http://stackoverflow.com/questions/22397289/finding-the-values-of-the-arrow-keys-in-python-why-are-they-triples
			#Deal with input
			if command =='\x1b[A':
				if self.yPos > 1 and self.isPath(self.xPos, self.yPos - 1):
					self.yPos -= 2
			elif command =='\x1b[B':
				if self.yPos < self.height - 2 and self.isPath(self.xPos, self.yPos + 1):
					self.yPos += 2
			elif command =='\x1b[C':
				if self.xPos < self.width - 2 and self.isPath(self.xPos + 1, self.yPos):
					self.xPos += 2
			elif command =='\x1b[D':
				if self.xPos > 1 and self.isPath(self.xPos - 1, self.yPos):
					self.xPos -= 2
			elif command == '\x1b':
				sys.exit()

	def __repr__(self):
		os.system('clear')
		maze = ""
		for y in range(self.height):
			for x in range(self.width):
				if x == self.xPos and y == self.yPos:
					maze += "@@"
				elif x == 1 and y == 1:
					maze += "St"
				elif x == self.width - 2 and y == self.height - 2:
					maze += "Ex"
				elif self.maze[y][x] == True:
					maze += "  "
				else:
					maze += "[]"
			maze += "\n"
		return maze


def main():
	print("Maze generator by Nick Meier")
	while True:
		a = Maze()
		a.fillmaze(1, 1)
		a.play()
		print("Maze completed! Do you want to play again? (y)es or (n)o")
		while (True):
			command = input()
			if (command == "y" or command == "yes"):
				break
			elif (command == "n" or command == "no"):
				return
			else:
				print("invalid command")
				continue

if __name__ == "__main__":
	main()
