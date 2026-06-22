# disk_management/algorithms.py


def _build_result(algo_name, initial_head, sequence, disk_size):
    """
    Package the result dict returned to the view.

    sequence : ordered list of cylinder positions the head visits
               (includes the initial head position as first element)
    """
    # Compute seek distances between consecutive positions
    seek_distances = []
    for i in range(1, len(sequence)):
        seek_distances.append(abs(sequence[i] - sequence[i - 1]))

    total_seek    = sum(seek_distances)
    avg_seek      = round(total_seek / len(seek_distances), 2) if seek_distances else 0

    # Build step-by-step table
    steps = []
    for i in range(1, len(sequence)):
        steps.append({
            'from':     sequence[i - 1],
            'to':       sequence[i],
            'distance': abs(sequence[i] - sequence[i - 1]),
        })

    return {
        'algo_name':      algo_name,
        'initial_head':   initial_head,
        'sequence':       sequence,
        'seek_distances': seek_distances,
        'total_seek':     total_seek,
        'avg_seek':       avg_seek,
        'steps':          steps,
        'disk_size':      disk_size,
    }


# ─── FCFS ────────────────────────────────────────────────────────────────────

def fcfs(requests, initial_head, disk_size=200):
    """
    First Come First Served — service requests in the order they arrive.
    """
    sequence = [initial_head] + list(requests)
    return _build_result('FCFS', initial_head, sequence, disk_size)


# ─── SSTF ────────────────────────────────────────────────────────────────────

def sstf(requests, initial_head, disk_size=200):
    """
    Shortest Seek Time First — always service the closest pending request.
    """
    pending  = list(requests)
    sequence = [initial_head]
    current  = initial_head

    while pending:
        closest = min(pending, key=lambda r: abs(r - current))
        sequence.append(closest)
        current = closest
        pending.remove(closest)

    return _build_result('SSTF', initial_head, sequence, disk_size)


# ─── SCAN ────────────────────────────────────────────────────────────────────

def scan(requests, initial_head, direction='right', disk_size=200):
    """
    SCAN (Elevator) — head moves in one direction servicing requests,
    reaches the end of disk, then reverses direction.
    direction: 'left' or 'right'
    """
    pending  = sorted(set(requests))
    sequence = [initial_head]

    left  = sorted([r for r in pending if r < initial_head], reverse=True)
    right = sorted([r for r in pending if r >= initial_head])

    if direction == 'right':
        sequence += right
        if right and right[-1] != disk_size - 1:
            sequence.append(disk_size - 1)   # go to end
        sequence += left
    else:
        sequence += left
        if left and left[-1] != 0:
            sequence.append(0)               # go to beginning
        sequence += right

    return _build_result(f'SCAN ({direction})', initial_head, sequence, disk_size)


# ─── C-SCAN ──────────────────────────────────────────────────────────────────

def cscan(requests, initial_head, disk_size=200):
    """
    Circular SCAN — head moves right servicing requests, jumps back to
    cylinder 0 (without servicing) when it reaches the end, then continues right.
    """
    pending  = sorted(set(requests))
    sequence = [initial_head]

    right = sorted([r for r in pending if r >= initial_head])
    left  = sorted([r for r in pending if r < initial_head])

    sequence += right
    if right[-1] != disk_size - 1 if right else True:
        sequence.append(disk_size - 1)   # go to end
    sequence.append(0)                   # jump to beginning (no service)
    sequence += left

    return _build_result('C-SCAN', initial_head, sequence, disk_size)


# ─── LOOK ────────────────────────────────────────────────────────────────────

def look(requests, initial_head, direction='right', disk_size=200):
    """
    LOOK — like SCAN but head only goes as far as the last request
    in each direction (does NOT go all the way to the disk boundary).
    """
    pending  = sorted(set(requests))
    sequence = [initial_head]

    left  = sorted([r for r in pending if r < initial_head], reverse=True)
    right = sorted([r for r in pending if r >= initial_head])

    if direction == 'right':
        sequence += right
        sequence += left
    else:
        sequence += left
        sequence += right

    return _build_result(f'LOOK ({direction})', initial_head, sequence, disk_size)


# ─── C-LOOK ──────────────────────────────────────────────────────────────────

def clook(requests, initial_head, disk_size=200):
    """
    C-LOOK — like C-SCAN but head only goes as far as the last request
    in the right direction, then jumps to the smallest pending request.
    """
    pending  = sorted(set(requests))
    sequence = [initial_head]

    right = sorted([r for r in pending if r >= initial_head])
    left  = sorted([r for r in pending if r < initial_head])

    sequence += right
    if left:
        sequence.append(left[0])    # jump to smallest (no service on jump)
        sequence += left

    return _build_result('C-LOOK', initial_head, sequence, disk_size)