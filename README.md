# poq
## A programming language for transforming expressions, inspired by noq (a programming language for transforming expressions, inspired by coq)
#### and it is written in python, hence the 'p'


Here's an example of a program in poq. Im defining what it means to square a sum, and then applying this notion to 
```
sqos = shape {
    (a + b)^2 
    => 
        sum = sub {(a+b) => x}
        square_id = shape { a^2 => a*a }
        mul_of_sum = shape {x * (y + z) => x*y + x*z}
        mul_commut = shape {self * other => other * self}
        apply square_id to all 
            with sum to all
            expand
        apply mul_of_sum to all 
            with sum to first
            expand
        apply mul_commut to all 
            with sum to all
            expand
        apply mul_of_sum to all
        apply reverse square_id to all
        apply mul_commut to first
        apply shape {x + x => 2*x} to all with {all b*a =>g}
        expand
}
shape {
    ((z + y)^2 + y)^2
    =>
        apply sqos to all with 
        { 
            all (z + y)^2 => a
        }
        expand
        apply sqos to all
}
```
`>>> ((z + y)^2 + y)^2 = (((z^2) + 2*(y*z) + (y^2))^2) + 2*(y*((z^2) + 2*(y*z) + (y^2))) + (y^2)`

same thing with math functions (like f(x)):
```
shape {
    ((f(x) + y)^2 + y)^2
    =>
        apply sqos to all with 
        { 
            all (f(x) + y)^2 => a
        }
        expand
}
```
`((f(x) + y)^2 + y)^2 = (((f(x) + y)^2)^2) + 2*(y*((f(x) + y)^2)) + (y^2)`
## How it works
1. There are Rules, acting on mathematical expressions. They match their first half and replace it with the second. Halves are seperated with a '=>'. The rule itself is enclosed in '{}'
2. You can assign a Rule to a variable with a '='
3. Rules can be of two different types: shapes and substitutions (denoted as 'shape' and 'sub')
4. Shapes match the general form of an expression, replacing variables in expressions accordingly (e.g. shape var + var => 2 * var matches expression a + a)
5. Substitutions match exactly, with respect to variable names (e.g. sub var + var => 2 * var does not match the expression a + a)
6. You can apply an already created rule or a new one on the fly, with a keyword 'apply', followed by a rule name or a rule definition
7. Actually, for it to work, you must specify application strategy: 'all'/'first' (also 'nth' and recursive 'deep' are coming). This tells the interpreter how much and where to apply.
8. You can (optionally) add a 'with <sub_name>', to treat a group of variables as one (or several different, if you choose so). This has the effect of substituting things for one rule application and then sub-ing back. This is useful because often we treat pieces of mathematical expressions as a single one, freely changing our perspective - i have tried replicating it with an algorithm for the rule application, and it does not retain the freedom. Alternatively, i could lean onto "n-th application of a rule" for a user to specify how they want their transformations. But, I personally dont think in numbers (especially in counts of rule applications), i think in shapes of variables in the expression. Hence, the choice - i hope this is the more intuitive way.
9. You can add a new substitution to a 'with'-context on the fly, providing a series of substitutions, separated by ';', enclosed in '{}' and each having their own keyword for application strategy (e.g.{all x^2=>y; first f(x+y) => d})
10. You can get rid of useless parenthesies with a keyword 'expand', but it will not perform any operations that change the meaning of an expression.
11. You can nest these things however you want, creating a shape in a shape in a sub in a shape and then applying it - not a problem. Effectively, when rule is exited, only the transformation from input to output is captured. In a way, this is a system of "last value returned", except that rules are not functions, they have very specific inputs.

## Why poq?
The core reason for the existence of this language is simple: i wanted to explore what it takes to successfully parse input based on its patterns and a set of keywords (i.e. I got excited by python 3.10 pattern matching and decided to ditch the notion of a statement in a programming language).
The answer was unsurprising: it takes a bit of spaghetti code.
However, I have made many more decisions along this journey (none of them are optimal, but all are deliberate) - and discovered a lot of nuance
## Goals and constraints
1. Math expressions must be seen as a sequence of "things", with no rigid structure and minimal assumptions. It is up to the user to define that a+a = a*2
2. Statements are not allowed, there may only be "stuff im looking at directly" and "all other stuff"
3. More recursion in the parser = better (again, this is not supposed to be maintainable, this is supposed to show what are the important bits of information for parsing - handling base cases is a lot closer to the point than handling loops)
4. More match statements in the parser = better (with the same reasoning)
5. The language must not feel "shallow" (i.e. it must be possible to define things in terms of other things with no limit)
## TODO
1. I still have to make the interpreter (which is by the way forever merged with the parser) respect operator precedence since there is no way to do it without introducing a million parenthesies.
2. It would be nice to have at least lex-level error-checking, for now if the poq program is written incorrectly, the interpreter dies with a useless python exception, some half a thousand frames deep in the recursion
## Takeaways
1. Make the interpreter read statement by statement and save the headache
2. Python match statement is underwhelming
