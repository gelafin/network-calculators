# Author: Mark Mendez
# Date: 03/04/2022

from NetworkingCalculators import generate_exponential_backoff_wait_time_seeds_ms, calculate_bit_time_ms


if __name__ == '__main__':
    BIT_TIME_MULTIPLIER_CONSTANT = 512  # most common standard is 512

    collision_count = 10
    link_transmission_rate_Mbps = 10

    wait_time_seeds_ms = generate_exponential_backoff_wait_time_seeds_ms(collision_count)
    bit_time_ms = calculate_bit_time_ms(link_transmission_rate_Mbps)

    if wait_time_seeds_ms is not None and len(wait_time_seeds_ms) > 0:
        smallest_seed_ms = wait_time_seeds_ms[0]  # typically 0
        largest_seed_ms = wait_time_seeds_ms[-1]

        smallest_wait_ms = smallest_seed_ms * BIT_TIME_MULTIPLIER_CONSTANT * bit_time_ms
        largest_wait_ms = largest_seed_ms * BIT_TIME_MULTIPLIER_CONSTANT * bit_time_ms

        print('range of wait times is\n')
        print(f'\tfrom {smallest_seed_ms} ms * {BIT_TIME_MULTIPLIER_CONSTANT} = {smallest_wait_ms} ms')
        print(f'\tto {largest_seed_ms} ms * {BIT_TIME_MULTIPLIER_CONSTANT} = {largest_wait_ms} ms')
        print('\nCalculated bit time of %.9fms' % bit_time_ms)
    else:
        print('Unexpected error. Keep calm and remember Jesus saves')
