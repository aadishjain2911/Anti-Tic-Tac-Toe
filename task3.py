import numpy as np
import subprocess
from difflib import ndiff

def diff(l1, l2) :
    if len(l1) != len(l2) :
        return -1
    else :
        ans = 0
        for i in range(len(l1)) :
            if l1[i] != l2[i] :
                ans += 1
        return ans

subprocess.call("mkdir policies", shell=True, stderr=subprocess.DEVNULL)
player = 2
np.random.seed(50)
state_files = {1: './states/states_file_p1.txt', 2: './states/states_file_p2.txt'}
policy_files = {1: './policies/pone_policy1.txt', 2: './policies/ptwo_policy2.txt'}
states = {}

f1 = open(state_files[1], 'r')
states[1] = f1.read().splitlines()

f1 = open(state_files[2], 'r')
states[2] = f1.read().splitlines()

pi = np.zeros(len(states[3 - player]))

for i in range(len(pi)) :
    l = list()
    for j in range(9) :
        if list(states[3 - player][i])[j] == '0' :
            l.append(j)
    pi[i] = np.random.choice(l)

lines = list()
lines.append(str(3 - player) + "\n")

for i, s in enumerate(states[3 - player]) :
    string = s
    string += " "
    action = int(pi[i])
    for j in range(9) :
        if j == action :
            string += "1.0 "
        else :
            string += "0.0 "
    lines.append(string[:-1] + "\n")

policy_file = open(policy_files[3 - player].replace(str(3 - player), '0'), 'w')
policy_file.writelines(lines)
policy_file.close()
prev_output = {1: "", 2: ""}
cmd_output = {1: "hi", 2: "hi"}

cmd_output[3 - player] = lines
i = 0

while True :

    print("Iteration:", i)
    prev_output[player] = cmd_output[player]

    cmd_encoder = "python3","encoder.py","--policy", policy_files[3-player].replace(str(3 - player), str(i)),"--states",state_files[player]
    f = open('verify_attt_mdp','w')
    subprocess.call(cmd_encoder,stdout=f)
    f.close()

    cmd_planner = "python3","planner.py","--mdp","verify_attt_mdp"
    f = open('verify_attt_planner','w')
    subprocess.call(cmd_planner,stdout=f)
    f.close()

    cmd_decoder = "python3","decoder.py","--value-policy","verify_attt_planner","--states",state_files[player] ,"--player-id",str(player)
    f = open(policy_files[player].replace(str(player), str(i+1)), 'w')
    cmd_output[player] = subprocess.check_output(cmd_decoder,universal_newlines=True)
    f.writelines(cmd_output[player])
    cmd_output[player] = cmd_output[player].split('\n')
    f.close()

    f = open(policy_files[3-player].replace(str(3-player), str(i+1)), 'w')
    f.writelines(cmd_output[3-player])
    f.close()

    if diff(prev_output[1], cmd_output[1]) != -1 :
        print("Player: 1, Changed states:", diff(prev_output[1], cmd_output[1]))
    if diff(prev_output[2], cmd_output[2]) != -1 :
        print("Player: 2, Changed states:", diff(prev_output[2], cmd_output[2]))

    if diff(prev_output[1], cmd_output[1]) == 0 and diff(prev_output[2], cmd_output[2]) == 0 :
        break

    player = 3 - player
    i += 1

print("Policies Converged!")
