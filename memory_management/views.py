from django.shortcuts import render
import json
from .algorithms import first_fit, best_fit, worst_fit
# Create your views here.

ALGORITHMS = {
    'first_fit': 'First Fit',
    'best_fit':  'Best Fit',
    'worst_fit': 'Worst Fit',
}


def index(request):
    context = {
        'algorithms': ALGORITHMS,
        'result': None,
        'error': None,
        'form': {},
    }

    if request.method == 'POST':
        try:
            algo           = request.POST.get('algorithm', 'first_fit')
            raw_blocks     = request.POST.get('block_sizes', '').strip()
            raw_proc_names = request.POST.get('process_names', '').strip()
            raw_proc_sizes = request.POST.get('process_sizes', '').strip()
            compaction     = request.POST.get('compaction', 'off') == 'on'

            block_sizes = [int(x.strip()) for x in raw_blocks.split(',') if x.strip()]
            proc_names  = [x.strip() for x in raw_proc_names.split(',') if x.strip()]
            proc_sizes  = [int(x.strip()) for x in raw_proc_sizes.split(',') if x.strip()]

            if not block_sizes:
                raise ValueError("Please enter at least one memory block size.")
            if len(proc_names) != len(proc_sizes):
                raise ValueError("Number of process names and sizes must match.")
            if any(s <= 0 for s in block_sizes):
                raise ValueError("All block sizes must be positive integers.")
            if any(s <= 0 for s in proc_sizes):
                raise ValueError("All process sizes must be positive integers.")

            processes = [
                {'pid': proc_names[i], 'size': proc_sizes[i]}
                for i in range(len(proc_names))
            ]

            if algo == 'first_fit':
                result = first_fit(block_sizes, processes, with_compaction=compaction)
            elif algo == 'best_fit':
                result = best_fit(block_sizes, processes, with_compaction=compaction)
            elif algo == 'worst_fit':
                result = worst_fit(block_sizes, processes, with_compaction=compaction)
            else:
                raise ValueError(f"Unknown algorithm: {algo}")

            # ── Build Chart.js data from segments ──────────────────────────
            # We draw one stacked horizontal bar per "row" (just one row = full memory).
            # Each segment becomes a dataset slice.
            segments = result['segments']

            chart_labels  = ['Memory']
            chart_datasets = []

            type_colors = {
                'process': '#4e79a7',
                'free':    '#d3d3d3',
            }

            # Assign distinct colors to each process
            process_palette = [
                '#4e79a7', '#f28e2b', '#e15759', '#76b7b2',
                '#59a14f', '#edc948', '#b07aa1', '#ff9da7',
                '#9c755f', '#bab0ac'
            ]
            process_color_map = {}
            color_idx = 0
            for seg in segments:
                if seg['type'] == 'process' and seg['label'] not in process_color_map:
                    process_color_map[seg['label']] = process_palette[color_idx % len(process_palette)]
                    color_idx += 1

            for seg in segments:
                color = process_color_map.get(seg['label'], '#d3d3d3')
                chart_datasets.append({
                    'label': f"{seg['label']} ({seg['size']} KB)",
                    'data': [seg['size']],
                    'backgroundColor': color,
                    'borderColor': '#333',
                    'borderWidth': 1,
                    'segment_type': seg['type'],
                    'segment_start': seg['start'],
                    'segment_size': seg['size'],
                    'segment_label': seg['label'],
                })

            result['chart_datasets_json'] = json.dumps(chart_datasets)
            result['chart_labels_json']   = json.dumps(chart_labels)

            context['result'] = result
            context['form'] = {
                'algorithm':     algo,
                'block_sizes':   raw_blocks,
                'process_names': raw_proc_names,
                'process_sizes': raw_proc_sizes,
                'compaction':    compaction,
            }

        except Exception as e:
            context['error'] = str(e)

    return render(request, 'memory_management/index.html', context)