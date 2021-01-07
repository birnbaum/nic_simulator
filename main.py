import csv
from typing import Tuple, List, Dict, Optional

import numpy as np

import simpy

# Interrupt trace data type: List of (time, IPs) where IPs is the list of package IPs that triggered the interrupt
InterruptTrace = List[Tuple[int, List[str]]]


class Buffer(simpy.Store):
    last_flush = 0

    def __init__(self, env: simpy.Environment, packet_limit: int = None, time_limit: int = None, *args, **kwargs):
        super().__init__(env, *args, **kwargs)
        self.env = env
        self.packet_limit = packet_limit
        self.time_limit = time_limit

    def try_flush(self, interrupt_trace: InterruptTrace):
        packet_limit_reached = self.packet_limit is not None and len(self.items) >= self.packet_limit
        time_limit_reached = self.time_limit is not None and self.env.now - self.last_flush >= self.time_limit
        if packet_limit_reached or time_limit_reached:
            self.flush(interrupt_trace)

    def flush(self, interrupt_trace: InterruptTrace):
        interrupt_trace.append((self.env.now, self.items))
        self.items = []
        self.last_flush = self.env.now


def main():
    env = simpy.Environment()

    # will flush every 10 packages
    buffer1 = Buffer(env, packet_limit=10)
    # will flush every 5 time units and will raise an exception if more packets than capacity are added
    buffer2 = Buffer(env, time_limit=5, capacity=128)

    ip_buffer_mapping = {
        "127.0.0.1": None,  # if no buffer is specified, interrupts will be triggered directly
        "127.0.0.2": buffer1,
        "127.0.0.3": buffer2,
    }

    interrupt_trace = []
    env.process(nic(env, ip_buffer_mapping, interrupt_trace))
    env.run()
    write_interrupt_trace(interrupt_trace)


def nic(env: simpy.Environment, ip_buffer_mapping: Dict[str, Optional[Buffer]], interrupt_trace: InterruptTrace):
    packet_trace = read_packet_trace()
    for time, ip in packet_trace:
        yield env.timeout(time - env.now)  # Wait for new packet to arrive
        buffer = ip_buffer_mapping[ip]
        if buffer is None:
            # No buffer, directly trigger interrupt
            interrupt_trace.append((env.now, [ip]))
            continue
        buffer.put(ip)
        buffer.try_flush(interrupt_trace)


def read_packet_trace() -> List[Tuple[int, str]]:
    with open("./packet_trace.csv") as csv_file:
        reader = csv.reader(csv_file)
        return [(int(time_str), ip) for time_str, ip in reader]


def write_interrupt_trace(interrupt_trace: InterruptTrace):
    with open("./interrupt_trace.csv", "w") as csv_file:
        writer = csv.writer(csv_file)
        for interrupt in interrupt_trace:
            writer.writerow(interrupt)


if __name__ == '__main__':
    main()
