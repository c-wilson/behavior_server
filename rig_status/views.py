from django.http import HttpResponse
from django.shortcuts import render
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
import traceback

from .models import Rig


def index(request):
    rig_list = Rig.objects.order_by('name')

    context = {'rigs': rig_list}


    return render(request, 'rig_status/index.html', context)


@csrf_exempt
def update_status(request):
    if request.method == 'POST':
        post = request.POST
        try:
            rigname = post['rig']
            rig = Rig.objects.get_or_create(name=rigname)[0]
            rig.status = post['status']
            rig.non_responses = int(post['non_resp'])
            rig.correct = int(post['corr_resp'])
            rig.n_trials = int(post['n_trials'])
            rig.last_heartbeat = timezone.now()
            rig.save()
        except KeyError as e:
            print(post)
        except Exception as e:
            traceback.print_exc()
            return HttpResponse(status=400)

        return HttpResponse('Success', status=202)
    else:
        return HttpResponse('This URL reached in error. This URL only accepts rig status posts.', status=400)


