# Author: Mark Mendez
# Date: 02/01/2022


from NetworkingCalculators import calculate_est_rtt_ms


if __name__ == '__main__':
    initial_est_rtt_ms = 47.5
    sample_rtts_ms = [33.1, 24.8, 11.1]  # most recent last
    weight_multiplier = 0.4

    result = calculate_est_rtt_ms(initial_est_rtt_ms, sample_rtts_ms, weight_multiplier)
    print('estimated RTT (ms): ', result)
