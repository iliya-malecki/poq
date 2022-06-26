from print_helper import dprint
import poq_token
from structures import Expr, TokenMappings
from dataclasses import dataclass


@dataclass
class ProtoRule:
    head: Expr
    body: Expr
    default_apply_strat = poq_token.ApplyStratKW.FIRST

    def __repr__(self):
        return f'{self.head} = {self.body}'

    def to_python_expression(self):
        return f'{self.head.to_python_expression()} = {self.body.to_python_expression()}'
    
    def reverse(self):
        return type(self)(self.body, Expr((poq_token.Separator.OPEN_PAR, *self.head, poq_token.Separator.CLOSE_PAR)))

    def apply_once(self, expr:Expr, *args, **kwargs) -> 'tuple[Expr, Expr, Expr]':
        raise TypeError(
            f"children of '{ProtoRule.__name__}' must define "
            f"apply_once(self, other, ...) -> upto_replacement, replacement, after_replacement. "
            f"'{type(self).__name__}' doesnt, or is the "
            f"'{ProtoRule.__name__}' itself")

    def apply(self, other, strat=None):

        if strat is None:
            strat = self.default_apply_strat

        match strat:

            case poq_token.ApplyStratKW.FIRST:
                dprint()
                dprint(f'working on {other.to_python_expression()}')
                dprint(f'{type(self).__name__} is {self.to_python_expression()}')
                dprint(f'replacement is {self.apply_once(other)}')
                head, repl, tail = self.apply_once(other)
                return Expr(head + repl + tail)

            case poq_token.ApplyStratKW.ALL:
                res = Expr()
                for _ in range(1000):
                    head, repl, tail = self.apply_once(other)
                    dprint()
                    dprint(f'working on {other.to_python_expression()}')
                    dprint(f'{type(self).__name__} is {self.to_python_expression()}')
                    dprint(f'cumulative replacement is {res.to_python_expression()}')
                    res = Expr((*res, *head, *repl))
                    if len(repl) == 0:
                        break
                    other = tail

                return res
                    

            case poq_token.Number():
                raise NotImplementedError('applying any rule to nth match is not implemented')


class Shape(ProtoRule):
    
    def apply_once(self, expr, pos=0):

        if pos + len(self.head) > len(expr):
            return expr, Expr(), Expr() # head, no replacement, no tail

        mappings = TokenMappings()

        for head_token, expr_token in zip(self.head, expr[pos:]):
            if head_token != expr_token:
                return self.apply_once(expr, pos+1)           
            try:
                mappings[head_token] = expr_token
            except ValueError:
                return self.apply_once(expr, pos+1)

        replacement = Expr()
        for body_token in self.body:
            try:
                replacement = replacement.extend(mappings[body_token])
            except KeyError:
                replacement = replacement.extend(body_token)

        return Expr(expr[:pos]), Expr(replacement), Expr(expr[pos+len(self.head):])


class Substitution(ProtoRule):

    def apply_once(self, expr, pos=0):

        if pos + len(self.head) > len(expr):
            return expr, Expr(), Expr()

        for head_token, expr_token in zip(self.head, expr[pos:]):
            if head_token.value != expr_token.value:
                return self.apply_once(expr, pos+1)

        return Expr(expr[:pos]), self.body, Expr(expr[pos+len(self.head):])


ruletypes = {
    poq_token.RuleKW.SHAPE: Shape,
    poq_token.RuleKW.SUB: Substitution
}