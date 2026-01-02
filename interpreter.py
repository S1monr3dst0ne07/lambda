#!/usr/bin/python3
from dataclasses import dataclass
import itertools

import sys

with open(sys.argv[1], 'r') as f:
    raw = f.read()

def translate(rosetta, text):
    for key, value in rosetta.items():
        text = text.replace(key, value)
    return text


#preprocess
rosetta = {}
for rule in raw.split('\n'):
    if rule.strip() == '': continue
    if rule.startswith('--'): continue
    if rule.count('=') != 1: print(f"Malformed rule: {rule}")

    name, body = map(str.strip, rule.split('='))
    rosetta[name] = translate(rosetta, body)

main = rosetta["MAIN"]
print(main)


src = list(x for x in main if x not in (' '))
peek = lambda: src[0]
pop  = lambda: src.pop(0)
has  = lambda: len(src) > 0

# during parsing, the `env` environment
# is a list of binding names of lambdas,
# used to compute the brujin index of each variable.

@dataclass
class ast_var:
    brujin : int

    @classmethod
    def parse(cls, name, env):
        brujin = env.index(name)
        return cls(brujin)

    def eval(self, env):
        return env[self.brujin]


@dataclass
class ast_clos:
    body : "body"
    env  : list[""]

    def eval(self, _, arg):
        # replace environment
        return self.body.eval([arg] + self.env)
        

@dataclass
class ast_lam:
    body : "body"
    env  : list[""]
    
    @classmethod
    def parse(cls, env):
        binding = pop()
        body    = ast_apply.parse([binding] + env)

        return cls(body, [])

    def eval(self, env, arg=None):
        #closure generation
        if arg is None:
            return ast_clos(self.body, env)

        return self.body.eval([arg] + env)

count = 0

class ast_print:
    def eval(env, arg): 
        global count        
        count += 1

        return arg


@dataclass
class ast_apply:
    terms : list[ast_lam | ast_var]

    @staticmethod
    def route(env):
        match pop():
            case '(':
                body = ast_apply.parse(env)
                pop()
                return body
            case '\\':  return ast_lam.parse(env)
            case '?':   return ast_print
            case x:     return ast_var.parse(x, env)

    @classmethod
    def parse(cls, env=[]):
        terms = []
        while has() and peek() != ')':
            terms.append(cls.route(env))

        #prune singleton applications
        if len(terms) == 1:
            return terms[0]

        return cls(terms)

    def eval(self, env):
        fn, *args = (
            x.eval(env)
            if type(x) in (ast_apply, ast_var)
            else x
            for x in self.terms
        )

        for arg in args:
            fn = fn.eval(env, arg)

        return fn


    
     

root = ast_apply.parse()
node = root.eval(env = [])

print(count)



