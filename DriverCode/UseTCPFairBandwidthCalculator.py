# Author: Mark Mendez
# Date: 02/02/2022
import json

from NetworkingCalculators import calculate_TCP_fair_bandwidth_Mbps


if __name__ == '__main__':
    total_available_bandwidth_Mbps = 5000
    app_connections = [
        {'app_name': 'A',
         'connection_count': 42
         },
        {'app_name': 'B',
         'connection_count': 3
         },
        {'app_name': 'C',
         'connection_count': 14
         },
    ]

    result = calculate_TCP_fair_bandwidth_Mbps(total_available_bandwidth_Mbps, app_connections)
    print('\nTCP bandwidth allocated to each app (Mbps)', json.dumps(result, indent=4))
