from django.shortcuts import render
import json
from .algorithms import (
    fcfs, sjf_non_preemptive, sjf_preemptive,
    priority_non_preemptive, priority_preemptive, round_robin
)
# Create your views here.

ALGORITHMS = {
    'fcfs': 'FCFS',
    'sjf_np': 'SJF (Non-Preemptive)',
    'sjf_p': 'SJF (Preemptive / SRTF)',
    'priority_np': 'Priority (Non-Preemptive)',
    'priority_p': 'Priority (Preemptive)',
    'rr': 'Round Robin',
}

NEEDS_PRIORITY = {'priority_np', 'priority_p'}
NEEDS_QUANTUM = {'rr'}


def index(request):
    context = {
        'algorithms': ALGORITHMS,
        'result': None,
        'error': None,
    }

    if request.method == 'POST':
        try:
            algo = request.POST.get('algorithm', 'fcfs')
            raw_pids = request.POST.get('pids', '').strip()
            raw_arrivals = request.POST.get('arrivals', '').strip()
            raw_bursts = request.POST.get('bursts', '').strip()
            raw_priorities = request.POST.get('priorities', '').strip()
            quantum = int(request.POST.get('quantum', 2))

            pids = [x.strip() for x in raw_pids.split(',') if x.strip()]
            arrivals = [int(x.strip()) for x in raw_arrivals.split(',')]
            bursts = [int(x.strip()) for x in raw_bursts.split(',')]

            if not (len(pids) == len(arrivals) == len(bursts)):
                raise ValueError("Number of PIDs, arrival times, and burst times must match.")

            processes = []
            for i, pid in enumerate(pids):
                p = {
                    'pid': pid,
                    'arrival': arrivals[i],
                    'burst': bursts[i],
                    'priority': 0,
                }
                if algo in NEEDS_PRIORITY:
                    priorities = [int(x.strip()) for x in raw_priorities.split(',')]
                    if len(priorities) != len(pids):
                        raise ValueError("Number of priorities must match number of processes.")
                    p['priority'] = priorities[i]
                processes.append(p)

            # Dispatch to the correct algorithm
            if algo == 'fcfs':
                timeline, stats = fcfs(processes)
            elif algo == 'sjf_np':
                timeline, stats = sjf_non_preemptive(processes)
            elif algo == 'sjf_p':
                timeline, stats = sjf_preemptive(processes)
            elif algo == 'priority_np':
                timeline, stats = priority_non_preemptive(processes)
            elif algo == 'priority_p':
                timeline, stats = priority_preemptive(processes)
            elif algo == 'rr':
                timeline, stats = round_robin(processes, quantum)
            else:
                raise ValueError(f"Unknown algorithm: {algo}")

            # Compute averages
            avg_waiting = sum(s['waiting'] for s in stats) / len(stats)
            avg_turnaround = sum(s['turnaround'] for s in stats) / len(stats)
            avg_response = sum(s['response'] for s in stats) / len(stats)

            # Prepare Gantt data for Chart.js
            # Each bar: { pid, start, duration }
            gantt_data = [
                {'pid': pid, 'start': start, 'duration': end - start}
                for (pid, start, end) in timeline
            ]

            # Unique PIDs for color assignment in the template
            unique_pids = list(dict.fromkeys(pid for pid, _, _ in timeline))

            context['result'] = {
                'algorithm_name': ALGORITHMS[algo],
                'stats': stats,
                'avg_waiting': round(avg_waiting, 2),
                'avg_turnaround': round(avg_turnaround, 2),
                'avg_response': round(avg_response, 2),
                'gantt_data_json': json.dumps(gantt_data),
                'unique_pids_json': json.dumps(unique_pids),
                'timeline': timeline,
            }
            context['form'] = {
                'algorithm': algo,
                'pids': raw_pids,
                'arrivals': raw_arrivals,
                'bursts': raw_bursts,
                'priorities': raw_priorities,
                'quantum': quantum,
            }

        except Exception as e:
            context['error'] = str(e)

    return render(request, 'cpu_scheduling/index.html', context)