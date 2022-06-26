import re
import poq_token
import functools
from structures import Context


def pretokenize(recipe):
    for token in ['{','}','(',')']: # 1. split up a nasty simple way
        recipe = re.sub(re.escape(token), f' {token} ', recipe)
    recipe = re.sub(r'\b',             ' ', recipe) # 2. insert spaces between words
    recipe = re.sub(r'(?<![\n ]) {2,}',' ', recipe) # 3. clean up multiple spaces
    return recipe


def word_to_token(word):
    for const_token in poq_token.const_types:
        try:
            return const_token(word)
        except ValueError:
            continue
    for varying_token in poq_token.varying_types:
        if re.fullmatch(varying_token.pattern, word):
            return varying_token(word)


def tokenize(recipe):
    return [word_to_token(word) for word in recipe.split()]

def hande_encapsulating_tokens(tokens, opener, closer, result_container):

    for n, token in enumerate(tokens):
        if type(token) is type(opener):
            if token == opener:
                    open_curly_pos = n
            elif token == closer:
                return hande_encapsulating_tokens(
                    [
                        *tokens[:open_curly_pos],
                        result_container(tokens[open_curly_pos+1:n]),
                        *tokens[n+1:]
                    ],
                    opener,
                    closer,
                    result_container
                    )
    return result_container(tokens)


def preparse(tokens):

    # a friendly reminder that this had to be a recursive thing, 
    # matching expressions in expressions as names
    
    # x = hande_encapsulating_tokens(
    #     tokens,
    #     Separator.OPEN_PAR, Separator.CLOSE_PAR,
    #     Expr
    # )
    
    x = hande_encapsulating_tokens(
        tokens,
        poq_token.Separator.OPEN_CURLY, poq_token.Separator.CLOSE_CURLY,
        Context
    )


    
    return x

def parse_symbols(recipe):
    return (
        functools.reduce(
            lambda acc, fun: fun(acc),
            [
                pretokenize,
                tokenize,
                preparse,
            ],
            recipe
        )
    )