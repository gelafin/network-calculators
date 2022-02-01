# Author: Mark Mendez
# Date: 02/01/2022
import json
from NetworkingCalculators import simulate_tcp_slowstart


if __name__ == '__main__':
    # known
    mss_bytes = 1460
    slowstart_congestion_window_limit_bytes = 11680
    packet_count = 15

    result = simulate_tcp_slowstart(mss_bytes, slowstart_congestion_window_limit_bytes, packet_count)
    print('\nslow start simulation results:\n', json.dumps(result, indent=4))
