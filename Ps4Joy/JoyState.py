# PS5:
#           L2: Axis 4              R2: Axis 5
#           L1: Btn 9               R1: Btn 10
#
#     Up : Btn 11         ----------          Tri : Btn 3
#  R: Btn 13   L: Btn 14  | Btn 15 |    Sqr: Btn 2  O: Btn 1
#     Down: Btn 12        ----------             X: 0
#  
#            Horiz: Axis 0    Horiz: Axis 2
#            Vert: Axis 1     Vert: Axis 3
#                Btn 7            Btn 8

class PS4JoyButtonId:
    def __init__(self, index):
        self._index = index
    
    def index(self):
        return self._index

class PS4JoyAxisId:
    def __init__(self, index):
        self._index = index
    
    def index(self):
        return self._index

class Ps4JoyButtons:
    Cross = PS4JoyButtonId(0)
    Circle = PS4JoyButtonId(1)
    Square = PS4JoyButtonId(2)
    Triangle = PS4JoyButtonId(3)
    Share = PS4JoyButtonId(4)
    PS = PS4JoyButtonId(5)
    Options = PS4JoyButtonId(6)
    L3 = PS4JoyButtonId(7)
    R3 = PS4JoyButtonId(8)
    L1 = PS4JoyButtonId(9)
    R1 = PS4JoyButtonId(10)
    Up = PS4JoyButtonId(11)
    Down = PS4JoyButtonId(12)
    Right = PS4JoyButtonId(13)
    Left = PS4JoyButtonId(14)
    Pad = PS4JoyButtonId(15)
    Count = 16

class Ps4JoyAxis:
    L_Horizontal = PS4JoyAxisId(0)
    L_Vertical = PS4JoyAxisId(1)
    R_Horizontal = PS4JoyAxisId(2)
    R_Vertical = PS4JoyAxisId(3)
    L2 = PS4JoyAxisId(4)
    R2 = PS4JoyAxisId(5)
    Count = 6

class JoyState:
    def __init__(self):
        self._b = 0
        self._a = [0.0] * Ps4JoyAxis.Count

    def __str__(self):
        return "\n  ".join(("JoyState:", str(self._b), str(self._a)))

    def get_button_mask(self):
        return self._b
    
    def set_button(self, btn: PS4JoyButtonId, pressed: bool):
        if btn.index() >= 0 and btn.index() < Ps4JoyButtons.Count:
            if pressed:
                self._b |= (1 << btn.index())
            else:
                self._b &= ~(1 << btn.index())

    def set_axis(self, axis: Ps4JoyAxis, value: float):
        if axis.index() >= 0 and axis.index() < Ps4JoyAxis.Count:
            self._a[axis.index()] = value

    def get_button(self, btn: PS4JoyButtonId):
        if btn.index() >= 0 and btn.index() < Ps4JoyButtons.Count:
            return (self._b & (1 << btn.index())) != 0
        else:
            return False

    def get_axis(self, axis: Ps4JoyAxis):
        if axis.index() >= 0 and axis.index() < Ps4JoyAxis.Count:
            return self._a[axis.index()]
        else:
            return 0.0 

    def serialize(self, pack):
        tup = (self._b,) + tuple(int((v + 1.0) * 127) for v in self._a)
        return pack('<HBBBBBB', *tup)

    def deserialize(content, unpack):
        tup = unpack('<HBBBBBB', content)
        state = JoyState()
        state._b = tup[0]
        state._a = [(float(c)/127 - 1.0) for c in tup[1:]]
        return state
