# Author: Mark Mendez
# Date: 01/29/2022
import heapq
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
        heappush(file_order_indices_by_needed_packets_asc,
                 (packet_count, turn_order))  # sort by size but pair with index
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
        remaining_packets_this_file_at_previous_done = total_packets_needed_this_file - (
                total_packets_at_previous_done / sharing_computers_count)
        total_packets_to_finish_this_file_at_previous_done = remaining_packets_this_file_at_previous_done * (
                sharing_computers_count - index)
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


def calculate_utilization_circuit_switched(total_user_count: int, utilization_per_user: list[dict]):
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


def calculate_tcp_timeout_interval_ms(estimated_rtt_ms: int | float, dev_rtt_ms: int | float,
                                      deviation_margin_multiplier: int | float = 4
                                      ):
    """
    Calculates timeout interval as EstimatedRTT + Margin * DevRTT
    :param estimated_rtt_ms: estimated round-trip time, in milliseconds
    :param dev_rtt_ms: deviation of round-trip-time data, in milliseconds
    :param deviation_margin_multiplier: (optional) multiplier to use for deviation margin other than 4
    :return: timeout interval, in milliseconds
    """
    return estimated_rtt_ms + deviation_margin_multiplier * dev_rtt_ms


def calculate_dev_rtt_ms(previous_dev_rtt_ms: int | float, sample_rtt_ms: int | float,
                         previous_estimated_rtt_ms: int | float, weight_multiplier: int | float = 0.25
                         ):
    """
    Calculates deviation of round-trip time as (1-β)prev_DevRTT + β(SampleRTT - prev_EstimatedRTT)
    :param previous_dev_rtt_ms: previously calculated deviation of round-trip-time, in milliseconds
    :param sample_rtt_ms: recently measured rtt, in milliseconds
    :param previous_estimated_rtt_ms: estimated round-trip time, in milliseconds
    :param weight_multiplier: the beta (β) in the equation; multiplier to determine weight of recentness (as EWMA)
    :return: deviation of round-trip time, in milliseconds
    """
    return ((1 - weight_multiplier) * previous_dev_rtt_ms + weight_multiplier *
            (sample_rtt_ms - previous_estimated_rtt_ms))


def calculate_est_rtt_ms(previous_estimated_rtt_ms: int | float, sample_rtts_ms: list[int | float],
                         weight_multiplier: int | float = 0.25, recursion_index: int = 0
                         ):
    """
    Calculates estimated round-trip time as (1-α)PreviousEstimatedRTT + (α)SampleRTT
    :param previous_estimated_rtt_ms: previously calculated estimated round-trip time, in milliseconds
    :param sample_rtts_ms: list of recently measured round-trip times, in milliseconds. Most recent last
    :param weight_multiplier: the alpha (α) in the equation; multiplier to determine weight of recentness (as EWMA)
    :param recursion_index: (used to iterate during recursion)
    :return: estimated round-trip time, in milliseconds
    """
    # base case: no more sample RTTs to use;
    # return the est RTT calculated from the previous sample RTT as the final result
    if recursion_index >= len(sample_rtts_ms):
        return previous_estimated_rtt_ms

    # get a sample RTT
    this_sample_rtt_ms = sample_rtts_ms[recursion_index]

    # calculate estimated RTT given this sample RTT
    this_est_rtt_ms = (1 - weight_multiplier) * previous_estimated_rtt_ms + weight_multiplier * this_sample_rtt_ms

    # recursive case: calculate the next est RTT
    return calculate_est_rtt_ms(this_est_rtt_ms, sample_rtts_ms, weight_multiplier, recursion_index + 1)


def simulate_tcp_slowstart(mss_bytes: int, slow_start_congestion_window_limit_bytes: int, packet_count: int,
                           packet_size_bytes: int = None
                           ):
    """
    Simulates the TCP slow-start phase by calculating changes in congestion window size
    :param mss_bytes: Maximum Segment Size, in bytes
    :param slow_start_congestion_window_limit_bytes: congestion window size limit for the slow-start phase, in bytes
    :param packet_count: how many packets are waiting to be sent
    :param packet_size_bytes: (optional) size of each packet. If None, packet_size will be set to mss_bytes
    :return: data for each group, as a list of dicts, each formatted as below.
             {
              'group_number': int,
              'congestion_window_bytes': int,
              'congestion_window_mss': int,
              'packets_sent_this_group': list[int]
              }
    """
    data_out = []
    packet_size_bytes = packet_size_bytes if packet_size_bytes is not None else mss_bytes
    current_congestion_window_mss = 1
    current_congestion_window_bytes = mss_bytes * current_congestion_window_mss
    packet_index = 0
    group_number = 1
    while packet_index < packet_count:
        # form a packet group according to congestion window size
        packet_group_bytes = 0
        packet_group_numbers = []
        packet_number_out = packet_index + 1  # start numbering from 1
        while (packet_group_bytes <= current_congestion_window_bytes - packet_size_bytes
               and packet_number_out - 1 < packet_count):  # while there's still room (and waiting packets)
            # add a packet
            packet_group_numbers.append(packet_number_out)

            # maintain loop
            packet_group_bytes += packet_size_bytes
            packet_number_out += 1

        # save this packet group's details for return
        data_out.append({
            'group_number': group_number,
            'congestion_window_mss': current_congestion_window_mss,
            'congestion_window_bytes': current_congestion_window_bytes,
            'packets_sent_this_group': packet_group_numbers
        })

        # increase congestion window size so the next packet group can be bigger
        if current_congestion_window_bytes >= slow_start_congestion_window_limit_bytes:
            # increase linearly if at the limit
            current_congestion_window_mss += 1
        else:
            # increase exponentially if not at the limit
            current_congestion_window_mss *= 2

        # update current_congestion_window_mss's dependent variable
        current_congestion_window_bytes = mss_bytes * current_congestion_window_mss

        # maintain loop
        group_number += 1
        packet_index += len(packet_group_numbers)

    return data_out


def calculate_TCP_fair_bandwidth_Mbps(total_available_bandwidth_Mbps: int | float,
                                      app_connections: list[dict]) -> list[dict]:
    """
    Calculates available bandwidth for each application, according to TCP "fairness" rules
    :param total_available_bandwidth_Mbps: total bandwidth that needs to be divided, in Mbps
    :param app_connections: list of dicts, in the following form.
                            [{'app_name': str, 'connection_count': int}]
    :return: bandwidth available to each app, in the following form.
             ['app_name': str, 'bandwidth_Mbps': int]
    """
    # calculate the total number of connections
    total_connection_count = sum([app_details['connection_count'] for app_details in app_connections])

    # calculate available bandwidth for each connection
    per_connection_bandwidth_Mbps = total_available_bandwidth_Mbps / total_connection_count

    # calculate available bandwidth for each app (which may have multiple connections)
    data_out = []
    for app_details_in in app_connections:
        # copy app name and calculate bandwidth to be allocated to all of this app's connections
        app_details_out = {
            'app_name': app_details_in['app_name'],
            'bandwidth_Mbps': per_connection_bandwidth_Mbps * app_details_in['connection_count']
        }

        # add to return variable
        data_out.append(app_details_out)

    return data_out


def calculate_effective_delay_ms(utilization_decimal: int | float, initial_delay_ms: int | float):
    """
    Calculates effective delay in a network as Delay = InitialDelay / (1 - Usage).
    This can be useful to account for the effects of congestion
    :param utilization_decimal: network utilization, as a decimal number
    :param initial_delay_ms: initial network delay, in milliseconds
    :return: effective network delay, in milliseconds
    """
    return initial_delay_ms / (1 - utilization_decimal)


def calculate_initial_delay_ms(effective_delay_ms: int | float, utilization_when_delay_known_decimal: int | float):
    """
    Calculates initial network delay as InitialDelay = Delay (1 - Usage)
    :param effective_delay_ms: known effective network delay, in milliseconds
    :param utilization_when_delay_known_decimal: network utilization when effective_delay_ms was measured,
           as a decimal number
    :return: initial network delay, in milliseconds
    """
    return effective_delay_ms * (1 - utilization_when_delay_known_decimal)
