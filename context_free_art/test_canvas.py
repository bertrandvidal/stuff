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

    def test_contains(self):
        size = 3
        terminal = Terminal(size, None)
        for i in range(size):
            self.assertTrue(terminal.contains(Pixel(i, i)))
        self.assertFalse(terminal.contains(Pixel(size +1, size + 1)))


class RgbImageTest(unittest.TestCase):

    def test_dimension(self):
        image = RgbImage(12, 23, None)
        self.assertEqual(image.dimension(), (12, 23))


if __name__ == '__main__':
    unittest.main()
