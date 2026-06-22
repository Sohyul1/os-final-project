# virtual_memory/algorithms.py


def _build_result(page_string, num_frames, frames_over_time, fault_flags, algo_name):
    """
    Package the simulation result into a dict for the view.

    frames_over_time : list of frame snapshots (list of lists), one per page reference
    fault_flags      : list of bools, True = page fault occurred at that step
    """
    total_faults = sum(1 for f in fault_flags if f)
    total_hits   = len(page_string) - total_faults
    fault_rate   = round(total_faults / len(page_string) * 100, 2) if page_string else 0

    # Build trace rows for the table
    trace = []
    for i, page in enumerate(page_string):
        trace.append({
            'step':        i + 1,
            'page':        page,
            'frames':      list(frames_over_time[i]),   # snapshot of frames at this step
            'page_fault':  fault_flags[i],
        })

    # Cumulative fault count over time (for the line chart)
    cumulative_faults = []
    count = 0
    for f in fault_flags:
        if f:
            count += 1
        cumulative_faults.append(count)

    return {
        'algo_name':          algo_name,
        'page_string':        page_string,
        'num_frames':         num_frames,
        'trace':              trace,
        'total_faults':       total_faults,
        'total_hits':         total_hits,
        'fault_rate':         fault_rate,
        'cumulative_faults':  cumulative_faults,
        'steps':              list(range(1, len(page_string) + 1)),
        'max_frames':         num_frames,
    }


# ─── FIFO ─────────────────────────────────────────────────────────────────────

def fifo(page_string, num_frames):
    """
    First-In First-Out page replacement.
    The page that has been in memory the longest is replaced first.
    """
    frames      = []          # current pages in memory
    fault_flags = []
    frames_over_time = []
    queue       = []          # tracks insertion order

    for page in page_string:
        fault = False

        if page not in frames:
            fault = True
            if len(frames) < num_frames:
                frames.append(page)
                queue.append(page)
            else:
                # Evict the oldest page
                oldest = queue.pop(0)
                idx = frames.index(oldest)
                frames[idx] = page
                queue.append(page)

        fault_flags.append(fault)
        # Pad snapshot to num_frames slots with '-' for empty frames
        snapshot = frames + ['-'] * (num_frames - len(frames))
        frames_over_time.append(snapshot)

    return _build_result(page_string, num_frames, frames_over_time, fault_flags, 'FIFO')


# ─── LRU ──────────────────────────────────────────────────────────────────────

def lru(page_string, num_frames):
    """
    Least Recently Used page replacement.
    The page that was used least recently is replaced.
    """
    frames      = []
    fault_flags = []
    frames_over_time = []
    recent_use  = []   # index 0 = least recently used, last = most recent

    for page in page_string:
        fault = False

        if page in frames:
            # Hit — update recency only
            recent_use.remove(page)
            recent_use.append(page)
        else:
            fault = True
            if len(frames) < num_frames:
                frames.append(page)
            else:
                # Evict least recently used
                lru_page = recent_use.pop(0)
                idx = frames.index(lru_page)
                frames[idx] = page
            recent_use.append(page)

        fault_flags.append(fault)
        snapshot = frames + ['-'] * (num_frames - len(frames))
        frames_over_time.append(list(snapshot))

    return _build_result(page_string, num_frames, frames_over_time, fault_flags, 'LRU')


# ─── OPTIMAL ──────────────────────────────────────────────────────────────────

def optimal(page_string, num_frames):
    """
    Optimal (OPT / Belady's) page replacement.
    Replace the page that will not be used for the longest time in the future.
    """
    frames      = []
    fault_flags = []
    frames_over_time = []

    for i, page in enumerate(page_string):
        fault = False

        if page not in frames:
            fault = True
            if len(frames) < num_frames:
                frames.append(page)
            else:
                # For each frame, find the next use of that page in the future
                future = page_string[i + 1:]
                farthest_idx = -1
                page_to_evict = None

                for f in frames:
                    if f not in future:
                        # This page is never used again — perfect eviction candidate
                        page_to_evict = f
                        break
                    else:
                        next_use = future.index(f)
                        if next_use > farthest_idx:
                            farthest_idx = next_use
                            page_to_evict = f

                idx = frames.index(page_to_evict)
                frames[idx] = page

        fault_flags.append(fault)
        snapshot = frames + ['-'] * (num_frames - len(frames))
        frames_over_time.append(snapshot)

    return _build_result(page_string, num_frames, frames_over_time, fault_flags, 'Optimal (OPT)')