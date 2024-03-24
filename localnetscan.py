import multiprocessing
import ipaddress
import socket

def generate_ips_in_subnet():
    '''Get curren relevant subnets'''

    subnet = "192.168.1.0/24"
    network = ipaddress.ip_network(subnet)
    return [str(ip) for ip in network.hosts()]

def check_port(ip_addrees):
    '''Look for FTP Servers on the local-net'''
    
    port = 2121
    print("Checking", ip_addrees)
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(1)
        s.connect((ip_addrees, port))
        return ip_addrees
    except (socket.timeout, ConnectionRefusedError):
        return None
    finally:
        s.close()

def parallel_execution():
    '''Run parallel checks for all addresses'''

    ip_address_list = generate_ips_in_subnet()

    pool = multiprocessing.Pool(processes=50)
    results = pool.starmap(check_port, [(ip,) for ip in ip_address_list])

    # Close the pool
    pool.close()
    pool.join()

    return results

if __name__ == "__main__":


    # Execute lambda functions in parallel
    results = parallel_execution()

    # Print results
    print(list(filter(None, results)))