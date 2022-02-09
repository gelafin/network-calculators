# Author: Mark Mendez
# Date: 02/07/2022


from NetworkingCalculators import match_ip_address_prefix, decimal_ip_address_to_binary


if __name__ == '__main__':
    routing_table = [  # use spaces every EIGHT binary digits (e.g., 10001100 00011011 01011101 01)
        '10001100 00011011 01011101',
        '10001100 00011011 01011101 000',
        '10001100 00011011 01011101 01',
        '10001100 00011011 01011110 00100'
    ]
    default_port = 4
    ip_address_dotted_decimal = '155.124.185.14'

    # if port numbers are different from indexes, map them. If not, assign empty list
    indexes_to_ports = []

    binary_ip = decimal_ip_address_to_binary(ip_address_dotted_decimal)
    print('\nip address in binary:', binary_ip)

    routing_match_index = match_ip_address_prefix(binary_ip, routing_table)

    result = routing_match_index
    if result is None:
        # no matches; use default port
        result = default_port
        print('\nnone matched; using default port', default_port)

    else:
        # got a match; print closest match
        if len(indexes_to_ports) > 0:
            result = routing_table[routing_match_index]

        print('\nprefix match output port:', result, '\nprefix matched:', routing_table[routing_match_index])
