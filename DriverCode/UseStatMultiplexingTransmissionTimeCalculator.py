# Author: Mark Mendez
# Date: 01/30/2022


from NetworkingCalculators import calculate_transmission_time_statistical_multiplexing, mibs_to_bytes, kibs_to_bytes


if __name__ == '__main__':
    # test
    known_data = {
        'total_link_rate_Mbps': 37.6,
        'sharing_computers_count': 2,  # should match len(file_sizes_bytes). For now, only 1 file per computer
        'starting_time_seconds': 0,
        'file_sizes_bytes': [
            mibs_to_bytes(11),
            kibs_to_bytes(36)
        ],
        'packet_payload_size_bytes': 1000,
        'packet_header_size_bytes': 24
    }

    result = calculate_transmission_time_statistical_multiplexing(known_data)
    print('transmission delay with statistical multiplexing:', result)
