# Author: Mark Mendez
# Date: 03/03/2022

from NetworkingCalculators import calculate_end_to_end_delay_packet_switched_ms


if __name__ == '__main__':
    # test
    link_transmission_rate_Mbps = 100
    packet_length_bytes = 1500
    propagation_distance_km = 2500
    propagation_speed_meters_per_second = {'significant_digits': 2.5, 'exponent': 8}  # e.g., 2.5 * 10^8,
    #                                     where 2.5 is the significant digits, and 8 is the exponent
    packet_number = 5  # position in queue
    intermediate_router_count = 0  # routers between sending and receiving host

    result = calculate_end_to_end_delay_packet_switched_ms(
        packet_length_bytes, link_transmission_rate_Mbps, packet_number, propagation_distance_km,
        propagation_speed_meters_per_second, intermediate_router_count
    )

    print('end-to-end delay in milliseconds:', result)
