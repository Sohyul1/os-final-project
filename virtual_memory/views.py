# Create your views here.
# virtual_memory/views.py
import json
from django.shortcuts import render
from .algorithms import fifo, lru, optimal

ALGORITHMS = {
    'fifo':    'FIFO (First-In First-Out)',
    'lru':     'LRU (Least Recently Used)',
    'optimal': 'Optimal (OPT / Belady\'s)',
}


def index(request):
    context = {
        'algorithms': ALGORITHMS,
        'result':     None,
        'error':      None,
        'form':       {},
    }

    if request.method == 'POST':
        try:
            algo          = request.POST.get('algorithm', 'fifo')
            raw_pages     = request.POST.get('page_string', '').strip()
            num_frames    = int(request.POST.get('num_frames', 3))

            # Accept space-separated or comma-separated page strings
            raw_pages = raw_pages.replace(',', ' ')
            page_string = [int(x.strip()) for x in raw_pages.split() if x.strip()]

            if not page_string:
                raise ValueError("Please enter a page reference string.")
            if num_frames < 1:
                raise ValueError("Number of frames must be at least 1.")
            if num_frames > 20:
                raise ValueError("Number of frames must be 20 or fewer.")
            if len(page_string) > 50:
                raise ValueError("Page string must be 50 references or fewer.")

            if algo == 'fifo':
                result = fifo(page_string, num_frames)
            elif algo == 'lru':
                result = lru(page_string, num_frames)
            elif algo == 'optimal':
                result = optimal(page_string, num_frames)
            else:
                raise ValueError(f"Unknown algorithm: {algo}")

            # Serialize chart data — keep Django tags out of <script> blocks
            result['chart_steps_json']  = json.dumps(result['steps'])
            result['chart_faults_json'] = json.dumps(result['cumulative_faults'])

            # Fault/hit bar chart data
            result['chart_summary_json'] = json.dumps({
                'labels': ['Page Faults', 'Page Hits'],
                'data':   [result['total_faults'], result['total_hits']],
                'colors': ['#e15759', '#59a14f'],
            })

            context['result'] = result
            context['form'] = {
                'algorithm':   algo,
                'page_string': raw_pages,
                'num_frames':  num_frames,
            }

        except ValueError as e:
            context['error'] = str(e)
        except Exception as e:
            context['error'] = f"Unexpected error: {str(e)}"

    return render(request, 'virtual_memory/index.html', context)