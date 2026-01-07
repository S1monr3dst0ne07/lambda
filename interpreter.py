#!/usr/bin/python3
from dataclasses import dataclass
from pprint import pprint

import sys
sys.setrecursionlimit(1000000)

if len(sys.argv) < 2:
    print("usage: ./interpreter.py main.lam")
    sys.exit(1)


def preprocess(path):
    rosetta = {}

    def translate(rosetta, text):
        for key, value in rosetta.items():
            text = text.replace(key, value)
        return text

    with open(path, 'r') as f:
        raw = f.read()

    for line_no, rule in enumerate(raw.split('\n')):
        if rule.strip() == '': continue
        if rule.startswith('--'): continue #comment
        if rule.startswith('#'):
            path = rule[1:]
            subrules = preprocess(path)
            rosetta.update(subrules)
            continue

        if rule.count('=') != 1: 
            print(f"Malformed rule in {path} at line {line_no}: {rule}")
            sys.exit(1)

        name, body = map(str.strip, rule.split('='))
        rosetta[name] = translate(rosetta, body)

    return rosetta

main = preprocess(sys.argv[1])["MAIN"]
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
    
    @classmethod
    def parse(cls, env):
        binding = pop()
        body    = ast_apply.parse([binding] + env)

        return cls(body)

    def eval(self, env, arg=None):
        #closure generation
        if arg is None:
            return ast_clos(self.body, env)

        return self.body.eval([arg] + env)


count = 0

class ast_print:
    def eval(env, arg=None): 
        if arg is None: return ast_print #normal
        global count        
        count += 1

        return arg


@dataclass
class ast_apply:
    terms : list[ast_lam | ast_var]

    @classmethod
    def parse(cls, env=[]):
        terms = []
        while has() and peek() != ')':
            match pop():
                case '(':
                    t = ast_apply.parse(env)
                    pop()
                case '\\':  t = ast_lam.parse(env)
                case '?':   t = ast_print
                case x:     t = ast_var.parse(x, env)

            terms.append(t)

        return cls(terms)

    def eval(self, env):

        fn, *args = (
            x.eval(env)
            for x in self.terms
        )

        for arg in args:
            fn = fn.eval(env, arg)

        return fn


    
     

root = ast_apply.parse()
node = root.eval(env = [])

print(count)



