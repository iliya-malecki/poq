from termcolor import colored
import re



class Context(list):
    def __repr__(self, *args, **kwargs):
        return colored('{','yellow') + super().__repr__(*args, **kwargs)[1:-1] + colored('}','yellow')


class Expr(tuple):

    def __eq__(self, other):
        if type(other) is not type(self):
            return False
        return all([self_token.value == other_token.value for self_token, other_token in zip(self,other)])

    def __repr__(self, *args, **kwargs):
        return colored('(','green') + super().__repr__(*args, **kwargs)[1:-1] + colored(')','green')

    def to_python_expression(self):
        res = ''.join([el.value for el in self])
        for token in '+=-/':
            res = re.sub(re.escape(token), f' {token} ', res)
        return res

    @property
    def value(self):
        return f'({self.to_python_expression()})'

    def extend(self, item):
        return Expr((*self, item))



class TokenMappings(dict):
    
    def search(self, token_in_question):
        for key_token, value_token in self.items():
            if value_token.value == token_in_question.value:
                return key_token

    def contains(self, token_in_question):
        for token in self.values():
            if token.value == token_in_question.value:
                return True
        return False

    def __setitem__(self, key_token, value_token):
        try:
            if self[key_token].value != value_token.value:
                raise ValueError(
                    'an attempt was made to change a value for an existing key: '
                    f'{{{key_token}:{self[key_token]}}} -> {{{key_token}:{value_token}}}'
                )
        except KeyError:
            # a friendly reminder that this dict in fact does not scream at you when
            # you call one 'a' a 'b' and one 'a' a 'c'. This is to make rule application easier.

            # if self.contains(value_token):
            #     raise ValueError(
            #         'an attempt was made to add a new key with a value that is already in use: '
            #         f'{{{self.search(value_token)}:{value_token}}} -> {{{key_token}:{value_token}}}'
            #     )
            super().__setitem__(key_token, value_token)
            return True
    
