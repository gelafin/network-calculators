# Author: Mark Mendez
# Date: 01/30/2022


from NetworkingCalculators import calculate_queuing_delay_ms


if __name__ == '__main__':
    # test
    packet_size_in_MiB = None  # set to None if entering file_size_in_bytes
    packet_size_in_bytes = 1500  # set to None if entering file_size_in_MiB
    rate_in_Gbps = 100 / 1000
    packet_number = 4  # packet to find queueing delay for

    packet_size_in_bytes = packet_size_in_MiB * 1024 * 1024 if packet_size_in_MiB is not None else packet_size_in_bytes
    result = calculate_queuing_delay_ms(packet_size_in_bytes, rate_in_Gbps, packet_number)
    print(f'\nqueueing delay for packet {packet_number} (ms): ', result)

    # average queueing delay over first n packets
    n = 10
    all_queueing_delays = []
    for packet_number in range(1, n + 1):
        result = calculate_queuing_delay_ms(packet_size_in_bytes, rate_in_Gbps, packet_number)
        all_queueing_delays.append(result)

    average_delay = sum(all_queueing_delays) / len(all_queueing_delays)

    print(f'\nqueueing delay averaged over the first {len(all_queueing_delays)} packets (ms)', average_delay)

