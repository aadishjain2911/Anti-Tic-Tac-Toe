import argparse
import numpy as np
import pulp as p

parser = argparse.ArgumentParser()
parser.add_argument("--mdp", type=str)
parser.add_argument("--algorithm", type=str, default="hpi")
epsilon = 1e-8
np.set_printoptions(precision=6)

args = parser.parse_args()

mdp_file = open(args.mdp, "r")
mdp_data = mdp_file.readlines()

S = int(mdp_data[0].split()[1])
A = int(mdp_data[1].split()[1])
end = [int(x) for x in mdp_data[2].split()[1:]]
mdptype = str(mdp_data[-2].split()[1])
discount = float(mdp_data[-1].split()[1])
L = [[[] for j in range(A)] for i in range(S)]
T = [[[] for j in range(A)] for i in range(S)]
R = [[[] for j in range(A)] for i in range(S)]

for line in mdp_data :
    vals = line.split()
    if vals[0] == "transition" :
        L[int(vals[1])][int(vals[2])].append(int(vals[3]))
        T[int(vals[1])][int(vals[2])].append(float(vals[5]))
        R[int(vals[1])][int(vals[2])].append(float(vals[4]))

def IS(pi) :
    Lp_prob = p.LpProblem('Problem')
    vars = list()

    for s in range(S) :
        vars.append(p.LpVariable("V"+str(s)))

    for s in range(S) :
        if s in end :
            Lp_prob += (vars[s] == 0)
            continue
        Lp_prob += (vars[s] == p.lpSum([T[s][int(pi[s])][i]*(R[s][int(pi[s])][i] + discount*vars[sd]) for i, sd in enumerate(L[s][int(pi[s])])]))

    Lp_prob.solve(p.PULP_CBC_CMD(msg=0, gapAbs=1e-8))

    V = np.zeros(S)
    Q = np.zeros((S, A))

    for s in range(S) :
        V[s] = vars[s].varValue

    for s in range(S) :
        for a in range(A) :
            for i, sd in enumerate(L[s][a]) :
                Q[s, a] += T[s][a][i]*(R[s][a][i] + discount*V[sd])
            if len(L[s][a]) == 0 :
                Q[s, a] = -1e12
    
    improvable_states = list()
    pid = np.copy(pi)

    for s in range(S) :
        l = list()
        vals = list()
        for a in range(A) :
            if Q[s, a] - V[s] > epsilon and a != pi[s] : 
                l.append(a)
                vals.append(Q[s, a])
        if len(l) >= 1 :
            pid[s] = l[np.argmax(vals)]
            improvable_states.append(s)
    
    return improvable_states, pid

if args.algorithm == "vi" :
    V = np.random.rand(S)
    Q = np.zeros((S, A))
    V_prev = np.zeros(S)

    TR = np.zeros((S, A))
    for s in range(S) :
        for a in range(A) :
            for i in range(len(L[s][a])) :
                TR[s, a] += T[s][a][i]*R[s][a][i]
    
    while np.max(np.abs(V - V_prev)) >= epsilon :
        V_prev = np.copy(V)
        for s in range(S) :
            if s in end :
                V[s] = 0
                continue
            val = 0
            for a in range(A) :
                temp_sum = TR[s, a]
                for i, sd in enumerate(L[s][a]) :
                    temp_sum += T[s][a][i]*discount*V[sd]
                val = max(val, temp_sum)
            V[s] = val

    for s in range(S) :
        for a in range(A) :
            for i, sd in enumerate(L[s][a]) :
                Q[s, a] += T[s][a][i]*(R[s][a][i] + discount*V[sd])
            if len(L[s][a]) == 0 :
                Q[s, a] = -1e12

    pi = np.argmax(Q, axis=1)

elif args.algorithm == "hpi" :
    pi = np.zeros(S)
    for s in range(S) :
        for a in range(A) :
            if len(L[s][a]) != 0 :
                pi[s] = a
                break

    improvable_states = [0 for i in range(S)]
    while len(improvable_states) >= 1 :
        improvable_states, pi = IS(pi)

    Lp_prob = p.LpProblem('Problem')
    vars = list()

    for s in range(S) :
        vars.append(p.LpVariable("V"+str(s)))

    for s in range(S) :
        if s in end :
            Lp_prob += (vars[s] == 0)
            continue
        Lp_prob += (vars[s] == p.lpSum([T[s][int(pi[s])][i]*(R[s][int(pi[s])][i] + discount*vars[sd]) for i, sd in enumerate(L[s][int(pi[s])])]))

    Lp_prob.solve(p.PULP_CBC_CMD(msg=0, gapAbs=1e-8))

    V = np.zeros(S)
    for s in range(S) :
        V[s] = vars[s].varValue

elif args.algorithm == "lp" :
    Lp_prob = p.LpProblem('Problem', p.LpMaximize)
    vars = list()

    for s in range(S) :
        vars.append(p.LpVariable("V"+str(s)))

    for s in range(S) :
        if s in end :
            Lp_prob += (vars[s] == 0)
            continue
        for a in range(A) :
            Lp_prob += (vars[s] >= p.lpSum([T[s][a][i]*(R[s][a][i] + discount*vars[sd]) for i, sd in enumerate(L[s][a])]))
    
    Lp_prob += -p.lpSum(vars)
    Lp_prob.solve(p.PULP_CBC_CMD(msg=0))

    V = np.zeros(S)
    Q = np.zeros((S, A))

    for s in range(S) :
        V[s] = vars[s].varValue

    for s in range(S) :
        for a in range(A) :
            for i, sd in enumerate(L[s][a]) :
                Q[s, a] += T[s][a][i]*(R[s][a][i] + discount*V[sd])
            if len(L[s][a]) == 0 :
                Q[s, a] = -1e12

    pi = np.argmax(Q, axis=1)

for s in range(S) :
    print('%.6f'%V[s], int(pi[s]), sep='\t')
