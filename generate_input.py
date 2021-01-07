import csv

import numpy as np

SEED = 0
NUMBER_OF_PACKETS = 100
MAX_TIME = 100
IP_LIST = ["127.0.0.1", "127.0.0.2", "127.0.0.3"]
IP_PROBABILITIES = [0.1, 0.3, 0.6]


def generate_input():
    """Generate packet list where each item is a tuple (time, IP)

    Packages are uniformly sampled over time.
    Package IPs are sampled according to `IP_PROBABILITIES`.
    """
    rng = np.random.default_rng(seed=SEED)
    times = np.sort(rng.integers(MAX_TIME, size=NUMBER_OF_PACKETS))
    ips = rng.choice(IP_LIST, p=IP_PROBABILITIES, size=NUMBER_OF_PACKETS)
    packets = [(time, ip) for time, ip in zip(times, ips)]

    with open("./packet_trace.csv", "w") as csv_file:
        writer = csv.writer(csv_file)
        for packet in packets:
            writer.writerow(packet)


if __name__ == '__main__':
    generate_input()
