import argparse
import numpy as np

parser = argparse.ArgumentParser()
parser.add_argument("--policy", type=str)
parser.add_argument("--states", type=str)

args = parser.parse_args()

policy_file = open(args.policy, 'r')
policy_data = policy_file.readlines()
opponent_states = list()
opponent_policy = {}

for line in policy_data[1:] :
    data = line.split()
    opponent_states.append(str(data[0]))
    opponent_policy[str(data[0])] = [float(x) for x in data[1:]]

# print(policy_data)
# print(opponent_policy)

states_file = open(args.states, 'r')
states = states_file.read().splitlines()
actions = list(range(9))

opponent = int(policy_data[0])
self = 3 - opponent

print("numStates", len(states)+1)
print("numActions", len(actions))
print("end", len(states))

def win(state, player) :
    l = list(state)
    for j in range(3) :
        c = 0
        for i in range(3) :
            if l[3*i + j] == player : c += 1
        if c == 3 : return True
    for j in range(3) :
        c = 0
        for i in range(3) :
            if l[i + 3*j] == player : c += 1
        if c == 3 : return True
    c = 0
    for i in range(3) :
        if l[4*i] == player : c += 1
    if c == 3 : return True
    c = 0
    for i in range(3) :
        if l[2*i+2] == player : c += 1
    if c == 3 : return True
    return False

def draw(state) :
    if not win(state, '1') and not win(state, '2') :
        return True
    else :
        return False

for s in states :
    for a in actions :
        opponent_state = list(s)
        opponent_state[a] = str(self)
        string = "".join(opponent_state)
        if s[a] == '0' and string in opponent_states :
            for opponent_action, prob in enumerate(opponent_policy[string]) :
                next_state = np.copy(opponent_state)
                next_state[opponent_action] = str(opponent)
                string2 = "".join(next_state)
                if prob > 0 :
                    if string2 in states :
                        print("transition", states.index(s), a, states.index("".join(next_state)), 0, prob)
                    elif draw(string2) :
                        print("transition", states.index(s), a, len(states), 0, prob)
                    else :
                        print("transition", states.index(s), a, len(states), 1, prob)
        elif s[a] == '0' :
            print("transition", states.index(s), a, len(states), 0, 1)

print("mdptype episodic")
print("discount", 1.0)