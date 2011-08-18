import simplejson 

from django.contrib import messages

class AjaxMessaging(object):
    def process_response(self, request, response):
        if request.is_ajax():
            if response['Content-Type'] in ["application/javascript", "application/json"]:
                try:
                    content = simplejson.loads(response.content)
                except ValueError:
                    return response

                django_messages = []
                for message in messages.get_messages(request):
                    print "appending msg to django_messages"
                    django_messages.append({
                        "level": message.level,
                        "message": message.message,
                        "extra_tags": message.tags,
                    })
                # import pdb; pdb.set_trace()

                print "request should be empty of messages now"
                content['django_messages'] = django_messages  
                print "len of django_messages is %i" % len(content['django_messages'])              

                response.content = simplejson.dumps(content)
        return response