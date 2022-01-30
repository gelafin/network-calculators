# Author: Mark Mendez
# Date: 01/30/2022


from NetworkingCalculators import calculate_circuit_switched_transmission_time_ms


if __name__ == '__main__':
    # test
    file_size_in_MiB = 9  # set to None if entering file_size_in_bytes
    file_size_in_bytes = None  # set to None if entering file_size_in_MiB
    rate_in_Gbps = 47.7
    total_users_sharing = 15
    setup_time_in_ms = 58.3

    file_size_in_bytes = file_size_in_MiB * 1024 * 1024 if file_size_in_MiB is not None else file_size_in_bytes
    result = calculate_circuit_switched_transmission_time_ms(file_size_in_bytes, rate_in_Gbps,
                                                             setup_time_in_ms, total_users_sharing
                                                             )
    print('\ntransmission time (ms): ', result)

