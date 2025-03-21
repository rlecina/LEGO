from pybricks.hubs import PrimeHub
from pybricks.pupdevices import Motor
from pybricks.parameters import Port, Icon
from pybricks.tools import wait, run_task, multitask

# Standard MicroPython modules
from umath import fabs
from usys import stdout
from Ps4Joy.JoyState import Ps4JoyButtons, Ps4JoyAxis
from Ps4Joy.GamePad import RemoteJoystick

hub = PrimeHub()
motorA = Motor(Port.A)
motorB = Motor(Port.B)
joy = RemoteJoystick(timeout=50)


async def main():
    hub.display.icon(Icon.HAPPY)
    await hub.speaker.play_notes([
                                 "G4/4.", "G4/4", "A4/2.", "G4/2.", "C5/2.", "B4/2.", "R/8",
                                 "G4/4.", "G4/4", "A4/2.", "G4/2.", "D5/2.", "C5/2.", "R/8",
                                 "G4/4.", "G4/4", "G5/2.", "E5/2.", "C5/2.", "B4/2.", "A4/2.", "R/8",
                                 "F5/4.", "F5/4", "E5/2.", "C5/2.", "D5/2.", "C5/1.", "R/8"
                                 ],
                                 tempo=340)

    dead_zone = 0.1
    base_speed = 1000
    turn_speed = 500

    a_speed = 0
    b_speed = 0
    control_mode = 0
    while True:
        joy.try_update()

        if control_mode == 0:
            vert = joy.get_axis(Ps4JoyAxis.L_Vertical)
            horiz = joy.get_axis(Ps4JoyAxis.L_Horizontal)

            if fabs(vert) < dead_zone and fabs(horiz) < dead_zone:
                vert = 0
                horiz = 0

            new_a_speed = vert * base_speed - horiz * turn_speed
            new_b_speed = -vert * base_speed - horiz * turn_speed
        else:
            vert_l = joy.get_axis(Ps4JoyAxis.L_Vertical)
            vert_r = joy.get_axis(Ps4JoyAxis.R_Vertical)

            if fabs(vert_l) < dead_zone:
                vert_l = 0
            if fabs(vert_r) < dead_zone:
                vert_r = 0

            new_a_speed = vert_l * base_speed
            new_b_speed = -vert_r * base_speed

        if new_a_speed != a_speed:
            motorA.run(new_a_speed)
            a_speed = new_a_speed

        if new_b_speed != b_speed:
            motorB.run(new_b_speed)
            b_speed = new_b_speed

        if joy.get_button_press(Ps4JoyButtons.Up):
            base_speed += 100
            turn_speed += 50
        if joy.get_button_press(Ps4JoyButtons.Down):
            base_speed -= 100
            turn_speed -= 50
        if joy.get_button_press(Ps4JoyButtons.Circle):
            stdout.buffer.write(b"kill")
        if joy.get_button_press(Ps4JoyButtons.Triangle):
            control_mode = 0
        if joy.get_button_press(Ps4JoyButtons.Cross):
            control_mode = 1

run_task(main())
