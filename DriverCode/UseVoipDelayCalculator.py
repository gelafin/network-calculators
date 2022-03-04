# Author: Mark Mendez
# Date: 01/30/2022


from NetworkingCalculators import calculate_end_to_end_voip_delay, calculate_propagation_delay_seconds


if __name__ == '__main__':
    # test
    known_data = {
        'conversion_rate_Kbps': 43,
        'link_transmission_rate_Mbps': 2.3,
        'packet_length_bytes': 46,
        'propagation_distance_km': 2500,
        'propagation_speed_meters_per_second':
            {'significant_digits': 2.5, 'exponent': 8}  # e.g., 2.5 * 10^8,
        #                                                 where 2.5 is the significant digits, and 8 is the exponent
    }

    result = calculate_end_to_end_voip_delay(known_data)
    print('\nend-to-end voip delay (ms): ', result)

    print('\npropagation delay (ms): ',
          calculate_propagation_delay_seconds(
              known_data['propagation_distance_km'], known_data['propagation_speed_meters_per_second']
                                             ) * 1000
          )
