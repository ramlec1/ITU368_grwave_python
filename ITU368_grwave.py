import numpy as np
import matplotlib.pyplot as plt
from ctypes import c_double, c_int, POINTER, Structure, CDLL, WinDLL, byref


class Result(Structure):
    ''' Class containing the data returned from a C-function in the form of a
    C-struct. Class is used in the lfmf function as the return variable.'''
    _fields_ = [('A_btl__db', c_double),
                ('E_dBuVm', c_double),
                ('P_rx__dbm', c_double),
                ('method', c_int)]

def run_ITU368_grwave(h_tx__meter, h_rx__meter, f__mhz, P_tx__wat, N_s, d__km, epsilon, sigma, pol):
    ''' Function to call the C++ LFMF function and compute groundwave propagation. The function
    takes the following parameters:
    h_tx__meter: TX height [m]: 0 ≤ h_tx__meter ≤ 50
    h_rx__meter: RX height [m]: 0 ≤ h_rx__meter ≤ 50
    f__mhz: Frequency [MHz]: 0.01 ≤ f__mhz ≤ 30
    P_tx__wat: TX power [W]: 0 < P_tx__watt
    N_s: Surface refractivity [N-units]: 250 ≤ N_s ≤ 400
    d__km: Distance [km]: d__km ≤ 10 000
    epsilon: Relative permittivity earth surface: 1 ≤ epsilon
    sigma: Conductivity earth surface [S/m]: 0 < sigma
    pol: Polarization: 0 = horizontal, 1 = vertical

    The function returns the following values:
    A_btl__db: Basic transmission loss [dB]
    E_dBuVm: Electric field strength [dBuV/m]
    P_rx__dbm: Received power [dBm]
    method: Method used for calculation (0 = Flat Earth with curve correction, 1 = Residue series)
    '''

    # Load the shared library
    lfmf_lib = WinDLL('./LFMF.dll') # Windows
    # lfmf_c_func = CDLL('./LFMF.so') # Linux/Mac

    # Define the argument and return types of the function
    lfmf_lib.LFMF.argtypes = [c_double, 
                            c_double, 
                            c_double, 
                            c_double,
                            c_double, 
                            c_double, 
                            c_double, 
                            c_double, 
                            c_int,
                            POINTER(Result)]
    lfmf_lib.LFMF.restype = c_int

    # Create an instance of the Result structure
    res = Result()

    # Call the function
    status = lfmf_lib.LFMF(h_tx__meter, 
                            h_rx__meter, 
                            f__mhz, 
                            P_tx__wat,
                            N_s,
                            d__km,
                            epsilon,
                            sigma,
                            pol,
                            byref(res))
    
    # Check the status and print the results
    if status == 0:
        return (res.A_btl__db, res.E_dBuVm, res.P_rx__dbm, res.method)
    else:
        print("LFMF function call execution failed.")
        match(status):
            case 1000:
                print(f"Error code {status}: VALIDATION ERROR: h_tx__meter out of range")
            case 1001:
                print(f"Error code {status}: VALIDATION ERROR: h_rx__meter out of range")
            case 1002:
                print(f"Error code {status}: VALIDATION ERROR: f__mhz out of range")
            case 1003:
                print(f"Error code {status}: VALIDATION ERROR: P_tx__wat out of range")
            case 1004:
                print(f"Error code {status}: VALIDATION ERROR: N_s out of range")
            case 1005:
                print(f"Error code {status}: VALIDATION ERROR: d__km out of range")
            case 1006:
                print(f"Error code {status}: VALIDATION ERROR: epsilon out of range")
            case 1007:
                print(f"Error code {status}: VALIDATION ERROR: sigma out of range")
            case 1008:
                print(f"Error code {status}: VALIDATION ERROR: invalid value for pol")
            case _:
                print(f"Error code {status}: UNKNOWN ERROR")
        
def main():
    # Define the input parameters
    h_tx__meter = 50.       # TX height [m]: 0 ≤ h_tx__meter ≤ 50
    h_rx__meter = 3.        # RX height [m]: 0 ≤ h_rx__meter ≤ 50
    f__mhz      = 0.89      # Frequency [MHz]: 0.01 ≤ f__mhz ≤ 30
    P_tx__wat   = 50e3      # TX power [W]: 0 < P_tx__watt
    N_s         = 250.      # Surface refractivity [N-units]: 250 ≤ N_s ≤ 400
    d__km       = 10.        # Distance [km]: d__km ≤ 10 000
    epsilon     = 4.         # Relative permittivity earth surface: 1 ≤ epsilon
    sigma       = 2e-3      # Conductivity earth surface [S/m]: 0 < sigma
    pol         = 1         # Polarization: 0 = horizontal, 1 = vertical 
    
    # run the grwave function
    result = run_ITU368_grwave(h_tx__meter, h_rx__meter, f__mhz, P_tx__wat, N_s, d__km, epsilon, sigma, pol)

    # print the results
    print(f"A_btl__db: {result[0]}")
    print(f"E_dBuVm: {result[1]}")
    print(f"P_rx__dbm: {result[2]}")
    print(f"Method: {result[3]}")

    # Create a range of distances [km]
    distances = np.arange(10, 401, 10) 

    # Compute the transmission loss for each distance using the ITU368 grwave function
    results = []
    for d in distances:
        result = run_ITU368_grwave(h_tx__meter, h_rx__meter, f__mhz, P_tx__wat, N_s, d, epsilon, sigma, pol)
        results.append(result[0])

    # Plot the results
    fig, ax = plt.subplots()
    ax.plot(distances, results)
    ax.set_xlabel('Distance [km]')
    ax.set_ylabel('Basic transmission loss [dB]')
    ax.set_title('ITU 368 Groundwave Propagation')
    ax.grid(True)
    plt.show()

if __name__ == "__main__": 
    main()