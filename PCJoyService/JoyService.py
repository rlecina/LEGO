import asyncio
import ctypes
import struct
import pyjoystick.sdl2
import sdl2
from bleak import BleakScanner, BleakClient
from contextlib import suppress
from pyjoystick.sdl2 import Key, JoystickEventLoop
from Ps4Joy.JoyState import JoyState, PS4JoyAxisId, PS4JoyButtonId
from queue import SimpleQueue

# Replace this with the name of your hub if you changed
# it when installing the Pybricks firmware.
HUB_NAME = "PyBichi"

class TerminateTaskGroup(Exception):
    """Exception raised to terminate a task group."""

class Joy:
    def __init__(self):
        self._last_known_state = JoyState()

    def print_add(self, joy):
        print('Added', joy)
        return True

    def print_remove(self, joy):
        print('Removed', joy)
        return True

    def key_received(self, key):
        if key.keytype == Key.BUTTON:
            self._last_known_state.set_button(PS4JoyButtonId(key.number), key.value > 0)
        elif key.keytype == Key.AXIS:
            self._last_known_state.set_axis(PS4JoyAxisId(key.number), key.value)

    def serialize(self):
        return self._last_known_state.serialize(struct.pack)



async def run_joy_update(joy: Joy):
    EventLoop = JoystickEventLoop(add=lambda sdljoy: joy.priny_add(sdljoy), 
                                remove=lambda sdljoy: joy.print_remove(sdljoy), 
                                handle_key=lambda key: joy.key_received(key),
                                key_from_event=None,
                                alive=None, 
                                event=None,
                                timeout=0)
    if not pyjoystick.sdl2.get_init():
        pyjoystick.sdl2.init()
    try:
        EventLoop.alive.set()
    except (AttributeError, Exception):
        pass

    while EventLoop.is_alive():
        # Wait for an event
        if sdl2.SDL_WaitEventTimeout(ctypes.byref(EventLoop.event), EventLoop.timeout) != 0:
            EventLoop.call_event(EventLoop.event)
        await asyncio.sleep(0)

class CommandHandler:
    PYBRICKS_COMMAND_EVENT_CHAR_UUID = "c5f50002-8280-46da-89f4-6d8051e4aeef"

    def __init__(self, joy: Joy,):
        self.queue = SimpleQueue()
        self.cmd_available = asyncio.Semaphore(0)
        self.joy = joy
        self.loop = True

    def handle_disconnect(self, client: BleakClient):
        print("Hub was disconnected.")

        # If the hub disconnects before this program is done,
        # cancel this program so it doesn't get stuck waiting
        # forever.
        self.queue.put(b"kill")
        self.cmd_available.release()

    def handle_rx(self, _, data: bytearray):
        if data[0] == 0x01:  # "write stdout" event (0x01)
            payload = data[1:]
            #print("Received:", payload)
            self.queue.put(payload)
            self.cmd_available.release()

    # Shorthand for sending some data to the hub.
    async def send(self, client, data):
        #print("Send:", data)
        # Send the data to the hub.
        await client.write_gatt_char(
            CommandHandler.PYBRICKS_COMMAND_EVENT_CHAR_UUID,
            b"\x06" + data,  # prepend "write stdin" command (0x06)
            response=True
        )

    async def start_program(self, client):
        await client.write_gatt_char(
            CommandHandler.PYBRICKS_COMMAND_EVENT_CHAR_UUID,
            b"\x01", # send "start user program" command (0x01)
            response=True)

    async def stop_program(self, client):
        await client.write_gatt_char(
            CommandHandler.PYBRICKS_COMMAND_EVENT_CHAR_UUID,
            b"\x00", # send "stop user program" command (0x00)
            response=True)

    async def Run(self):
        # Do a Bluetooth scan to find the hub.
        device = await BleakScanner.find_device_by_name(HUB_NAME)

        if device is None:
            print(f"could not find hub with name: {HUB_NAME}")
            raise TerminateTaskGroup
        print(f"Device found!: {HUB_NAME}")

        # Connect to the hub.
        async with BleakClient(device, lambda client: self.handle_disconnect(client) ) as client:

            # Subscribe to notifications from the hub.
            await client.start_notify(CommandHandler.PYBRICKS_COMMAND_EVENT_CHAR_UUID, 
                                          lambda client, data: self.handle_rx(client, data))

            # Tell user to start program on the hub.
            print("Starting the program on the hub.")
            await self.start_program(client)

            # Send a few messages to the hub.
            while self.loop:
                # Wait for hub to say that it is ready to receive data.
                await self.cmd_available.acquire()
                command = self.queue.get()
                if command == b"joy": 
                    await self.send(client, self.joy.serialize())
                elif command == b"kill":
                    await self.stop_program(client)
                    self.loop = False
                else:
                    print("Received:", command.decode("ascii"))
            # Hub disconnects here when async with block exits.
        raise TerminateTaskGroup

async def run_command_handler(joy: Joy):
    ch = CommandHandler(joy)
    await ch.Run()


async def main():
    joy = Joy()

    with suppress(ExceptionGroup, TerminateTaskGroup):
        async with asyncio.TaskGroup() as tg:
            tg.create_task(run_command_handler(joy))
            tg.create_task(run_joy_update(joy))

    return 0

# Run the main async program.
if __name__ == "__main__":
    with suppress(asyncio.CancelledError):
        asyncio.run(main())
