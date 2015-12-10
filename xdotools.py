import subprocess

xdt = 'xdotool'

def call(fun):
    def wrapper(*args):
        proc = subprocess.run([xdg] + fun(*args))
        if proc.returncode == 0:
            return proc
        else:
            return None

class Mouse:
    class BUTTON:
        LEFT = 1
        MIDDLE = 2
        RIGHT = 3
        WHEEL_UP = 4
        WHEEL_DOWN = 5
        
    def __init__(self):
        self.update_position()

    def updateAfter(fun):
        def fun_wrapper(this, *args):
            args = [xdt] + fun(this, *args) + ['getmouselocation']
            proc = subprocess.run(args,
                                  stdout=subprocess.PIPE,
                                  universal_newlines=True)
            if proc.returncode == 0:
                out = proc.stdout.split()
                this.x = int(out[0].split(':')[1])
                this.y = int(out[1].split(':')[1])
            else:
                this.x = 0
                this.y = 0
        return fun_wrapper
            

    @updateAfter
    def relative(self, dx, dy):
        dxstr, dystr = str(dx), str(dy)
        return ['mousemove_relative', '--', dxstr, dystr]
    
    @updateAfter
    def absolute(self, x, y):
        xstr, ystr = str(x), str(y)
        return ['mousemove', xstr, ystr]

    @call
    def click(self, button=BUTTON.LEFT):
        return ['click', str(button)]

    @updateAfter
    def update_position(self):
        return []
    
class Key:
    ALT = 'alt'
    CTRL = 'ctrl'
    SHIFT = 'shift'
    SUPER = 'super'
    META = 'meta'
    LEFT = 'Left'
    RIGHT = 'Right'
    UP = 'Up'
    DOWN = 'Down'

    @call
    def key(self, keys):
        return ['key', '+'.join(keys)]

    @call
    def keydown(self, key):
        return ['keydown', key]

    @call
    def keyup(self, keys):
        return ['keyup', key]

mouse = Mouse()
key = Key()
