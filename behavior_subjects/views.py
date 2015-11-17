from django.shortcuts import render, redirect
# from django.core.urlresolvers import reverse
from django.core.exceptions import ObjectDoesNotExist
from .models import Mouse, Session, Trial, TrialTable
from django.utils import timezone
# from django.http import HttpResponse, Http404, HttpResponseRedirect
from .forms import MouseForm
from .utils import parse_h5path

from bokeh.plotting import figure
from bokeh.resources import CDN
from bokeh.embed import components
from bokeh.models import Range1d

import numpy as np

def index(request, msg=None):
    mice_list = Mouse.objects.order_by('-date_added')
    context = {'mice_list': mice_list,
               'error_msg': msg}

    return render(request, 'behavior_subjects/index.html', context)


def mouse(request, mouse_number):
    mouse = Mouse.objects.get(mouse_number=mouse_number)
    sessions = mouse.session_set.order_by('-run_dtg')
    y = []
    x = []
    for s in sessions:
        x.append(s.performance)
        y.append(s.run_dtg)

    for i in range(len(x)):
        if np.isnan(float(x[i])):
            x[i] = 0.

    plot = figure(plot_width=500, plot_height=300, toolbar_location=None,
                  x_axis_type='datetime', x_axis_label='Date', y_axis_label='Performance',
                  tools="xpan, xwheel_zoom, reset,resize")
    plot.y_range = Range1d(0., 1.)
    plot.line(y, x)
    plot.circle(y, x)
    script, div = components(plot, CDN)

    return render(request, 'behavior_subjects/mouse.html', {'mouse': mouse,
                                                    'sessions_list': sessions,
                                                    'script': script,
                                                    'div': div})


def session(request, mouse_number, session_num):

    mouse = Mouse.objects.get(mouse_number=mouse_number)
    session = mouse.session_set.get(id=session_num)
    trials = session.trial_set.order_by('trial_num')
    corrects = []
    for t in trials:
        if t.valid:
            corrects.append(t.correct)
    corrects = np.array(corrects)
    window_size = 10
    y = np.convolve(corrects, [1/window_size]*window_size, mode='valid')
    x = np.linspace(1, len(y))
    i = np.where(np.isnan(y))[0]
    y[i] = 0.
    p = figure(plot_width=500, plot_height=300, toolbar_location=None,
               x_axis_label='trial', y_axis_label='Performance',
               tools="")
    p.circle(x, y)
    p.y_range = Range1d(0, 1)
    p.line(x, y)
    script, div = components(p, CDN)

    table = TrialTable(trials)

    context = {'mouse_num': mouse_number,
               'session': session,
               'script': script,
               'div': div,
               'trial_table': table}

    return render(request, 'behavior_subjects/session.html', context)


def add_session(request):
    if request.FILES:
        files = request.FILES.getlist('files')
        for file in files:
            fn = file.name
            mouse_num, sess_num, dtg = parse_h5path(fn)
            try:
                mouse = Mouse.objects.get(mouse_number=mouse_num)
            except ObjectDoesNotExist:
                err = 'Mouse {0} does not exist in database. Please add mouse first!'.format(mouse_num)
                return index(request, msg=err)  # short circuit if mouse doesn't exist before adding anything to db.

        for file in files:
            fn = file.name
            mouse_num, sess_num, dtg = parse_h5path(fn)
            mouse = Mouse.objects.get(mouse_number=mouse_num)
            print (Session.objects.filter(run_dtg=dtg))
            if not Session.objects.filter(run_dtg=dtg):
                new_sess = Session(mouse=mouse,
                                   session_num=sess_num,
                                   run_dtg=dtg,
                                   added_dtg=timezone.now(),
                                   file=file)

                new_sess.save()
                try:
                    new_sess.process()
                except Exception as e:
                    new_sess.delete()
                    raise e
                msg = 'Sessions successfully added!'
            else:
                print('Session exists.')
                continue
    else:
        msg = 'Please select one or more session files!'
    return index(request, msg=msg)


def mouse_adder(request):
    if request.method == 'POST':
        form = MouseForm(request.POST)
        if form.is_valid():
            mouse = form.save()
            # return index(request, 'Mouse added.')
            success_msg = 'Mouse {0} added.'.format(form.cleaned_data['mouse_number'])
            return redirect('behavior_subjects:index')
        else:
            pass
    else:
        form = MouseForm()
        return render(request, "behavior_subjects/mouse_adder.html", {'form': form})


def edit_mouse(request, mouse_number):
    # todo: mouse editor.
    mouse = Mouse.objects.get(mouse_number=mouse_number)
    if request.method == 'POST':
        form = MouseForm(request.POST, instance=mouse)
        if form.is_valid():
            form.save()
        return redirect('behavior_subjects:mouse', form.cleaned_data['mouse_number'])

    form = MouseForm(instance=mouse)

    return render(request, "behavior_subjects/mouse_editor.html", {'mouse_number': mouse_number,
                                                           'form': form})


def session_graph(request, mouse_number, session_number):
    return None