import sys
import random

NUM_EXPERIMENTS = 10
NUM_BITS = 12

BASIS  = { 0: '+', 1: 'x' }
HV_BIT = { 0: '-', 1: '|' }
DA_BIT = { 0: '/', 1: '\\' }
# maintain reverse mappings for utility
BASIS |= { v: k for k, v in BASIS.items() }
HV_BIT |= { v: k for k, v in HV_BIT.items() }
DA_BIT |= { v: k for k, v in DA_BIT.items() }
MAPPING = { 
    f"{BASIS['+']}0": HV_BIT[0], # H -
    f"{BASIS['+']}1": HV_BIT[1], # V |
    f"{BASIS['x']}0": DA_BIT[0], # D /
    f"{BASIS['x']}1": DA_BIT[1], # A \
}
MAPPING |= { v: k for k, v in MAPPING.items() }

def measure(polarity: str, basis):
    result = ''
    if basis == str(BASIS['+']):
        if polarity in ('|', '-'):
            result = polarity
        else:
            result = HV_BIT[random.getrandbits(1)]
    elif basis == str(BASIS['x']):
        if polarity in ('/', '\\'):
            result = polarity
        else:
            result = DA_BIT[random.getrandbits(1)]
    #print(f"measuring {polarity} with basis {BASIS[int(basis)]}: result {result}")
    return result
        
# allow flipping config based on CLI input
EVE_INTERFERING = False
if len(sys.argv) == 2:
    EVE_INTERFERING = bool(int(sys.argv[1]))

for _ in range(NUM_EXPERIMENTS):
    print(f"EVE_INTERFERING: {EVE_INTERFERING}")
    # Alice generate private random streams to decide the data and basis chosen 
    r_key_A = format(random.getrandbits(NUM_BITS), f'0{NUM_BITS}b')
    r_basis_A = format(random.getrandbits(NUM_BITS), f'0{NUM_BITS}b')
    print(f"**( Alice generates K:\t {' '.join(r_key_A)} )**")
    print(f"**( Alice generates Tx:\t {' '.join(r_basis_A)} )**")

    # Alice then uses these streams to produce the qubits she will send to Bob
    qbits = [ MAPPING[ r_basis_A[i]+r_key_A[i] ] for i in range(NUM_BITS) ]
    print("Alice sends to Bob:\t", " ".join(qbits))

    # Eve may be attempting to snoop using random basis to measure
    OG_qbits = qbits
    if EVE_INTERFERING:
        r_basis_E = format(random.getrandbits(NUM_BITS), f'0{NUM_BITS}b')
        # Eve's measurements will affect the qbit states
        qbits = [ measure(qbits[i], r_basis_E[i]) for i in range(NUM_BITS) ]
        #print("Eve intercepts!\t", " ".join(qbits))

    # Bob then generates random basis to measure
    r_basis_B = format(random.getrandbits(NUM_BITS), f'0{NUM_BITS}b')
    measured_vals_B = [ measure(qbits[i], r_basis_B[i]) for i in range(NUM_BITS) ]
    print("Bob measures:\t\t", " ".join(measured_vals_B))
    print(f"**( Bob generates Rx:\t {' '.join(r_basis_B)} )**")
    print(f"**( Bob measured K*:\t {' '.join([MAPPING[measured_vals_B[i]][1] for i in range(NUM_BITS)])} )**")

    # Alice & Bob publicly announce the bases they used
    # exchanging r_basis_A and r_basis_B

    # they then retain only those events in which their bases matched
    matched_bases = [ int(r_basis_A[i] == r_basis_B[i]) for i in range(NUM_BITS) ]
    print(f"After exchanging bases:\t {' '.join(map(str, matched_bases))} ({sum(matched_bases)} matches)")

    # assert those were measured consistently and there was no Eve interference
    verified_bits = [ int(OG_qbits[i] == measured_vals_B[i]) for i in range(NUM_BITS) if matched_bases[i] ]
    prop_valid = sum(verified_bits) / sum(matched_bases) * 100
    print(f"Successful validation: {sum(verified_bits)}/{sum(matched_bases)} matches - {prop_valid}%")
    if prop_valid < 99.999: 
        print("TOO MUCH INTERFERENCE DETECTED - UNABLE TO ESTABLISH KEY!\n")
    else:
        print("KEY CAN BE ESTABLISHED\n")
