# app.py  -  LLM Assistive Task Evaluation App
# Run:  python app.py
# Then open:  http://localhost:5000

from flask import Flask, render_template, request, session, redirect, url_for, make_response
import pandas as pd
import csv
import io
import os

app = Flask(__name__)
app.secret_key = 'eval_study_2026'

# ---------------------------------------------------------------
# 1. CONFIGURATION
# ---------------------------------------------------------------

CSV_PATH = os.path.join(os.path.dirname(__file__), 'data', 'model_outputs.csv')

DIMENSIONS = ['Clarity', 'Appropriateness', 'Accuracy', 'Consistency', 'Empathy']

EXPERTISE_OPTIONS = [
    'Communication disabilities / AAC',
    'Cognitive / intellectual disabilities',
    'AI accessibility research',
    'Text simplification / plain language',
    'Clinical / rehabilitation',
    'Other',
]

# ---------------------------------------------------------------
# 2. LOAD CSV DATA
# ---------------------------------------------------------------

def load_prompts():
    df = pd.read_csv(CSV_PATH)

    def clean(value):
        if pd.isna(value):
            return 'No output generated.'
        return str(value).strip()

    prompts = []
    for _, row in df.iterrows():
        prompts.append({
            'id':         row['prompt_id'],
            'category':   row['category'],
            'disability': row['disability_type'],
            'task':       row['task_type'].replace('_', ' ').title(),
            'context':    clean(row['notes']),
            'prompt':     clean(row['prompt_text']),
            'model_a':    clean(row['gpt4_output']),
            'model_b':    clean(row['claude_output']),
            'model_c':    clean(row['groq_output']),
        })

    return prompts

PROMPTS = load_prompts()
TOTAL   = len(PROMPTS)
print(f"Loaded {TOTAL} prompts from CSV")

# ---------------------------------------------------------------
# 3. ROUTES
# ---------------------------------------------------------------

# ROUTE 0: Consent form
@app.route('/consent', methods=['GET', 'POST'])
def consent():
    error = None

    if request.method == 'POST':
        agreed    = request.form.get('agreed')
        signature = request.form.get('signature', '').strip()

        if not agreed or not signature:
            error = 'Please check the consent box and type your full name to continue.'
        else:
            session['consented'] = True
            return redirect(url_for('index'))

    return render_template('consent.html', error=error)


# ROUTE 1: Evaluator info screen
@app.route('/', methods=['GET', 'POST'])
def index():
    error = None

    if 'consented' not in session:
        return redirect(url_for('consent'))

    if request.method == 'POST':
        name        = request.form.get('name', '').strip()
        expertise   = request.form.get('expertise', '').strip()
        institution = request.form.get('institution', '').strip()

        if not name or not expertise:
            error = 'Please enter your name and select your area of expertise.'
        else:
            session['evaluator'] = {
                'name':        name,
                'expertise':   expertise,
                'institution': institution,
            }
            session['current'] = 0
            session['ratings'] = {}

            return redirect(url_for('evaluate'))

    return render_template('index.html',
                           expertise_options=EXPERTISE_OPTIONS,
                           error=error)


# ROUTE 2: Evaluation screen
@app.route('/evaluate', methods=['GET', 'POST'])
def evaluate():
    if 'consented' not in session:
        return redirect(url_for('consent'))
    if 'evaluator' not in session:
        return redirect(url_for('index'))

    if request.method == 'POST':
        idx = session['current']

        session['ratings'][str(idx)] = {
            'model_a': [int(request.form.get(f'a_{d}', 0)) for d in range(5)],
            'model_b': [int(request.form.get(f'b_{d}', 0)) for d in range(5)],
            'model_c': [int(request.form.get(f'c_{d}', 0)) for d in range(5)],
            'notes':   request.form.get('notes', '').strip(),
        }
        session.modified = True

        action = request.form.get('action')

        if action == 'next' and idx < TOTAL - 1:
            session['current'] += 1
        elif action == 'back' and idx > 0:
            session['current'] -= 1
        elif action == 'submit':
            return redirect(url_for('done'))

        return redirect(url_for('evaluate'))

    idx    = session['current']
    prompt = PROMPTS[idx]
    saved  = session['ratings'].get(str(idx), {})

    return render_template('evaluate.html',
        evaluator = session['evaluator'],
        prompt    = prompt,
        idx       = idx,
        total     = TOTAL,
        percent   = round((idx / TOTAL) * 100),
        saved     = saved,
        dims      = DIMENSIONS,
    )


# ROUTE 3: Completion screen
@app.route('/done')
def done():
    if 'consented' not in session:
        return redirect(url_for('consent'))
    if 'evaluator' not in session:
        return redirect(url_for('index'))

    return render_template('done.html',
        evaluator = session['evaluator'],
        total     = TOTAL,
    )


# ROUTE 4: Download ratings as CSV
@app.route('/download')
def download():
    if 'evaluator' not in session:
        return redirect(url_for('index'))

    evaluator = session['evaluator']
    ratings   = session.get('ratings', {})

    output = io.StringIO()
    writer = csv.writer(output)

    writer.writerow([
        'evaluator_name', 'evaluator_expertise', 'evaluator_institution',
        'prompt_id', 'disability_type', 'task_type', 'context',
        'model_a_clarity', 'model_a_appropriateness', 'model_a_accuracy',
        'model_a_consistency', 'model_a_empathy',
        'model_b_clarity', 'model_b_appropriateness', 'model_b_accuracy',
        'model_b_consistency', 'model_b_empathy',
        'model_c_clarity', 'model_c_appropriateness', 'model_c_accuracy',
        'model_c_consistency', 'model_c_empathy',
        'notes',
    ])

    for i, prompt in enumerate(PROMPTS):
        r = ratings.get(str(i), {
            'model_a': [0, 0, 0, 0, 0],
            'model_b': [0, 0, 0, 0, 0],
            'model_c': [0, 0, 0, 0, 0],
            'notes':   '',
        })
        writer.writerow([
            evaluator['name'],
            evaluator['expertise'],
            evaluator['institution'],
            prompt['id'],
            prompt['disability'],
            prompt['task'],
            prompt['context'],
            *r['model_a'],
            *r['model_b'],
            *r['model_c'],
            r['notes'],
        ])

    response = make_response(output.getvalue())
    filename = f"ratings_{evaluator['name'].replace(' ', '_')}.csv"
    response.headers['Content-Disposition'] = f'attachment; filename={filename}'
    response.headers['Content-Type'] = 'text/csv'
    return response


# ---------------------------------------------------------------
# 4. START THE APP
# ---------------------------------------------------------------

if __name__ == '__main__':
    app.run(debug=True, port=5000)