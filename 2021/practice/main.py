#!/usr/bin/env python3
import sys
from itertools import combinations
import random

ID = 0
INGREDIENTS = dict()
def to_id(ingredient):
    global ID
    if ingredient in INGREDIENTS:
        return INGREDIENTS[ingredient]

    INGREDIENTS[ingredient] = ID
    ID += 1
    return ID - 1

def read_file(filename):
    with open(filename, 'r') as f:
        m, t2, t3, t4 = map(int, f.readline().strip().split(' '))
        pizzas = []
        for i in range(m):
            ingredients = tuple([to_id(ingredient) for ingredient in f.readline().strip().split(' ')[1:]])
            pizzas += [(len(pizzas), ingredients)]
    teams = [0, 0, t2, t3, t4]
    return pizzas, teams

def memoize(f):
    memo = {}
    def helper(x):
        if isinstance(x, list): x = tuple(x)
        if x not in memo:
            memo[x] = f(x)
        return memo[x]
    return helper

def rate_delivery(pizzas):
    ingredients = set()
    for pizza in pizzas:
        ingredients |= set(pizza[1])
    return len(ingredients)

def brute(pizzas, teams):
    deliveries = []
    while True:
        for i in reversed(range(2, 5)):
            if teams[i] > 0 and len(pizzas) >= i:
                team_delivery = [pizza[0] for pizza in pizzas[:i]]
                pizzas = pizzas[i:]
                teams[i] -= 1
                break
        else:
            break
        deliveries += [team_delivery]
    return deliveries

def optimize_group(pizzas, teams):
    deliveries = []
    while True:
        if len(pizzas) < 4:
            deliveries += brute(pizzas, teams)
            break

        combs = []
        if teams[2] > 0:
            combs += list(combinations(range(4), 2))
        if teams[3] > 0:
            combs += list(combinations(range(4), 3))
        if teams[4] > 0:
            combs += [(0, 1, 2, 3)]

        if not combs:
            break # no teams left

        sorted_combs = list(sorted(combs, key=lambda comb: -rate_delivery([pizzas[i] for i in comb])))
        deliveries += [[pizzas[i][0] for i in sorted_combs[0]]]
        left_pizzas = {0, 1, 2, 3} - set(sorted_combs[0])
        pizzas = [pizzas[i] for i in left_pizzas] + pizzas[4:]
        teams[len(deliveries[-1])] -= 1

    return deliveries

GROUP = 16
COMBS2 = list(combinations(range(GROUP), 2))
COMBS3 = list(combinations(range(GROUP), 3))
COMBS4 = list(combinations(range(GROUP), 4))
GROUP_RANGE = set(range(GROUP))

def optimize_group_larger(pizzas, teams):
    deliveries = []
    while True:
        if len(pizzas) < GROUP:
            deliveries += optimize_group(pizzas, teams)
            break

        combs = []
        if teams[2] > 0:
            combs += COMBS2
        if teams[3] > 0:
            combs += COMBS3
        if teams[4] > 0:
            combs += COMBS4

        if not combs:
            break # no teams left

        sorted_combs = list(sorted(combs, key=lambda comb: -rate_delivery([pizzas[i] for i in comb])))
        deliveries += [[pizzas[i][0] for i in sorted_combs[0]]]
        left_pizzas = GROUP_RANGE - set(sorted_combs[0])
        pizzas = [pizzas[i] for i in left_pizzas] + pizzas[GROUP:]
        teams[len(deliveries[-1])] -= 1

    return deliveries


def always_first(pizzas, teams, group):
    deliveries = []
    while True:
        if len(pizzas) < 4:
            deliveries += optimize_group(pizzas, teams)
            break

        group = min(len(pizzas), group)
        delivery = [pizzas[0]]

        if teams[2] > 0:
            m = rate_delivery(delivery)
            j = 1
            for i in range(1, group):
                n = rate_delivery(delivery + [pizzas[i]])
                if n > m:
                    j = i
                    m = n

            pizzas[1], pizzas[j] = pizzas[j], pizzas[1]
            delivery += [pizzas[1]]

        if teams[3] > 0:
            m = rate_delivery(delivery)
            j = None
            for i in range(2, group):
                n = rate_delivery(delivery + [pizzas[i]])
                if n > m:
                    j = i
                    m = n

            if j:
                pizzas[2], pizzas[j] = pizzas[j], pizzas[2]
                delivery += [pizzas[2]]

        if teams[4] > 0:
            m = rate_delivery(delivery)
            j = None
            for i in range(3, group):
                n = rate_delivery(delivery + [pizzas[i]])
                if n > m:
                    j = i
                    m = n

            if j:
                pizzas[3], pizzas[j] = pizzas[j], pizzas[3]
                delivery += [pizzas[3]]

        if len(delivery) == 1:
            break

        teams[len(delivery)] -= 1
        pizzas = pizzas[len(delivery):]
        deliveries += [[pizza[0] for pizza in delivery]]

    return deliveries


def sorted_pizzas(pizzas, teams):
    pizzas = list(sorted(pizzas, key=lambda x: -len(x[1])))
    return always_first(pizzas, teams, 1000)

def random_pizzas(pizzas, teams):
    random.shuffle(pizzas)
    return optimize_group_larger(pizzas, teams)

def write_file(input_file, deliveries):
    assert input_file.endswith('.in')
    output_file = f'{input_file[:-3]}.out'
    print(output_file)
    with open(output_file, 'w') as f:
        print(len(deliveries), file=f)
        for delivery in deliveries:
            print(len(delivery), ' '.join(map(str, delivery)), file=f)

if __name__ == '__main__':
    pizzas, teams = read_file(sys.argv[1])
    deliveries = sorted_pizzas(pizzas, teams)
    write_file(sys.argv[1], deliveries)

