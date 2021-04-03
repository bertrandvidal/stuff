import unittest
from io import StringIO

from canvas import Terminal, RgbImage
from pixel import Pixel


class TerminalTest(unittest.TestCase):

    def test_display_output(self):
        output_buffer = StringIO()
        terminal = Terminal(3, output_buffer)
        terminal.display([Pixel(), Pixel(x=1, y=1)])
        expected_output = "".join([
            "   \n",
            " X \n",
            "X  \n"
        ])
        self.assertEqual(output_buffer.getvalue(), expected_output)


class RgbImageTest(unittest.TestCase):

    def test_dimension(self):
        image = RgbImage(12, 23, None)
        self.assertEqual(image.dimension(), (12, 23))


if __name__ == '__main__':
    unittest.main()
