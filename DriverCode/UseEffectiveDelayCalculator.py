# Author: Mark Mendez
# Date: 02/02/2022


from NetworkingCalculators import calculate_effective_delay_ms, calculate_initial_delay_ms


if __name__ == '__main__':
    # solves questions like "given an effective delay of x ms when utilization is y%,
    #     find effective delay when usage is z%"
    known_effective_delay_ms = 14.5
    utilization_when_delay_known_decimal = 0
    utilization_during_result_delay_decimal = 0.078

    initial_delay = calculate_initial_delay_ms(known_effective_delay_ms, utilization_when_delay_known_decimal)

    effective_delay_result_ms = calculate_effective_delay_ms(utilization_during_result_delay_decimal, initial_delay)

    print(f'\neffective delay when utilization is {utilization_during_result_delay_decimal}: '
          f'{effective_delay_result_ms}')
