# Author: Mark Mendez
# Date: 01/30/2022


from NetworkingCalculators import find_seq_and_ack_numbers


if __name__ == '__main__':
    # test
    initial_ack = 2541
    known_packet_data = [
        {
            'name': 'P',
            'size': 413
        },
        {
            'name': 'Q',
            'size': 382
        },
        {
            'name': 'R',
            'size': 245
        }
    ]
    full_packet_data = find_seq_and_ack_numbers(initial_ack, known_packet_data)
    print(full_packet_data)
