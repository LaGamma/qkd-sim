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
    r_basis_A = format(random.getrandbits(NUM_BITS), f'0{NUM_BITS}b')

    # Alice then uses these streams to produce the qubits she will send to Bob
    qbits = [ MAPPING[ r_basis_A[i]+r_key_A[i] ] for i in range(NUM_BITS) ]
    print("Alice sends to Bob:\t", " ".join(qbits))

    # Bob then generates random basis to measure
    r_basis_B = format(random.getrandbits(NUM_BITS), f'0{NUM_BITS}b')
    #r_basis_B = str(random.getrandbits(1))*NUM_BITS # choose one basis for all
    measured_vals_B = [ measure(qbits[i], r_basis_B[i]) for i in range(NUM_BITS) ]
    print("Bob measures:\t\t", " ".join(measured_vals_B))

    r_b = str(random.getrandbits(1))
    j_index = random.randrange(0, NUM_BITS)
    print(f"Bob publishes j={j_index} and b={r_b}")

    #Alice publicly announce the bases she used and key for the j-th bit
    print(f"Alice chose basis {BASIS[r_basis_A[j_index]]} encoding bit {r_key_A[j_index]} "\
            f"({qbits[j_index]})")

    # check if their bases matched and should align
    if BASIS[r_basis_A[j_index]] == BASIS[r_basis_B[j_index]] \
            and qbits[j_index] != measured_vals_B[j_index]:
        print("ABORT!!!")
    else:
        coin_result = int(r_key_A[j_index]) ^ int(r_b)
        print(f"{int(r_key_A[j_index])} ^ {int(r_b)} = {coin_result}\n")
        totals[coin_result] += 1

print("TOTALS:", totals)


