from termcolor import colored
from pprint import PrettyPrinter
from structures import Context

DEBUG = False


def dprint(*args, **kwargs):
    if DEBUG:
        print(*args, **kwargs)

class TokenPrettyPrinter(PrettyPrinter):
    _dispatch = PrettyPrinter._dispatch.copy()

    def _pprint_token_context(self, object, stream, indent, allowance, context, level):
        stream.write(colored('{\n','yellow'))
        stream.write('\n' + ' ' + ' ' * indent)
        self._format_items(object, stream, indent, allowance + 1,
                           context, level)
        stream.write('\n' + ' ' * indent)
        stream.write(colored('}','yellow'))

    _dispatch[Context.__repr__] = _pprint_token_context

tprinter = TokenPrettyPrinter(
    indent=4,
    width=100,
)

def tprint(*args, **kwargs):
    tprinter.pprint(*args, **kwargs)