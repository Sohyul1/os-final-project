# memory_management/algorithms.py


def _build_memory_map(total_size, blocks, allocations):
    """
    Build a list of segments for visualization.
    Each segment: { 'label': str, 'start': int, 'size': int, 'type': 'process'|'free'|'os' }
    We reserve block 0 implicitly as OS space (size = blocks[0].start if blocks start >0).
    This is a flat representation of memory after allocation.
    """
    segments = []
    # Walk memory in order of block starts, filling gaps
    # blocks is a list of dicts: {id, start, size, allocated_to, remaining}
    sorted_blocks = sorted(blocks, key=lambda b: b['start'])
    for b in sorted_blocks:
        if b['allocated_to']:
            # Show allocated portion
            segments.append({
                'label': b['allocated_to'],
                'start': b['start'],
                'size': b['size'] - b['remaining'],
                'type': 'process'
            })
            if b['remaining'] > 0:
                segments.append({
                    'label': 'Free',
                    'start': b['start'] + (b['size'] - b['remaining']),
                    'size': b['remaining'],
                    'type': 'free'
                })
        else:
            segments.append({
                'label': 'Free',
                'start': b['start'],
                'size': b['size'],
                'type': 'free'
            })
    return segments


def _init_blocks(block_sizes):
    """Convert list of block sizes into block dicts with computed start addresses."""
    blocks = []
    address = 0
    for i, size in enumerate(block_sizes):
        blocks.append({
            'id': i,
            'start': address,
            'size': size,
            'original_size': size,
            'allocated_to': None,
            'remaining': size,
        })
        address += size
    return blocks


def _allocation_result(blocks, processes, algo_name, compaction_applied=False):
    """Package the result dict returned to the view."""
    allocation_table = []
    unallocated = []
    for p in processes:
        allocated = False
        for b in blocks:
            if b['allocated_to'] == p['pid']:
                allocation_table.append({
                    'pid': p['pid'],
                    'size': p['size'],
                    'block_id': b['id'],
                    'block_start': b['start'],
                    'allocated': True,
                })
                allocated = True
                break
        if not allocated:
            allocation_table.append({
                'pid': p['pid'],
                'size': p['size'],
                'block_id': None,
                'block_start': None,
                'allocated': False,
            })
            unallocated.append(p['pid'])

    total_memory = sum(b['original_size'] for b in blocks)
    used_memory = sum(p['size'] for p in processes if p['pid'] not in unallocated)
    free_memory = total_memory - used_memory
    fragmentation = sum(b['remaining'] for b in blocks if b['allocated_to'] is None)

    segments = _build_memory_map(total_memory, blocks, allocation_table)

    return {
        'algo_name': algo_name,
        'allocation_table': allocation_table,
        'unallocated': unallocated,
        'total_memory': total_memory,
        'used_memory': used_memory,
        'free_memory': free_memory,
        'external_fragmentation': fragmentation,
        'compaction_applied': compaction_applied,
        'segments': segments,
    }


# ─── FIRST FIT ────────────────────────────────────────────────────────────────

def first_fit(block_sizes, processes, with_compaction=False):
    """
    Allocate each process to the first block with enough space.
    If with_compaction=True and a process can't be allocated,
    compact free space and retry.
    """
    blocks = _init_blocks(block_sizes)
    compaction_applied = False

    def try_allocate(blocks, processes):
        for p in processes:
            if any(b['allocated_to'] == p['pid'] for b in blocks):
                continue  # already allocated
            for b in blocks:
                if b['allocated_to'] is None and b['remaining'] >= p['size']:
                    b['allocated_to'] = p['pid']
                    b['remaining'] -= p['size']
                    break

    try_allocate(blocks, processes)

    if with_compaction:
        unallocated_pids = [
            p['pid'] for p in processes
            if not any(b['allocated_to'] == p['pid'] for b in blocks)
        ]
        if unallocated_pids:
            blocks = _compact(blocks)
            compaction_applied = True
            try_allocate(blocks, [p for p in processes if p['pid'] in unallocated_pids])

    return _allocation_result(blocks, processes, 'First Fit', compaction_applied)


# ─── BEST FIT ─────────────────────────────────────────────────────────────────

def best_fit(block_sizes, processes, with_compaction=False):
    """
    Allocate each process to the smallest block that still fits it.
    """
    blocks = _init_blocks(block_sizes)
    compaction_applied = False

    def try_allocate(blocks, processes):
        for p in processes:
            if any(b['allocated_to'] == p['pid'] for b in blocks):
                continue
            # Find all fitting free blocks, pick smallest remaining
            candidates = [
                b for b in blocks
                if b['allocated_to'] is None and b['remaining'] >= p['size']
            ]
            if candidates:
                chosen = min(candidates, key=lambda b: b['remaining'])
                chosen['allocated_to'] = p['pid']
                chosen['remaining'] -= p['size']

    try_allocate(blocks, processes)

    if with_compaction:
        unallocated_pids = [
            p['pid'] for p in processes
            if not any(b['allocated_to'] == p['pid'] for b in blocks)
        ]
        if unallocated_pids:
            blocks = _compact(blocks)
            compaction_applied = True
            try_allocate(blocks, [p for p in processes if p['pid'] in unallocated_pids])

    return _allocation_result(blocks, processes, 'Best Fit', compaction_applied)


# ─── WORST FIT ────────────────────────────────────────────────────────────────

def worst_fit(block_sizes, processes, with_compaction=False):
    """
    Allocate each process to the largest available block.
    """
    blocks = _init_blocks(block_sizes)
    compaction_applied = False

    def try_allocate(blocks, processes):
        for p in processes:
            if any(b['allocated_to'] == p['pid'] for b in blocks):
                continue
            candidates = [
                b for b in blocks
                if b['allocated_to'] is None and b['remaining'] >= p['size']
            ]
            if candidates:
                chosen = max(candidates, key=lambda b: b['remaining'])
                chosen['allocated_to'] = p['pid']
                chosen['remaining'] -= p['size']

    try_allocate(blocks, processes)

    if with_compaction:
        unallocated_pids = [
            p['pid'] for p in processes
            if not any(b['allocated_to'] == p['pid'] for b in blocks)
        ]
        if unallocated_pids:
            blocks = _compact(blocks)
            compaction_applied = True
            try_allocate(blocks, [p for p in processes if p['pid'] in unallocated_pids])

    return _allocation_result(blocks, processes, 'Worst Fit', compaction_applied)


# ─── COMPACTION ───────────────────────────────────────────────────────────────

def _compact(blocks):
    """
    Merge all free fragments into a single contiguous free block at the end.
    Allocated blocks slide down to fill gaps (addresses recomputed).
    Returns a new block list.
    """
    allocated = [b for b in blocks if b['allocated_to'] is not None]
    total_free = sum(b['remaining'] for b in blocks)

    new_blocks = []
    address = 0
    for b in allocated:
        used = b['original_size'] - b['remaining']
        new_blocks.append({
            'id': b['id'],
            'start': address,
            'size': used,          # block is now exactly the size of the process
            'original_size': used,
            'allocated_to': b['allocated_to'],
            'remaining': 0,
        })
        address += used

    # One big free block at the end
    if total_free > 0:
        new_blocks.append({
            'id': len(new_blocks),
            'start': address,
            'size': total_free,
            'original_size': total_free,
            'allocated_to': None,
            'remaining': total_free,
        })

    return new_blocks