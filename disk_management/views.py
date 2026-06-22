# Create your views here.
# disk_management/views.py
import json
from django.shortcuts import render
from .algorithms import fcfs, sstf, scan, cscan, look, clook

ALGORITHMS = {
    'fcfs':  'FCFS (First Come First Served)',
    'sstf':  'SSTF (Shortest Seek Time First)',
    'scan':  'SCAN (Elevator)',
    'cscan': 'C-SCAN (Circular SCAN)',
    'look':  'LOOK',
    'clook': 'C-LOOK (Circular LOOK)',
}

NEEDS_DIRECTION = {'scan', 'look'}


def index(request):
    context = {
        'algorithms': ALGORITHMS,
        'result':     None,
        'error':      None,
        'form':       {},
    }

    if request.method == 'POST':
        try:
            algo         = request.POST.get('algorithm', 'fcfs')
            raw_requests = request.POST.get('requests', '').strip()
            initial_head = int(request.POST.get('initial_head', 50))
            disk_size    = int(request.POST.get('disk_size', 200))
            direction    = request.POST.get('direction', 'right')

            # Accept comma or space separated
            raw_requests = raw_requests.replace(',', ' ')
            requests = [int(x.strip()) for x in raw_requests.split() if x.strip()]

            if not requests:
                raise ValueError("Please enter at least one disk request.")
            if initial_head < 0 or initial_head >= disk_size:
                raise ValueError(f"Initial head position must be between 0 and {disk_size - 1}.")
            if any(r < 0 or r >= disk_size for r in requests):
                raise ValueError(f"All requests must be between 0 and {disk_size - 1}.")
            if disk_size < 2:
                raise ValueError("Disk size must be at least 2.")
            if direction not in ('left', 'right'):
                direction = 'right'

            if algo == 'fcfs':
                result = fcfs(requests, initial_head, disk_size)
            elif algo == 'sstf':
                result = sstf(requests, initial_head, disk_size)
            elif algo == 'scan':
                result = scan(requests, initial_head, direction, disk_size)
            elif algo == 'cscan':
                result = cscan(requests, initial_head, disk_size)
            elif algo == 'look':
                result = look(requests, initial_head, direction, disk_size)
            elif algo == 'clook':
                result = clook(requests, initial_head, disk_size)
            else:
                raise ValueError(f"Unknown algorithm: {algo}")

            # Build chart data — sequence index on X axis, cylinder on Y axis
            chart_data = {
                'labels':   list(range(len(result['sequence']))),
                'sequence': result['sequence'],
            }
            result['chart_data_json']       = json.dumps(chart_data)
            result['needs_direction']       = algo in NEEDS_DIRECTION

            context['result'] = result
            context['form'] = {
                'algorithm':    algo,
                'requests':     raw_requests,
                'initial_head': initial_head,
                'disk_size':    disk_size,
                'direction':    direction,
            }

        except ValueError as e:
            context['error'] = str(e)
        except Exception as e:
            context['error'] = f"Unexpected error: {str(e)}"

    return render(request, 'disk_management/index.html', context)