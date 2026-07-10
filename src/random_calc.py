import random
# import sympy

PYTOTEX = {
    '*': "\\times",
    '+': "+",
    '-': "-",
    '/': "\\div"
}
PYTOTXT = {
    '*': "mul",
    '+': "add",
    '-': "sub",
    '/': "div",
    '#': "non" 
}
SIGMA = 15


def norm(rel_int):
    """
    Return a relative integer with parenthesis if
    the numbre is negative else only the number.
    """
    if type(rel_int) == str:
        rel_int = eval(rel_int)
    if rel_int < 0:
        return '(' + str(rel_int) + ')'
    return str(rel_int)

def write(calc, par=False, mathmode=False):
    if type(calc) == str:
        if mathmode:
            return '$' + calc + '$'
        return calc
    tex_string, a, b = calc
    result = tex_string.format(a,b)
    if par:
        return '(' + result + ')'
    if mathmode:
        return '$' + result + '$'
    return result

class RelIntOp:

    def __init__(self, op, result):
        self.result=result
        self.op = op
        self.calc = getattr(self,PYTOTXT[op]+"_two_rel_int")()

    def non_two_rel_int(self):
        return str(self.result)

    def add_two_rel_int(self, sigma=SIGMA, exc={0}):
        a = round(random.gauss(0, sigma))
        while a in exc:
            a = round(random.gauss(self.result, sigma))
        b = self.result-a
        return ["{}+{}", str(a), norm(b)]

    def sub_two_rel_int(self, sigma=SIGMA, exc={0}):
        a = round(random.gauss(0, sigma))
        while a in exc:
            a = round(random.gauss(self.result, sigma))
        b = self.result + a
        return ["{}-{}", str(b), norm(a)]

    # def mul_two_rel_int(self, sigma=SIGMA, exc={0}):
    #     a = random.choice(sympy.divisors(self.result))
    #     while a in exc:
    #         a = random.choice(sympy.divisors(self.result))
    #         print(self.result)
    #     b = int(self.result/a)
    #     return ["{}\\times{}", str(b), norm(a)]

    def div_two_rel_int(self, sigma=SIGMA, exc={0,1}):
        a = round(random.gauss(0, sigma))
        while a in exc or a == 0:
            a = round(random.gauss(self.result, sigma))
        b = int(self.result*a)
        return ["{}\\div{}", str(b), norm(a)]

def rand_calc(ops, result):
    lop, cop, rop = ops
    calc = RelIntOp(cop, result).calc
    calc[1] = write(RelIntOp(lop, eval(calc[1])).calc, par=False)
    calc2 = eval(calc[2])
    if rop == '#' and calc2 < 0:
        par2 = True
    else:
        par2 = random.choice([True, False])
    calc[2] = write(RelIntOp(rop, calc2).calc, par=par2)
    return write(calc, mathmode=True)

OPS = [
    '#+#', '#-#', '#*#', '#/#',
    # '#+*', '#-*', '#+/', '#-/',
    # '*+#', '*-#', '/+#', '/-#',
    # '+*+', '+*-', '-*+', '-*-',
    # '+/+', '+/-', '-/+', '-/-'
    ]

def get_rand_calc(ops, result):
    calc = rand_calc(ops, result)
    while any(['\\div-' in calc, '\\times-' in calc, '+-' in calc, '--' in calc]):
        calc = rand_calc(ops, result)
    return calc


def bleu_clair():
    return get_rand_calc(random.choice(OPS), random.randint(-20,-10))

def bleu_fonce():
    return get_rand_calc(random.choice(OPS), random.randint(-9,-1))

def gris():
    return get_rand_calc(random.choice(OPS), random.randint(1,10))

def noir():
    return get_rand_calc(random.choice(OPS), random.randint(11,20))

LENGHT = 15

LINE1 = [bleu_clair]*15

LINE2 = [bleu_clair]*15
LINE2[8] = bleu_fonce
LINE2[12] = bleu_fonce

LINE3 = LINE1
LINE3[9] = bleu_fonce
LINE3[11] = bleu_fonce

LINE4 = LINE1
LINE4[10] = bleu_fonce

LINE5 = LINE4
LINE6 = LINE4

LINE7 = [bleu_clair, gris]*2 + [bleu_clair]*2 + [gris]*7 + [bleu_clair]*2

LINE8 = LINE7
LINE8[2] = gris

LINE9 = [bleu_clair] + [gris]*3 + [bleu_clair]*2 + [gris]*5 + [noir] + [gris] + [bleu_clair]*2

LINE10 = LINE9
LINE10[11] = gris

LINE11 = [bleu_clair]*2 + [gris]*11 + [bleu_clair]*2
LINE12 = LINE11
LINE13 = LINE11

LINE14 = [bleu_fonce]*15
LINE15 = LINE14

def line_to_tex(line):
    line = [line[i]() for i in range(len(line))]
    return '&'.join(line) + '\\\\\\hline'

CALCS = []
for i in range(1, LENGHT+1):
    line = globals()['LINE' + str(i)]
    CALCS.append(line_to_tex(line))

print(CALCS)

with open("..\\data\\latex\\templates\\pixelart-template.tex", 'r', encoding='utf-8') as texFile:
    texFileDataLines = texFile.read().split('\n')

tabular_index = 0
line = texFileDataLines[0]
while not "\\hline" in line:
    line = texFileDataLines[tabular_index]
    tabular_index += 1

beg = texFileDataLines[:tabular_index]
end = texFileDataLines[tabular_index:]

coloriage_lines = beg + CALCS + end

with open("..\\data\\latex\\pixelart\\baleine.tex", 'w', encoding='utf-8') as texFile:
     texFile.write('\n'.join(coloriage_lines))