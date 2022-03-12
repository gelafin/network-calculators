# Author: Mark Mendez
# Date: 03/11/2022

from NetworkingCalculators import stuff_bytes


if __name__ == '__main__':
    # input is delimited by spaces
    input_string_hex = '78h 04h 1Bh 7Ah 01h 1Bh'
    special_chars_to_escape_char_list = {
        'soh': ['esc', 'x'],
        'eot': ['esc', 'y'],
        'esc': ['esc', 'z'],
    }
    hex_conversion_table = {
        'soh': '01h',
        'eot': '04h',
        'esc': '1Bh',
        'x':   '78h',
        'y':   '79h',
        'z':   '7Ah'
    }
    include_framing_chars = True

    result = stuff_bytes(
        input_string_hex, special_chars_to_escape_char_list, hex_conversion_table, include_framing_chars
    )

    framing_char_reminder = '(without framing chars)' if include_framing_chars is False else '(includes framing chars)'
    print(f'stuffed string{framing_char_reminder}:\n{result}')
