# Author: Mark Mendez
# Date: 01/29/2022


from math import ceil
from heapq import heappush


def kibs_to_bytes(kibs: int | float):
    """
    Simple conversion from MiB to bytes
    :param kibs: number of MiB
    :return: number of bytes
    """
    return kibs * 1024  # to bytes


def mibs_to_bytes(mibs: int | float):
    """
    Simple conversion from MiB to bytes
    :param mibs: number of MiB
    :return: number of bytes
    """
    return mibs * 1024 * 1024  # to KiB to bytes


def calculate_transmission_time_statistical_multiplexing(known_data: dict) -> list[tuple]:
    """
    Calculates transmission times for each file, in a continuous alternating-packet transmission network.
    The order of elements in known_data['file_sizes_bytes'] should reflect the turn order given to packet senders
        by the transmission medium.
    !!! Ignores processing and queuing delays
    !!! Assumes partial packets are padded to known_data['packet_payload_size_bytes']
    :param known_data: dict in the following form:
                      'total_link_rate_Mbps': int or float,
                      'sharing_computers_count': int,  # Should match len(file_sizes_bytes).
                      #                                  For now, only 1 file per computer
                      'starting_time_seconds': int or float,
                      'file_sizes_bytes': [
                          int or float,
                          ...
                      ],
                      'packet_payload_size_bytes': int or float,
                      'packet_header_size_bytes': int or float
    :return: number of seconds for each file to finish transmitting, as a list of tuples,
             where index 0 is the time in seconds and index 1 is the turn order
    """
    # unpack known data
    total_link_rate_bps = known_data['total_link_rate_Mbps'] * 1000 * 1000  # convert to Kbps to bps
    sharing_computers_count = known_data['sharing_computers_count']
    starting_time_seconds = known_data['starting_time_seconds']
    file_sizes_bytes = known_data['file_sizes_bytes']
    packet_payload_size_bytes = known_data['packet_payload_size_bytes']
    packet_header_size_bytes = known_data['packet_header_size_bytes']

    # calculate number of packet payloads needed to send each file (rounding up because of assumed padding)
    needed_packets = [ceil(size_in_bytes / packet_payload_size_bytes) for size_in_bytes in file_sizes_bytes]

    # calculate total size per packet
    total_packet_size_bits = (packet_header_size_bytes + packet_payload_size_bytes) * 8  # * 8 to convert to bits

    # make a list (heapq for efficiency) of turn-order indices of files in size order (small to large)
    file_order_indices_by_needed_packets_asc = []
    for turn_order, packet_count in enumerate(needed_packets):
        heappush(file_order_indices_by_needed_packets_asc, (packet_count, turn_order))  # sort by size but pair with index
        #                                                                       (docs say turn_order is a tie-breaker)

    # Calculate the number of packets that will have been sent when each file finishes transmitting,
    #     iterating in size order (because the smallest packet finishes transmitting first, etc)
    # Calculate the first one separately to initialize
    packet_count = file_order_indices_by_needed_packets_asc[0][0]
    turn_order = file_order_indices_by_needed_packets_asc[0][1]
    total_packets_at_file_done = packet_count * sharing_computers_count
    total_packets_at_each_file_done = [total_packets_at_file_done]
    time_when_file_done_seconds = (
            total_packets_at_file_done
            * total_packet_size_bits
            / total_link_rate_bps
            + starting_time_seconds
    )
    times_at_each_packet_done_seconds = [(time_when_file_done_seconds, turn_order)]
    for index in range(1, len(file_order_indices_by_needed_packets_asc)):
        # this is the next smallest packet (rounded; post-rounding duplicates sorted by turn order)
        size_and_order = file_order_indices_by_needed_packets_asc[index]
        total_packets_needed_this_file = size_and_order[0]
        turn_order = size_and_order[1]
        total_packets_at_previous_done = total_packets_at_each_file_done[index - 1]

        # calculate total packets this file will wait for
        remaining_packets_this_file_at_previous_done = total_packets_needed_this_file - (total_packets_at_previous_done / sharing_computers_count)
        total_packets_to_finish_this_file_at_previous_done = remaining_packets_this_file_at_previous_done * (sharing_computers_count - index)
        total_packets_at_file_done = total_packets_to_finish_this_file_at_previous_done + total_packets_at_previous_done

        # calculate total time for this file to finish
        time_when_file_done_seconds = (
                total_packets_at_file_done
                * total_packet_size_bits
                / total_link_rate_bps
                + starting_time_seconds
        )

        # add to output variable
        times_at_each_packet_done_seconds.append((time_when_file_done_seconds, turn_order))

    return times_at_each_packet_done_seconds



def calculate_utilization_circuit_switched(total_user_count : int, utilization_per_user: list[dict]):
    """
    Calculates total utilization in a circuit-switched network with equal bandwidth share among users
    :param total_user_count: number of users sharing equal bandwidth
    :param utilization_per_user: list of dicts in the following form, where each dict is a group of users who have
                                 the exact same utilization:
                                 {'user_count': int, 'utilization_percent_per_user': int}
    :return: total percent utilization of the network
    """
    # validate user count
    user_count_validation = sum([group['user_count'] for group in utilization_per_user])
    if total_user_count != user_count_validation:
        raise ValueError('check your total user count and per user count; they have to match')

    bandwidth_percent_allocated_per_user = 100 / total_user_count

    total_utilization_decimal = 0
    for user_group in utilization_per_user:
        group_user_count = user_group['user_count']
        group_utilization_multiplier = user_group['utilization_percent_per_user'] / 100
        bandwidth_allocated_per_user_multiplier = bandwidth_percent_allocated_per_user / 100

        total_utilization_decimal += (group_user_count
                                      * group_utilization_multiplier
                                      * bandwidth_allocated_per_user_multiplier
                                      )

    total_utilization_percent = total_utilization_decimal * 100

    return total_utilization_percent


def calculate_queuing_delay(packet_size_in_bytes: int, rate_in_Gbps: float, packet_number: int):
    """
    Calculates network queueing delay
    :param packet_size_in_bytes: bytes per packet
    :param rate_in_Gbps: total connection speed / link transmission rate, in Gbps
    :param packet_number: packet to find queueing delay for (number of previous packets + 1)
    :return: queuing delay in milliseconds
    """
    # convert units
    packet_size_in_bits = packet_size_in_bytes * 8
    rate_in_bps = rate_in_Gbps * 1000 * 1000 * 1000  # convert from Gbps to Mbps to Kbps to bps

    # calculate rate per packet
    transmission_time_per_packet_in_ms = packet_size_in_bits / rate_in_bps * 1000  # * 1000 to convert to ms

    # calculate queuing delay
    previous_packet_count = packet_number - 1
    queueing_delay = transmission_time_per_packet_in_ms * previous_packet_count

    return queueing_delay


def calculate_circuit_switched_transmission_time_ms(file_size_in_bytes: int, rate_in_Gbps: float,
                                                    setup_time_in_ms: float, total_users_sharing: int
                                                    ):
    """
    Calculates the end-to-end transmission time for one file in a circuit-switched network
    :param file_size_in_bytes: number of bytes to be transmitted, in bytes
    :param rate_in_Gbps: total connection speed / link transmission rate, in Gbps
    :param setup_time_in_ms: milliseconds of setup time for the connection
    :param total_users_sharing: if TDM with equal share, enter the number of users sharing bandwidth
    :return: transmission time of the file in the network, in ms
    """
    # convert units
    file_size_in_bits = file_size_in_bytes * 8
    rate_in_bps = rate_in_Gbps * 1000 * 1000 * 1000 / total_users_sharing  # Gbps to bps shared by 15 users

    # calculate transmission time
    transmission_time_in_ms = file_size_in_bits / rate_in_bps * 1000 + setup_time_in_ms  # * 1000 to convert to ms

    return transmission_time_in_ms


def calculate_transmission_time_simple(length_in_bytes: int, rate_in_Mbps: float) -> float:
    """
    Calculates network transmission time for a packet
    :param length_in_bytes: size of each packet --in bytes--
    :param rate_in_Mbps: transmission rate --in Mbps--
    :return: transmission time --in milliseconds--
    """
    packet_length = length_in_bytes
    rate = float(rate_in_Mbps)

    # convert all applicable values to bits
    packet_length *= 8  # from bytes to bits
    rate *= 1000 * 1000  # from Mbps to Kbps to bps

    # calculate transmission time in seconds
    transmission_time = float(packet_length) / rate

    # convert transmission time to milliseconds
    transmission_time *= 1000

    return transmission_time


def calculate_network_utilization(known_data: dict, window_size: int = None) -> float:
    """
    Calculates network utilization given some raw data
    :param known_data: dict containing the following data, with these keys
                       'length_in_bytes': (int) size of each packet --in bytes--
                       'rate_in_Mbps': (float) transmission rate --in Mbps--
                       'rtt_in_ms': (int) round-trip-time, or 2 * propagation delay, --in milliseconds--
    :param window_size: if using pipelining, set this to
                        the number of --bytes-- advertised as the receiver's window size
    :return: network utilization --in raw decimal--
    """
    # unpack known data
    packet_length = known_data['length_in_bytes']
    rate = known_data['rate_in_Mbps']
    rtt = float(known_data['rtt_in_ms'])

    # calculate transmission time in milliseconds
    transmission_time = calculate_transmission_time_simple(packet_length, rate)

    # calculate total time
    total_time = transmission_time + rtt

    # calculate utilization
    utilization = transmission_time / total_time

    # if pipelining, calculate the number of packets that can be sent with the given window size
    pipelined_packet_count = 1  # default is one packet, because pipelining is optional for this function
    if window_size is not None:
        pipelined_packet_count = int(window_size / packet_length)

    # account for pipelining (if not using pipelining, this just multiplies by 1)
    utilization *= pipelined_packet_count

    return utilization


def find_seq_and_ack_numbers(initial_ack_number: int, packets: list):
    """
    Solves problems like 'Suppose segments P, Q, and R arrive at Host B in order.
             What is the acknowledgment number on the segment sent in response to segment R?'
    :param initial_ack_number: ack number before the first packet of sizes is sent
    :param packets: list of dicts holding each packet's "name" and "size", in order sent
    :return: dict wherein keys are packet names, values are dicts in JSON format with
             sequence number, size, and ack number that should be sent in response, assuming in-order arrival
    """
    # return variable
    packet_data_out = {}

    prev_ack_number = initial_ack_number
    for packet in packets:
        # packet name
        packet_name = packet['name']

        # packet size
        packet_size = packet['size']

        # sequence number is previous packet's ack number (assuming in-order arrival and immediate ack)
        packet_seq_number = prev_ack_number

        # ack number sent in response is one more than is inside this packet
        #     (assuming in-order arrival and immediate ack)
        presumed_ack_number = packet_seq_number + packet_size

        # update prev ack for next iteration
        prev_ack_number = presumed_ack_number

        # add values to return variable
        packet_data_out[packet_name] = {
            'seq_number': packet_seq_number,
            'size': packet_size,
            'in_order_ack_number': presumed_ack_number
        }

    return packet_data_out


# TODO: this is copied from the utilization calculator except returns seconds not ms; merge into one function
def calculate_transmission_time_seconds(length_in_bytes: int | float, rate_in_Mbps: int | float) -> float:
    """
    Calculates network transmission time for a packet
    :param length_in_bytes: size of each packet --in bytes--
    :param rate_in_Mbps: transmission rate --in Mbps--
    :return: transmission time --in seconds--
    """
    packet_length = length_in_bytes
    rate = rate_in_Mbps

    # convert all applicable values to bits
    packet_length *= 8  # from bytes to bits
    rate *= 1000 * 1000  # from Mbps to Kbps to bps

    # calculate transmission time in seconds
    transmission_time_seconds = packet_length / rate

    return transmission_time_seconds


def calculate_propagation_delay_seconds(propagation_distance_km: int | float,
                                        propagation_speed_meters_per_second: dict
                                        ):
    """
    Calculates propagation delay
    :param propagation_distance_km:
    :param propagation_speed_meters_per_second:
    :return: propagation delay in seconds
    """
    # convert from km to meters
    propagation_distance_meters = propagation_distance_km * 1000

    # reconstruct from scientific notation like 2.5 * 10^8
    propagation_speed_mps_float = (propagation_speed_meters_per_second['significant_digits']
                                   * 10 ** propagation_speed_meters_per_second['exponent']
                                   )
    propagation_delay_seconds = propagation_distance_meters / propagation_speed_mps_float

    return propagation_delay_seconds


def calculate_end_to_end_voip_delay(known_data: dict):
    """
    Calculates end-to-end voip delay--that is, the time taken to convert and transmit one packet to another host.
    Assumes partial packets are not sent or de-converted.
    :param known_data: dict in the following form:
                       {
                        'conversion_rate_Kbps': int or float,
                        'link_transmission_rate_Mbps': int or float,
                        'packet_length_bytes': int or float,
                        'propagation_distance_km': int or float,
                        'propagation_speed_meters_per_second':
                            {'significant_digits': int or float, 'exponent': int or float}
                       }
    :return: time taken from when conversion begins to when de-conversion begins, in milliseconds
    """
    # unpack known variables
    conversion_rate_bps = known_data['conversion_rate_Kbps'] * 1000  # convert to bps
    link_transmission_rate_Mbps = known_data['link_transmission_rate_Mbps']
    packet_length_bytes = known_data['packet_length_bytes']
    propagation_distance_km = known_data['propagation_distance_km']
    propagation_speed_meters_per_second = known_data['propagation_speed_meters_per_second']

    # propagation delay
    propagation_delay_seconds = calculate_propagation_delay_seconds(propagation_distance_km,
                                                                    propagation_speed_meters_per_second
                                                                    )

    # transmission delay
    transmission_delay_seconds = calculate_transmission_time_seconds(packet_length_bytes, link_transmission_rate_Mbps)

    # conversion delay
    packet_length_bits = packet_length_bytes * 8
    conversion_delay_seconds = packet_length_bits / conversion_rate_bps

    # end-to-end voip delay, from start of conversion to end of propagation
    voip_delay_seconds = conversion_delay_seconds + transmission_delay_seconds + propagation_delay_seconds

    # convert to ms
    voip_delay_ms = voip_delay_seconds * 1000

    return voip_delay_ms


