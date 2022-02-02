# Author: Mark Mendez
# Date: 02/01/2022


from NetworkingCalculators import calculate_est_rtt_ms


if __name__ == '__main__':
    initial_est_rtt_ms = 34.4
    sample_rtts_ms = [43.8, 44.9, 17.4]  # most recent last
    weight_multiplier = 0.4

    result = calculate_est_rtt_ms(initial_est_rtt_ms, sample_rtts_ms, weight_multiplier)
    print('estimated RTT (ms): ', result)
