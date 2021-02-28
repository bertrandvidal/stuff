import unittest

from display import Terminal
from grammar import GrammarGenerator, Grammar
from pixel import Pixel


class TerminalTest(unittest.TestCase):

    def test_something(self):
        grammar = Grammar(rules=[lambda p: [p, Pixel(x=p.x + 1, y=p.y + 1)]])
        generator = GrammarGenerator(grammar=grammar, start=Pixel())
        terminal = Terminal(3, #io.StringIO)
        pixels = next(generator.generate(1))
        terminal.display(pixels)


if __name__ == '__main__':
    unittest.main()
