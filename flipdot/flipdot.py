import random
import time

from .framebuf import FrameBuffer
from .fonts import Font
from . import GPIO
from furvester import Furvester

DEADPIXEL = (45,5)

class FlipDot(FrameBuffer):
    def __init__(self, height: int = 7, width: int = 84, panels: int = 3, upside_down: bool = True) -> None:
        """
        :param height:
        Height of the display in pixels
        :param width:
        Width of the display in pixels
        :param panels:
        Number of panels in the display
        :param upside_down:
        Turns the whole display by 180°
        """
        self.height = height
        self.width = width
        self.panels = panels
        self.panelwidth = self.width // self.panels
        self.upside_down = upside_down

        self.pulsetime = 250  # length of enable pulse in µs - 250µs works reliable. Avoid too long!!!
        self.powerTimeout = 2000  # how long to keep flipdot VS on after the last update (in ms)
        self.power = False  # state of flipdot VS
        self.mode = "dayclock"
        self.lastUpdate = time.time_ns()
        self.lastClock = time.time()
        self.lastText = ""
        self.standby = False
        self.furvester = Furvester(self)

        # Pin initialization
        self.pins = {}
        self._init_pins()

        # Initialize Fonts
        self.fonts = {
            "mono": Font("narrow", mono=True),
            "variable": Font("narrow", mono=False),
        }
        self.font = "variable"  # selected font
        self.align = "center"  # default alignment

        # Initialize Framebuffer
        super().__init__(self.width, self.height)
        self.fill(0)

        # Initialize second framebuffer to store display state - this is used to only flip changed pixels on the display
        self.lastBuffer = FrameBuffer(self.width, self.height)
        self.lastBuffer.fill(1)

        # Keep track of the current state to save time when row, column and/or color don't change
        self.lastRow = -1
        self.lastColumn = -1
        self.lastColor = -1

        # Clear the display
        self.clear()
        self.show()

        print("Display Ready")

    def text(self, text: str, align: str = None, clear: bool = True,
             show: bool = True, font: str = None, vpos: int = 0, cutoff: bool = True) -> None:
        """
        Display text on the display
        :param cutoff:
        Cut off text if too long for the display
        :param text:
        The text to display. Expects a string
        :param align:
        Alignment on the display. Expects "left", "center" or "right"
        :param clear:
        clear the display before adding the text?
        :param show:
        show immediately? disable if you want to use an effect
        :param font:
        font to be used
        :param vpos:
        vertical position of the first pixel
        """
        if align is None:
            align = self.align
        elif align not in ["left", "center", "right"]:
            raise ValueError("align must be left, center or right")
        # write text to framebuffer
        if clear:
            self.clear()

        if font is None:
            font = self.font

        buf = self.fonts[font].text(text)
        if cutoff:
            cuttext = text
            while buf.width > self.width:
                cuttext = cuttext[:-1]
                print(text)
                buf = self.fonts[font].text(cuttext + "...")
        self.copy_buffer(buf, self._x_align(buf.width, align), vpos)

        if show:
            self.show()

        self.lastText = text

    def ticker(self, text: str, font=None) -> None:
        """
        Display text in newsticker style, slowly running it over the display
        :param text:
        Text to display
        :param font:
        font to be used
        """
        if font is None:
            font = self.font
        textbuf, width, height = self.fonts[font].text(text)
        self.clear()
        self.show()
        step = 0
        for i in range(self.width + width):
            pos_x = self.width - step
            # self.fill(0)
            self.copy_buffer(textbuf, pos_x, 0)
            self.show()
            # time.sleep(0.1 / speed)
            step += 1

    def show(self, keyframe: bool = False, slow: bool = False, avoid_dead: bool = True) -> None:
        """
        draw the whole framebuffer to the display
        :param avoid_dead:
        avoid dead pixel on show
        :param keyframe:
        overwrite the whole display, no matter if pixels are already set
        :param slow:
        slow down the process to keep noise a little lower
        :return:
        """
        if avoid_dead:
            self._avoid_dead_pixel()
        for col in range(self.width // self.panels):
            for row in range(self.height):
                for panel in range(self.panels):
                    # check if the selected pixel changed or keyframe is set
                    phycol = col + panel * self.panelwidth
                    if self.get_pixel(phycol, row) != self.lastBuffer.get_pixel(phycol, row) or keyframe is True:
                        self.flip(phycol, row, self.get_pixel(phycol, row))  # flip it
                        if slow:
                            time.sleep(0.01)
        self.lastBuffer.copy_buffer(self, 0, 0)  # after writing the display, store current image for next compare
        self._power_off()

    def _avoid_dead_pixel(self):
        x, y = DEADPIXEL
        if self.get_pixel(x, y):
            if not self.get_pixel(x - 1, y):
                self.scroll(1, 0)
            elif not self.get_pixel(x + 1, y):
                self.scroll(-1, 0)

    def transition_scroll(self, reverse: bool = False) -> None:
        """
        Show the new contents by scrolling them into the display
        :param reverse:
        reverse direction of the animation
        """
        self._avoid_dead_pixel()
        if reverse is True:
            direction = 1
        else:
            direction = -1
        buf = FrameBuffer(self.width, (self.height + 1) * 3)
        buf.copy_buffer(self.lastBuffer, 0, self.height + 1)
        buf.copy_buffer(self, 0, 0)
        buf.copy_buffer(self, 0, (self.height + 1) * 2)
        for _ in range(self.height + 1):
            buf.scroll(0, direction)
            self.copy_buffer(buf, 0, -(self.height + 1))
            self.show(avoid_dead=False)

    def transition_random(self, sleep_between_pixels: float = None, transition_time: float = None) -> None:
        """
        Randomly replace pixels from previous buffer to new one
        :param sleep_between_pixels:
        How long to sleep between each pixel, minimum wait time if set together with
        :param transition_time:
        Time for the whole transition so the animation is played faster the more pixels need to change
        """
        self._avoid_dead_pixel()
        if transition_time is not None:
            diff = self.diff(self.lastBuffer)
            if sleep_between_pixels is None or transition_time / diff > sleep_between_pixels:
                sleep_between_pixels = transition_time / diff
        elif sleep_between_pixels is None:
            sleep_between_pixels = 0.01
        pixels = list(range(82 * 7))
        random.shuffle(pixels)
        for pixel in pixels:
            x = pixel % 82
            y = pixel % 7
            if self.get_pixel(x, y) != self.lastBuffer.get_pixel(x, y):
                self.flip(x, y, self.get_pixel(x, y))  # flip it
                time.sleep(sleep_between_pixels)
        self.lastBuffer.copy_buffer(self, 0, 0)

    def flip(self, column, row, color) -> None:
        """
        Flip a single pixel
        :param column:
        column of the pixel to flip
        :param row:
        row of the pixel to flip
        :param color:
        new color of the pixel
        """
        # make sure power is on
        self._power_on()
        # set one pixel
        if self.upside_down:  # check if the panel is upside-down - if so flip the coordinates
            row = self.height - 1 - row
            column = self.width - 1 - column
        panel = int(column / 28)  # find out which panel we're on
        # timer1 = time.time_ns()
        self._select_column(column)  # set the column bits
        self._select_row(row)  # set the row bits
        self._select_color(color)  # set the color
        self._pulse(panel)  # pulse the enable pin for the right panel
        # timer2 = time.time_ns()
        self.lastUpdate = time.time()
        # print((timer2 - timer1)/1000)

    def clear(self) -> None:
        """
        fill the whole framebuffer with black pixels
        """
        self.lastClock = 0
        self.fill(0)

    def loop(self, standby: bool = False) -> None:
        """
        Update the display with the latest changes
        Run this as often as possible
        :param standby:
        The display will turn black and stop updating on its own, if this is True
        """
        if not standby:
            if self.standby:
                print("Active Mode")
                self.standby = False
            if self.mode == "clock":
                self.clock()
            if self.mode == "dayclock":
                self.dayclock(seconds=False)
            if self.mode == "dayclock2":
                self.dayclock(seconds=True)
            if self.mode == "furvester":
                self.furvester.screen()
        else:
            if not self.standby:
                print("Standby Mode")
                self.clear()
                self.show(slow=True)
                self.standby = True

        if self.lastUpdate + 2 < time.time():
            self._power_off()

    def clock(self) -> None:
        """
        Show a simple clock
        """
        if int(time.time()) != self.lastClock:
            text = time.strftime("%H:%M:%S")
            self.lastClock = int(time.time())
            self.text(text,
                      align="center",
                      font="mono")

    def dayclock(self, seconds: bool = True) -> None:
        """
        Show date and time
        :param seconds:
        Set to True to make the dots between hours and minutes blink
        """
        if int(time.time()) != self.lastClock or seconds:
            self.lastClock = int(time.time())
            if time.time() % 1 >= 0.5 and seconds is True:  # or 0.5 < time.time() % 1 < 0.75:
                text = time.strftime("%a %d. %b %H %M")
            else:
                text = time.strftime("%a %d. %b %H:%M")
            if text != self.lastText:
                self.text(text,
                          align="center",
                          font="variable",
                          show=False)
                self.transition_random(transition_time=1.0, sleep_between_pixels=0.02)

    def stop(self) -> None:
        """
        Clear the display and all GPIOs before shutting down
        """
        self.clear()
        self.show()
        self._power_off()
        GPIO.cleanup()
        del self

    def _power_on(self) -> None:
        # Enable Flip Dot VS if off right now
        if not self.power:
            self.power = True
            self.pins["VsEN"].on()  # enable Vs
            self.pins["RowEN"].off()  # enable row drivers
            # print("Rows ON")

    def _power_off(self) -> None:
        # Disable Flip Dot VS
        if self.power:
            self.power = False
            self.pins["RowEN"].on()  # disable row drivers
            self.pins["VsEN"].off()  # disable Vs
            # print("Rows OFF")

    def _x_align(self, width: int, align: str) -> int:
        # Calculate X-Position for start of item with :width: depending on alignment
        aligns = {
            "left": 0,
            "center": 1,
            "right": 2,
        }
        if align in aligns.keys():
            align = aligns[align]

        if align == 0:
            return 0
        if align == 1:
            return int(self.width / 2) - int(width / 2)
        if align == 2:
            return self.width - width

    def _select_row(self, row: int) -> None:
        # switch row drivers (74HCT238) to the right address
        if row != self.lastRow:  # check if the row actually changed, if not do nothing
            # Set the address bits
            self.pins["RowA0"].value((row >> 0) % 2)
            self.pins["RowA1"].value((row >> 1) % 2)
            self.pins["RowA2"].value((row >> 2) % 2)
            # Store for next run
            self.lastRow = row

    def _select_column(self, column: int) -> None:
        # switch column drivers (FP2800A) to the right address
        if column != self.lastColumn:  # check if the column actually changed, if not do nothing
            # FP2800 is subdivided into 4 "characters" (B0, B1) with 7 "segments" (A0, A1, A2) each
            # Each panel has 28 columns and since all FP2800A are wired in parallel
            # we just need to take care of those 28
            col = column % 28  # find out where we are on this panel
            b = int(col / 7)  # find the right "character"
            a = col % 7 + 1  # find the right "segment" - there is no segment 0
            # Set the address bits
            self.pins["B0"].value((b >> 0) % 2)
            self.pins["B1"].value((b >> 1) % 2)
            self.pins["A0"].value((a >> 0) % 2)
            self.pins["A1"].value((a >> 1) % 2)
            self.pins["A2"].value((a >> 2) % 2)
            # Store for next run
            self.lastColumn = column

    def _select_color(self, color: bool | int) -> None:
        # Switch polarization of the whole grid
        if color != self.lastColor:  # check if the color actually changed, if not do nothing
            self.pins["RowEN"].on()  # disable row drivers
            self.pins["RowSEL"].value(1 - color)  # enable high or low row driver
            self.pins["DATA"].value(color)  # set data bit on column drivers
            self.pins["RowEN"].off()  # enable row drivers
            # Store for next run
            self.lastColor = color

    def _pulse(self, panel: int) -> None:
        # pulse ENABLE pin of <panel> for <pulsetime> µs
        (self.pins["EN0"], self.pins["EN1"], self.pins["EN2"], self.pins["EN3"])[panel].on()
        # time.sleep(self.pulsetime / 1000000)
        # replace sleep with a timestamp controlled loop since that is way more accurate
        timestamp = time.time_ns() + self.pulsetime * 1000
        while timestamp > time.time_ns():
            pass
        (self.pins["EN0"], self.pins["EN1"], self.pins["EN2"], self.pins["EN3"])[panel].off()

    def _init_pins(self) -> None:
        # Initialize all needed GPIO pins
        # Row drivers (74HTC238)
        self.pins["RowA0"] = GPIO.Pin(19, GPIO.Pin.OUT)
        self.pins["RowA1"] = GPIO.Pin(16, GPIO.Pin.OUT)
        self.pins["RowA2"] = GPIO.Pin(26, GPIO.Pin.OUT)
        self.pins["RowSEL"] = GPIO.Pin(21, GPIO.Pin.OUT)
        self.pins["RowEN"] = GPIO.Pin(20, GPIO.Pin.OUT, value=1)  # active low
        # Column drivers (FP2800)
        self.pins["A0"] = GPIO.Pin(13, GPIO.Pin.OUT)
        self.pins["A1"] = GPIO.Pin(12, GPIO.Pin.OUT)
        self.pins["A2"] = GPIO.Pin(6, GPIO.Pin.OUT)
        self.pins["B0"] = GPIO.Pin(7, GPIO.Pin.OUT)
        self.pins["B1"] = GPIO.Pin(8, GPIO.Pin.OUT)
        self.pins["DATA"] = GPIO.Pin(5, GPIO.Pin.OUT)
        # Panel select (by chosing the corresponding EN pin)
        self.pins["EN0"] = GPIO.Pin(10, GPIO.Pin.OUT)
        self.pins["EN1"] = GPIO.Pin(9, GPIO.Pin.OUT)
        self.pins["EN2"] = GPIO.Pin(25, GPIO.Pin.OUT)
        self.pins["EN3"] = GPIO.Pin(23, GPIO.Pin.OUT)
        self.pins["VsEN"] = GPIO.Pin(24, GPIO.Pin.OUT)

