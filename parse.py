from itertools import groupby
import functools
import poq_token
from structures import Expr, Context
from rules import Substitution, Shape, ruletypes
from preparse import hande_encapsulating_tokens, parse_symbols
from print_helper import dprint, tprint



def split_list(l,on):
    return [
        list(group) 
        for n, group in groupby(l, lambda el: el==on) 
        if not n
        ]


def context_to_head_body(context):
    for n, el in enumerate(context):
        if el == poq_token.Separator.BODYDEF:
            return (Expr(context[:n]), Context(context[n+1:]))
    raise ValueError(
        f'context {context} doesnt have a distinct head and body, indicated by {poq_token.Separator.BODYDEF}'
    )

def parse_with(withy_context):
    return [
        (kind, Substitution(head, Expr(body)))
        for kind, head, body
        in map(
            lambda el: (el[0], *context_to_head_body(el[1:])), 
            split_list(withy_context, poq_token.Separator.EXPR_SPLITTER))
        ]

def expr_to_expanded_exprs(self, is_function_params=False):

    try:
        iter(self)
    except TypeError:
        return self

    if len(self) == 1:
        if is_function_params:
            return Expr((expr_to_expanded_exprs(self[0], False),))
        else:
            return expr_to_expanded_exprs(self[0], False)

    out = []
    for token, prev in zip(self, Expr((None, *self))):
        out.append(expr_to_expanded_exprs(token, isinstance(prev, poq_token.Name)))
    return Expr(out)

def exprs_to_token_sequence(self):
    def f(self):
        try:
            iter(self)
        except TypeError:
            return Expr((poq_token.Separator.OPEN_PAR, self, poq_token.Separator.CLOSE_PAR))
        out = []
        for token in self:
            if isinstance(token, Expr):
                out.extend(f(token))
            else:
                out.append(token)
        return Expr((poq_token.Separator.OPEN_PAR, *out, poq_token.Separator.CLOSE_PAR))

    return Expr(f(self)[1:-1])

def expand_parentheses(expr):
    res = hande_encapsulating_tokens(
        expr,
        poq_token.Separator.OPEN_PAR, 
        poq_token.Separator.CLOSE_PAR,
        Expr
    )
    res = expr_to_expanded_exprs(res)
    res = exprs_to_token_sequence(res)
    res = (
        Shape(
            Expr(parse_symbols('(f(name))')),
            Expr(parse_symbols('f(name)')))
        .apply(res, poq_token.ApplyStratKW.ALL)
    )

    if res == expr:
        return res
    else:
        return expand_parentheses(res)
    

def parse_context(head: Context = None, context: Context = None, rules: dict = None):

    if rules is None:
        rules = {}

    match context:
        
        case [
            poq_token.Name() as name, 
            poq_token.Separator.ASSIGN, 
            poq_token.RuleKW() as ruletype, 
            Context() as value, 
            *other
        ]:

            rules[name] = parse_context(head, Context([ruletype, value]), rules)
            if other:
                return parse_context(head, Context(other), rules)
            else: 
                return rules[name]


        case [
            poq_token.RuleKW() as ruletype, 
            Context() as value
        ]:

            head, body = context_to_head_body(value)
            return ruletypes[ruletype](
                head,
                parse_context(head=head, context=body, rules=rules)
            )

        case [
            poq_token.SugarKW.EXPAND, 
            *other_tokens
        ]:

            if head is None:
                raise ValueError('no head to expand')
            
            new_body = expand_parentheses(head)

            if other_tokens:
                return parse_context(Expr(new_body), Context(other_tokens), rules)
            else: 
                return new_body

        case [
            poq_token.FlowKW.APPLY, 
            *apply_details
        ]:

            if head is None:
                raise ValueError('no head to apply rules to')

            reverse_rule = False
            match apply_details:
                case [
                    poq_token.FlowKW.REVERSE,
                    *apply_details
                ]:
                    reverse_rule = True


            match apply_details:

                case [
                    poq_token.RuleKW() as ruletype, 
                    Context() as value,
                    poq_token.FlowKW.TO,
                    (poq_token.ApplyStratKW() | poq_token.Number()) as apply_strat,
                    *maybe_with_statement
                ]:
                    used_rule = parse_context(head, Context([ruletype, value]), rules)

                case [
                    poq_token.Name() as rulename,
                    poq_token.FlowKW.TO,
                    (poq_token.ApplyStratKW() | poq_token.Number()) as apply_strat,
                    *maybe_with_statement
                ]:
                    used_rule = rules[rulename]
            
            if reverse_rule:
                        used_rule = used_rule.reverse()
                
            match maybe_with_statement:

                case [
                    poq_token.FlowKW.WITH, 
                    poq_token.Name() as subname,
                    poq_token.FlowKW.TO,
                    (poq_token.ApplyStratKW() | poq_token.Number()) as substitution_strat,
                    *other_tokens
                ]:
                    new_body = rules[subname].apply(head, substitution_strat)

                    dprint('\n\napplying rule', used_rule, ' of type ', type(used_rule))
                    new_body = used_rule.apply(new_body, apply_strat)
                    dprint('\n\nrule applied, result is', new_body)

                    new_body = rules[subname].reverse().apply(new_body, poq_token.ApplyStratKW.ALL)
                    

                case [
                    poq_token.FlowKW.WITH, 
                    Context() as value, 
                    *other_tokens
                ]:

                    substitutions = parse_with(value)

                    for substitution_strat, sub in substitutions:
                        head = sub.apply(head, substitution_strat)
                        
                    new_body = used_rule.apply(head, apply_strat)

                    for substitution_strat, sub in reversed(substitutions):
                        new_body = sub.reverse().apply(new_body, poq_token.ApplyStratKW.ALL)
                    
                case other_tokens:
                    new_body = used_rule.apply(head, apply_strat)

            if other_tokens:
                return parse_context(Expr(new_body), Context(other_tokens), rules)
            else: 
                return new_body

        case maybe_expr:
            return Expr(maybe_expr)


def parse(recipe):
    return (
        functools.reduce(
            lambda acc, fun: fun(acc),
            [
                parse_symbols,
                lambda x: parse_context(head=None, context=x),
                lambda x: x.to_python_expression(),
                tprint,
                lambda *args: None

            ],
            recipe
        )
    )

