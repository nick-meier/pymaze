#run in terminal, currently working on mac, should work on linux, should not work on pc.

from random import randrange as rand

import sys

################################################################################
#http://code.activestate.com/recipes/577977-get-single-keypress/
try:
    import tty, termios
except ImportError:
    # Probably Windows.
    try:
        import msvcrt
    except ImportError:
        # FIXME what to do on other platforms?
        # Just give up here.
        raise ImportError('getch not available')
    else:
        getch = msvcrt.getch
else:
    def getch():
        """getch() -> key character

        Read a single keypress from stdin and return the resulting character. 
        Nothing is echoed to the console. This call will block if a keypress 
        is not already available, but will not wait for Enter to be pressed. 

        If the pressed key was a modifier key, nothing will be detected; if
        it were a special function key, it may return the first character of
        of an escape sequence, leaving additional characters in the buffer.
        """
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch

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
		print("Enter width")	#Make odd (+1 if even)
		self.width = (int(input()) // 2) * 2 + 1
		print("Enter height")
		self.height = (int(input()) // 2) * 2 + 1

		sys.stdout.write("\x1b[8;{rows};{cols}t".format(rows=self.height + 1, cols=self.width * 2))

		def initmaze(w, h):
			maze = []
			for row in range(h):
				maze += [[1] * (w)]
			return maze

		self.maze = initmaze(self.width, self.height)
		self.xpos = -1
		self.ypos = -1

	def fillmaze(self, x, y):
		#while path while neighbours might be cleaner
		position = [x, y]
		path = [[x, y]]
		self.maze[position[1]][position[0]] = 0
		for i in range(self.width * self.height * 10):
			if not path:
				break
			neighbours = []

			if position[0] > 1 and (self.maze[position[1]][position[0] - 2] == 1):
				neighbours.append([x - 2, y, 'W'])
			if position[0] < self.width - 2 and (self.maze[position[1]][position[0] + 2] == 1):
				neighbours.append([x + 2, y, 'E'])
			if position[1] > 1 and (self.maze[position[1] - 2][position[0]] == 1):
				neighbours.append([x, y - 2, 'N'])
			if position[1] < self.height - 2 and (self.maze[position[1] + 2][position[0]] == 1):
				neighbours.append([x, y + 2, 'S'])

			if neighbours:
				temp = neighbours[rand(len(neighbours))]
				position = temp[:2]
				direction = temp[2]

				path += [position]

				if direction == 'W':
					self.maze[y][x - 1] = 0
				elif direction == 'E':
					self.maze[y][x + 1] = 0
				elif direction == 'N':
					self.maze[y - 1][x] = 0
				else:
					self.maze[y + 1][x] = 0

			else:
				position = path.pop()

			x = position[0]
			y = position[1]
			self.maze[position[1]][position[0]] = 0
			print(self)
		self.maze[0][0] = 2
		self.maze[self.height - 1][self.width - 1] = 3
		print(self)

	def play(self):
		self.xpos = 0
		self.ypos = 0
		os.system('clear')
		print("Use arrow keys to move, win by reaching the XX square.")
		time.sleep(5)
		print(self)
		while (True):
			if (self.xpos == self.width - 1 and self.ypos == self.height - 1):
				return
			with raw(sys.stdin):
				with nonblocking(sys.stdin):
					command = ""
					current = sys.stdin.read(1)
					while not current:
						time.sleep(.1)
						current = sys.stdin.read(1)
					while current:
						command += current
						current = sys.stdin.read(1)
			#http://stackoverflow.com/questions/22397289/finding-the-values-of-the-arrow-keys-in-python-why-are-they-triples
			if command =='\x1b[A':
				if self.ypos > 0 and (self.maze[self.ypos - 1][self.xpos] != 1):
					self.ypos -= 1
			elif command =='\x1b[B':
				if self.ypos < self.height - 1 and (self.maze[self.ypos + 1][self.xpos] != 1):
					self.ypos += 1
			elif command =='\x1b[C':
				if self.xpos < self.width - 1 and (self.maze[self.ypos][self.xpos + 1] != 1):
					self.xpos += 1
			elif command =='\x1b[D':
				if self.xpos > 0 and (self.maze[self.ypos][self.xpos - 1] != 1):
					self.xpos -= 1
			elif command == '\x1b':
				sys.exit()
			else:
				print("not an arrow key!")
			print(self)
				

	def __repr__(self):
		os.system('clear')
		for row in range(self.height):
			asciirow = ""
			for index in range(self.width):
				value = self.maze[row][index]
				if (row == self.ypos and index == self.xpos):
					asciirow += "@@"
				#path
				elif value == 0:
					asciirow += "  "
				#wall
				elif value == 1:
					asciirow += "[]"
				#start
				elif value == 2:
					asciirow += "SS"
				#end
				elif value == 3:
					asciirow += "XX"
					return asciirow
			print(asciirow)
		return ""


def main():
	print("Maze generator by Nick Meier")
	exitFlag = False
	while (not exitFlag):
		a = Maze()
		a.fillmaze(0,0)
		a.play()
		print("Maze completed! Do you want to play again? (y)es or (n)o")
		while (True):
			command = input()
			if (command == "y" or command == "yes"):
				break
			elif (command == "n" or command == "no"):
				exitFlag = True
				break
			else:
				print("invalid command")
				continue

if __name__ == "__main__":
	main()
