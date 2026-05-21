from django.shortcuts import render, redirect
from .questions import questions
from .models import result
import random


def home(request):
    topics = {topic: len(qs) for topic, qs in questions.items()}
    total = sum(topics.values())
    return render(request, 'quizbot/home.html', {'topics': topics, 'total': total})


def start(request):
    if request.method != 'POST':
        return redirect('home')

    name = request.POST.get('name', '').strip()
    if not name:
        name = 'студент'

    mode = request.POST.get('mode', 'quick')

    if mode == 'all':
        qs = []
        for topic, items in questions.items():
            for q in items:
                qs.append({**q, 'topic': topic})
    elif mode == 'quick':
        all_q = []
        for topic, items in questions.items():
            for q in items:
                all_q.append({**q, 'topic': topic})
        qs = random.sample(all_q, min(10, len(all_q)))
    elif mode in questions:
        qs = [{**q, 'topic': mode} for q in questions[mode]]
    else:
        return redirect('home')

    request.session['name'] = name
    request.session['questions'] = qs
    request.session['mode'] = mode
    request.session['current'] = 0
    request.session['score'] = 0
    request.session['wrong'] = []

    return redirect('question')


def question(request):
    qs = request.session.get('questions', [])
    current = request.session.get('current', 0)

    if not qs or current >= len(qs):
        return redirect('results')

    q = qs[current]
    total = len(qs)
    feedback = request.session.pop('feedback', None)

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'hint':
            request.session['show_hint'] = True
            return redirect('question')

        if action == 'answer':
            try:
                user_ans = int(request.POST.get('answer', -1))
            except (ValueError, TypeError):
                user_ans = -1

            correct = q['ans']
            is_correct = user_ans == correct

            if is_correct:
                request.session['score'] = request.session.get('score', 0) + 1
                request.session['feedback'] = {'ok': True}
            else:
                wrong = request.session.get('wrong', [])
                wrong.append({
                    'q': q['q'],
                    'topic': q['topic'],
                    'correct': q['opts'][correct],
                })
                request.session['wrong'] = wrong
                request.session['feedback'] = {
                    'ok': False,
                    'correct_text': q['opts'][correct],
                }

            request.session['current'] = current + 1
            request.session['show_hint'] = False
            return redirect('question')

    show_hint = request.session.pop('show_hint', False)
    opts = list(enumerate(q['opts']))
    letters = ['a', 'b', 'c', 'd']
    progress = int((current / total) * 100) if total > 0 else 0

    return render(request, 'quizbot/question.html', {
        'q': q,
        'opts': opts,
        'letters': letters,
        'current': current + 1,
        'total': total,
        'score': request.session.get('score', 0),
        'name': request.session.get('name', ''),
        'show_hint': show_hint,
        'feedback': feedback,
        'progress': progress,
    })


def results(request):
    score = request.session.get('score', 0)
    wrong = request.session.get('wrong', [])
    qs = request.session.get('questions', [])
    name = request.session.get('name', 'студент')
    mode = request.session.get('mode', '')
    total = len(qs)

    if total == 0:
        return redirect('home')

    pct = int((score / total) * 100)

    if pct == 100:
        grade, color = '5', 'success'
    elif pct >= 80:
        grade, color = '4', 'primary'
    elif pct >= 60:
        grade, color = '3', 'warning'
    else:
        grade, color = '2', 'danger'

    result.objects.create(
        name=name,
        topic=mode,
        score=score,
        total=total,
        percent=pct,
        grade=grade,
    )

    topic_errors = {}
    for item in wrong:
        t = item['topic']
        topic_errors.setdefault(t, []).append(item)

    return render(request, 'quizbot/results.html', {
        'name': name,
        'score': score,
        'total': total,
        'pct': pct,
        'grade': grade,
        'color': color,
        'topic_errors': topic_errors,
    })


def history(request):
    results = result.objects.all()[:50]
    return render(request, 'quizbot/history.html', {'results': results})
