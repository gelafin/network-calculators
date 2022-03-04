# Author: Mark Mendez
# Date: 01/30/2022


from NetworkingCalculators import calculate_network_utilization, calculate_transmission_time_simple_ms


if __name__ == '__main__':
    # =============
    # set test data
    # =============
    known_data = {
        'length_in_bytes': 1004,
        'rate_in_Mbps': 11,
        'rtt_in_ms': 10.0 * 2  # end-to-end delay * 2
    }
    window_size_in_bytes = 5569  # set to None if not pipelining

    # how many digits --after-- the decimal point should the answers be?
    percentage_precision = 1
    raw_precision = 5

    # =============
    # use test data
    # =============
    # get transmission time by itself
    transmission_time_in_ms = calculate_transmission_time_simple_ms(known_data['length_in_bytes'], known_data['rate_in_Mbps'])
    print(f'\ntransmission time (ms): {transmission_time_in_ms}')

    # get utilization
    utilization_in_decimal = round(calculate_network_utilization(known_data, window_size_in_bytes), raw_precision)
    utilization_percentage = round(utilization_in_decimal * 100, percentage_precision)
    print(f'\nutilization (decimal): {utilization_in_decimal}, which is {utilization_percentage}%')

