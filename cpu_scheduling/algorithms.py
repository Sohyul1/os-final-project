from collections import deque

def _compute_stats(processes, timeline):
    """
    Given original process list and a Gantt timeline,
    compute waiting time, turnaround time, response time for each process.

    processes: list of dicts with keys: pid, arrival, burst, priority (optional)
    timeline:  list of (pid, start, end) tuples
    """
    stats = {}
    for p in processes:
        stats[p['pid']] = {
            'pid': p['pid'],
            'arrival': p['arrival'],
            'burst': p['burst'],
            'first_run': None,
            'finish': None,
        }

    for (pid, start, end) in timeline:
        if stats[pid]['first_run'] is None:
            stats[pid]['first_run'] = start
        stats[pid]['finish'] = end

    result = []
    for p in processes:
        s = stats[p['pid']]
        turnaround = s['finish'] - p['arrival']
        waiting = turnaround - p['burst']
        response = s['first_run'] - p['arrival']
        result.append({
            'pid': p['pid'],
            'arrival': p['arrival'],
            'burst': p['burst'],
            'finish': s['finish'],
            'turnaround': turnaround,
            'waiting': waiting,
            'response': response,
        })
    return result


# FCFS 

def fcfs(processes):
    """First Come First Served (non-preemptive)."""
    procs = sorted(processes, key=lambda p: (p['arrival'], p['pid']))
    timeline = []
    current_time = 0
    for p in procs:
        start = max(current_time, p['arrival'])
        end = start + p['burst']
        timeline.append((p['pid'], start, end))
        current_time = end
    return timeline, _compute_stats(processes, timeline)


# SJF Non-Preemptive

def sjf_non_preemptive(processes):
    """Shortest Job First — Non-Preemptive."""
    remaining = [dict(p) for p in processes]
    timeline = []
    current_time = 0
    done = []

    while remaining:
        # Processes that have arrived
        available = [p for p in remaining if p['arrival'] <= current_time]
        if not available:
            # CPU idle: jump to next arrival
            current_time = min(p['arrival'] for p in remaining)
            available = [p for p in remaining if p['arrival'] <= current_time]

        # Pick shortest burst (tie-break: earlier arrival, then pid)
        chosen = min(available, key=lambda p: (p['burst'], p['arrival'], p['pid']))
        remaining.remove(chosen)

        start = current_time
        end = start + chosen['burst']
        timeline.append((chosen['pid'], start, end))
        current_time = end
        done.append(chosen)

    return timeline, _compute_stats(processes, timeline)


# SJF Preemptive (SRTF) 

def sjf_preemptive(processes):
    """Shortest Remaining Time First — Preemptive SJF."""
    remaining = {p['pid']: p['burst'] for p in processes}
    procs = sorted(processes, key=lambda p: p['arrival'])
    timeline = []
    current_time = 0
    done = set()
    last_pid = None

    all_times = sorted(set(
        [p['arrival'] for p in processes] +
        [p['arrival'] + p['burst'] for p in processes]
    ))

    while len(done) < len(processes):
        available = [
            p for p in processes
            if p['arrival'] <= current_time and p['pid'] not in done
        ]
        if not available:
            current_time += 1
            continue

        chosen = min(available, key=lambda p: (remaining[p['pid']], p['arrival'], p['pid']))

        if timeline and timeline[-1][0] == chosen['pid']:
            # Extend last segment
            pid, start, end = timeline[-1]
            timeline[-1] = (pid, start, end + 1)
        else:
            timeline.append((chosen['pid'], current_time, current_time + 1))

        remaining[chosen['pid']] -= 1
        current_time += 1

        if remaining[chosen['pid']] == 0:
            done.add(chosen['pid'])

    # Merge consecutive same-pid segments for a cleaner Gantt
    merged = []
    for seg in timeline:
        if merged and merged[-1][0] == seg[0] and merged[-1][2] == seg[1]:
            merged[-1] = (merged[-1][0], merged[-1][1], seg[2])
        else:
            merged.append(list(seg))

    merged = [tuple(s) for s in merged]
    return merged, _compute_stats(processes, merged)


# Priority Non-Preemptive 

def priority_non_preemptive(processes):
    """Priority Scheduling — Non-Preemptive. Lower number = higher priority."""
    remaining = [dict(p) for p in processes]
    timeline = []
    current_time = 0

    while remaining:
        available = [p for p in remaining if p['arrival'] <= current_time]
        if not available:
            current_time = min(p['arrival'] for p in remaining)
            available = [p for p in remaining if p['arrival'] <= current_time]

        chosen = min(available, key=lambda p: (p['priority'], p['arrival'], p['pid']))
        remaining.remove(chosen)

        start = current_time
        end = start + chosen['burst']
        timeline.append((chosen['pid'], start, end))
        current_time = end

    return timeline, _compute_stats(processes, timeline)




def priority_preemptive(processes):
    """Priority Scheduling — Preemptive. Lower number = higher priority."""
    remaining = {p['pid']: p['burst'] for p in processes}
    timeline = []
    current_time = 0
    done = set()

    max_time = sum(p['burst'] for p in processes) + max(p['arrival'] for p in processes) + 1

    while len(done) < len(processes) and current_time < max_time:
        available = [
            p for p in processes
            if p['arrival'] <= current_time and p['pid'] not in done
        ]
        if not available:
            current_time += 1
            continue

        chosen = min(available, key=lambda p: (p['priority'], p['arrival'], p['pid']))

        if timeline and timeline[-1][0] == chosen['pid']:
            pid, start, end = timeline[-1]
            timeline[-1] = (pid, start, end + 1)
        else:
            timeline.append((chosen['pid'], current_time, current_time + 1))

        remaining[chosen['pid']] -= 1
        current_time += 1

        if remaining[chosen['pid']] == 0:
            done.add(chosen['pid'])

    merged = []
    for seg in timeline:
        if merged and merged[-1][0] == seg[0] and merged[-1][2] == seg[1]:
            merged[-1] = (merged[-1][0], merged[-1][1], seg[2])
        else:
            merged.append(list(seg))

    merged = [tuple(s) for s in merged]
    return merged, _compute_stats(processes, merged)




def round_robin(processes, quantum):
    """Round Robin with given time quantum."""
    remaining = {p['pid']: p['burst'] for p in processes}
    procs = sorted(processes, key=lambda p: (p['arrival'], p['pid']))
    timeline = []
    current_time = 0
    queue = deque()
    enqueued = set()
    proc_map = {p['pid']: p for p in procs}
    done = set()

    # Seed the queue with processes arriving at time 0
    for p in procs:
        if p['arrival'] <= current_time and p['pid'] not in enqueued:
            queue.append(p['pid'])
            enqueued.add(p['pid'])

    while len(done) < len(processes):
        if not queue:
            # CPU idle
            next_arrival = min(
                p['arrival'] for p in procs if p['pid'] not in done and p['pid'] not in enqueued
            )
            current_time = next_arrival
            for p in procs:
                if p['arrival'] <= current_time and p['pid'] not in enqueued:
                    queue.append(p['pid'])
                    enqueued.add(p['pid'])
            continue

        pid = queue.popleft()
        run_time = min(quantum, remaining[pid])
        start = current_time
        end = start + run_time
        timeline.append((pid, start, end))
        remaining[pid] -= run_time
        current_time = end

        # Enqueue newly arrived processes (arrived during this slice)
        for p in procs:
            if p['arrival'] <= current_time and p['pid'] not in enqueued:
                queue.append(p['pid'])
                enqueued.add(p['pid'])

        if remaining[pid] == 0:
            done.add(pid)
        else:
            queue.append(pid)

    return timeline, _compute_stats(processes, timeline)