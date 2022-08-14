import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--value-policy", type=str)
parser.add_argument("--states", type=str)
parser.add_argument("--player-id", type=int)

args = parser.parse_args()

value_policy_file = open(args.value_policy, 'r')
value_policy_data = value_policy_file.read().splitlines()

states_file = open(args.states, 'r')
states = states_file.read().splitlines()

self = args.player_id

print(self)
for i, s in enumerate(states) :
    string = ""
    string += s
    string += " "
    action = int(value_policy_data[i].split('\t')[1])
    for j in range(9) :
        if j == action :
            string += "1.0 "
        else :
            string += "0.0 "
    print(string[:-1])
