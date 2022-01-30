# Author: Mark Mendez
# Date: 01/30/2022


from NetworkingCalculators import calculate_utilization_circuit_switched


if __name__ == '__main__':
    # test circuit-switched utilization calculator
    total_user_count = 5  # this should match the total per-user user_counts
    utilization_per_user = [
        {'user_count': 2, 'utilization_percent_per_user': 85},
        {'user_count': 2, 'utilization_percent_per_user': 44},
        {'user_count': 1, 'utilization_percent_per_user': 11}
    ]

    result = calculate_utilization_circuit_switched(total_user_count, utilization_per_user)
    print('\nutilization percent: ', result)
