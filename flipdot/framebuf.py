class FrameBuffer:
    """
    Partial re-implementation of the Adafruit framebuffer library in pure python tailored for the flipdot display
    """
    def __init__(self, width: int, height: int, buffer: bytearray = None):
        """
        :param width:
        Width in pixels
        :param height:
        Height in pixels
        :param buffer:
        optional pre-filled byte array
        """
        self.width = width
        self.height = height
        self._bufferheight = (self.height - 1) // 8 + 1  # make sure we have enough bytes per column to store the rows
        self.buffersize = self._bufferheight * self.width
        if buffer is None:
            self._buf = bytearray(self.buffersize)
        elif len(buffer) == self.buffersize:
            self._buf = buffer
        else:
            raise BufferError("Imported buffer must have same size as self")

    def fill(self, color: [bool, int] = 0) -> None:
        """
        Fill the whole framebuffer with one color
        :param color:
        Black or White
        """
        self._buf = bytearray([0x00 if color == 0 else 0xFF] * self.buffersize)

    def set_pixel(self, pos_x: int, pos_y: int, color: [bool, int]) -> None:
        """
        Set the pixel at given coordinates to color
        :param pos_x:
        X-Position
        :param pos_y:
        Y-Position
        :param color:
        Color - Black or White
        :return:
        """
        byte, bit = self._get_bit(pos_x, pos_y)
        mask = 1 << bit
        self._buf[byte] &= ~mask
        if color:
            self._buf[byte] |= mask

    def get_pixel(self, pos_x: int, pos_y: int) -> bool:
        """
        Returns the color of the pixel at the given coordinates
        :param pos_x:
        X-Position
        :param pos_y:
        Y-Position
        :return:
        bool: Black (0) or White (1)
        """
        # get the color of pixel at given coordinates
        byte, bit = self._get_bit(pos_x, pos_y)
        return (self._buf[byte] >> bit) % 2

    def pixel(self, pos_x: int, pos_y: int, color: [int, bool] = None) -> int:
        """
        Can be used to get or set a pixel. Always returns the color in that pixel.
        :param pos_x:
        X-Position
        :param pos_y:
        Y-Position
        :param color:
        Color to be set - 0 = Black, 1 = White
        :return:
        Color of the pixel (after setting)
        """
        # get or set a pixel
        if color is None:
            return self.get_pixel(pos_x, pos_y)
        else:
            self.set_pixel(pos_x, pos_y, color)
            return color

    def _get_bit(self, pos_x: int, pos_y: int) -> tuple:
        # returns the bit position of the pixel at given coordinates in the buffer
        if pos_x < 0 or pos_x > self.width:
            raise ValueError("pos_x is out of range")
        if pos_y < 0 or pos_y > self.height:
            raise ValueError("pos_y is out of range")
        byte = pos_x * self._bufferheight + pos_y // 8
        bit = pos_y % 8
        return byte, bit

    def copy_buffer(self, buffer: 'FrameBuffer', pos_x: int, pos_y: int) -> None:
        """
        Copy the contents of :param buffer: into self at given coordinates
        :param buffer:
        Framebuffer object to be copied from
        :param pos_x:
        X-Position
        :param pos_y:
        Y-Position
        """
        for x in range(buffer.width):
            for y in range(buffer.height):
                if pos_x + x in range(self.width) and pos_y + y in range(self.height):
                    self.set_pixel(pos_x + x, pos_y + y, buffer.get_pixel(x, y))

    def scroll(self, offset_x: int, offset_y: int) -> None:
        """
        Scroll the contents of self by offset
        :param offset_x:
        X-Offset
        :param offset_y:
        Y-Offset
        """
        if offset_x < 0:
            shift_x = 0
            xend = self.width + offset_x
            xmove = 1
        else:
            shift_x = self.width - 1
            xend = offset_x - 1
            xmove = -1
        if offset_y < 0:
            y = 0
            yend = self.height + offset_y
            ymove = 1
        else:
            y = self.height - 1
            yend = offset_y - 1
            ymove = -1
        while y != yend:
            x = shift_x
            while x != xend:
                self.set_pixel(
                    x, y, self.get_pixel(x - offset_x, y - offset_y)
                )
                x += xmove
            y += ymove

    def diff(self, compare_to: 'FrameBuffer') -> int:
        """
        Compares this buffer with compare_to and returns the number of different pixels
        :param compare_to:
        Framebuffer object to be compared
        :return:
        Number of different pixels
        """
        diffpixels = 0
        for x in range(self.width):
            for y in range(self.height):
                if self.get_pixel(x, y) != compare_to.get_pixel(x, y):
                    diffpixels += 1
        return diffpixels

    def __str__(self) -> str:
        # return human readable version of the whole buffer
        text = ""
        for row in range(self.height):
            for col in range(self.width):
                if self.pixel(col, row):
                    # print X if pixel is set
                    text += "X"
                else:
                    # print . if pixel is not set
                    text += "."
            text += "\n"  # line break
        return text

    def __repr__(self) -> str:
        return f"<Framebuffer with {self.width} x {self.height} pixels>"


