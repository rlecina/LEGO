from micropython import kbd_intr
from uselect import poll
from pybricks.tools import wait, StopWatch
from Ps4Joy.JoyState import JoyState, PS4JoyAxisId, PS4JoyButtonId
import ustruct
from usys import stdin, stdout

class RemoteJoystick:
    def __init__(self, timeout=100):
        kbd_intr(-1)
        self._state = JoyState()
        self._time = None
        self._timeout = timeout
        self._keyboard = poll()
        self._keyboard.register(stdin)
        self._btn_mask = 0

    def _update(self):
        stdout.buffer.write(b"joy")
        command = stdin.buffer.read(8)
        self._state = JoyState.deserialize(command, ustruct.unpack)
        self._btn_mask &= self._state.get_button_mask()

    async def update(self):
        self._update()
        await wait(self._timeout)

    def try_update(self):
        if self._time == None:
            self._time = StopWatch()
        elif self._time.time() < self._timeout:
            return
        self._update()
        self._time.reset()

    def get_button(self, btn: PS4JoyButtonId):
        return self._state.get_button(btn)
    
    def get_button_press(self, btn: PS4JoyButtonId):
        mask = (1 << btn.index())
        if self._btn_mask & mask:
            return False
        state = self._state.get_button(btn) 
        if state:
            self._btn_mask |= (1 << btn.index())
        return state

    def get_axis(self, axis: PS4JoyAxisId):
        return self._state.get_axis(axis)

