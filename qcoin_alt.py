import random

NUM_EXPERIMENTS = 10000
NUM_BITS = 12

BASIS = { '+': '0', 'x': '1' }
BASIS |= { v: k for k, v in BASIS.items() }
BASIS |= { '|': '+', '-': '+', '/': 'x', '\\': 'x' }
HV_BIT = { 0: '|', 1: '-' }
DA_BIT = { 0: '/', 1: '\\' }
MAPPING = { 
    f"{BASIS['+']}0": HV_BIT[0], # H |
    f"{BASIS['+']}1": HV_BIT[1], # V -
    f"{BASIS['x']}0": DA_BIT[0], # D /
    f"{BASIS['x']}1": DA_BIT[1], # A \
}

def measure(polarity: str, basis):
    result = ''
    if basis == BASIS['+']:
        if polarity in ('|', '-'):
            result = polarity
        else:
            result = HV_BIT[random.getrandbits(1)]
    elif basis == BASIS['x']:
        if polarity in ('/', '\\'):
            result = polarity
        else:
            result = DA_BIT[random.getrandbits(1)]
    #print(f"measuring {polarity} with basis {BASIS[basis]}: result {result}")
    return result
            
totals = [0, 0]
for _ in range(NUM_EXPERIMENTS):
    # Alice generate private random streams to decide the data and basis chosen 
    r_key_A = format(random.getrandbits(NUM_BITS), f'0{NUM_BITS}b')
    r_basis_A = str(random.getrandbits(1))

    # Alice then uses these streams to produce the qubits she will send to Bob
    qbits = [ MAPPING[ r_basis_A+r_key_A[i] ] for i in range(NUM_BITS) ]
    print("Alice sends to Bob:\t", " ".join(qbits))

    # Bob then generates random basis to measure
    r_basis_B = format(random.getrandbits(NUM_BITS), f'0{NUM_BITS}b')
    #r_basis_B = str(random.getrandbits(1))*NUM_BITS # choose one basis for all
    measured_vals_B = [ measure(qbits[i], r_basis_B[i]) for i in range(NUM_BITS) ]
    print("Bob measures:\t\t", " ".join(measured_vals_B))

    # Bob guesses the basis Alice used
    counts = {
            '+': sum([int(BASIS[measured_vals_B[i]] == '+') for i in range(NUM_BITS) ]),\
            'x': sum([int(BASIS[measured_vals_B[i]] == 'x') for i in range(NUM_BITS) ])
    }

    basis_guess = max((v,k) for k,v in counts.items())
    print(f"Bob guesses Alice used {basis_guess} basis")

    #Alice publicly announce the bases she used and sequence of qbits
    print(f"Alice chose basis {BASIS[r_basis_A]}")

    guess_result = int(BASIS[r_basis_A] == basis_guess[1])
    print(f"Bob's guess was {['wrong', 'correct'][guess_result]} ({guess_result})")
    totals[guess_result] += 1

    # Alice sends the original bits to confirm she was not cheating
    # those events in which their bases matched should align
    matched_bases = [ int(r_basis_A == r_basis_B[i]) for i in range(NUM_BITS) ]
    for i in range(NUM_BITS):
        if matched_bases[i]: assert(qbits[i] == measured_vals_B[i])
    print(f"Bob verifies no cheating occurred - matched bases: {matched_bases} {sum(matched_bases)}\n")

print("TOTALS:", totals)


