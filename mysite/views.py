'''psu_ldap/mysite/psu_ldap/views.py'''

from django.shortcuts               import render_to_response 
from django.http                    import HttpResponse, HttpResponseRedirect
from django.template                import RequestContext, Context, loader
from django.contrib.auth.decorators import login_required
from django.utils.html              import escape, strip_tags
from my_forms                       import LdapQueryForm, LdapModifyForm
from support.query_util             import query_process_form
from support.modify_util            import modify_process_form, process_input
from python_ldap_stuff.psu_ldap     import *

#for debug
import logging
__logger__ = logging.getLogger(__name__)

@login_required
def index(request):
    '''this is the index method, it serves and handles all functionality

        @params:
            request - the django request object.'''

    #check for correct permission
    if not request.user.has_perm('mysite.psu_ldap'):
        return render_to_response('invalid.html')

    else:
        #check if form submitted
        if not request.method == 'POST':
            #if form not submitted, ie: no POST, then render the blank form(s)
            query_form = LdapQueryForm(initial = {'query_group_name':''})
            modify_form = LdapModifyForm(initial = {'group_dn':'','modify_group_name':'',
                'group_preferredcn':'','group_room':'','group_phone':'','group_email':'',
                'group_labeledUri':''})
            template = loader.get_template( 'index.html' )
            context = Context()
            return render_to_response( 'index.html',
                    { 'query_form':query_form, 'modify_form':modify_form },
                    context_instance=RequestContext(request)  )

        #if it's the modify form that they submitted it will have this field:
        elif (u'group_phone' in request.POST.keys()):
            #get the form
            form = LdapModifyForm( request.POST )

            #check if form valid
            if not form.is_valid():
                return HttpResponse("form not valid...")
            #handle form submission
            else:
                group_dn, group_name, group_preferredcn, group_room, group_phone, group_email, group_labeledUri = modify_process_form(form)

            #is there a labeled URI for this entry?
            has_labeled_uri = False
            if (group_labeledUri is not 'NOT PERMITTED') and (group_labeledUri is not ''):
                has_labeled_uri = True

            lookup_cn = ''
            dn_split = group_dn.split(',')
            for section in dn_split:
                if section.strip().startswith('cn'):            
                    lookup_cn = section.strip()
            #print 'lookup_cn: {0}'.format(lookup_cn) #debug

            initial_record = (101, [])
            if lookup_cn is not '':
                initial_record = search(lookup_cn, {'basedn':'ou=groups,dc=pdx,dc=edu'}, my_creds)

            #logic to figure out what needs to change
            dn_same = False
            cn_same = False
            preferred_cn_same = False
            room_same = False
            phone_same = False
            email_same = False
            uri_same = False

            #print 'initial_record: {0}\ninitial_record == (101, []): {1}'.format(initial_record, (initial_record == (101,[]))) #debug

            before_dict = {}
            after_dict  = {}

            if initial_record != (101, []):
                if group_dn == initial_record[1][0][0]:
                    dn_same = True

                if group_name in initial_record[1][0][1]['cn']:
                    cn_same = True
                else:
                    before_dict['cn'] = initial_record[1][0][1]['cn']
                    after_dict['cn']  = process_input(group_name)
                    rdn_results = modify_rdn(group_dn, 'cn={0}'.format(group_name), my_creds)
                    group_dn = search('cn={0}'.format(group_name), {'basedn':'ou=groups,dc=pdx,dc=edu'}, my_creds)[1][0][0]

                if group_preferredcn in initial_record[1][0][1]['preferredcn']:
                    preferred_cn_same = True
                else:
                    before_dict['preferredcn'] = initial_record[1][0][1]['preferredcn']
                    after_dict['preferredcn']  = process_input(group_preferredcn)
                    
                if group_room in initial_record[1][0][1]['roomNumber']:
                    room_same = True
                else:
                    before_dict['roomNumber'] = initial_record[1][0][1]['roomNumber']
                    after_dict['roomNumber']  = process_input(group_room)

                if group_phone in initial_record[1][0][1]['telephoneNumber']:
                    phone_same = True
                else:
                    before_dict['telephoneNumber'] = initial_record[1][0][1]['telephoneNumber']
                    after_dict['telephoneNumber']  = process_input(group_phone)

                if group_email in initial_record[1][0][1]['mail']:
                    email_same = True
                else:
                    before_dict['mail'] = initial_record[1][0][1]['mail']
                    after_dict['mail']  = process_input(group_email)
                try:
                    if group_labeledUri in initial_record[1][0][1]['labeledUri']:
                        uri_same = True
                    else:
                        if (group_labeledUri != 'NOT PERMITTED') and (group_labeledUri != ''):
                            before_dict['labeledUri'] = initial_record[1][0][1]['labeledUri']
                            after_dict['labeledUri']  = process_input(group_labeledUri)
                       
                except Exception, error:
                    uri_same = True


                #return HttpResponse('initial_record: {0}<br/>boos: {1}<br/>troubleshoot:<br/>group_name:{2} initial_record["cn"]:{3}<br/>group_room:{4} initial_record["roomNumber"]{5}<br/>group_phone:{6} initial_record["telephoneNumber"]:{7}'.format(initial_record, (dn_same, cn_same, preferred_cn_same, room_same, phone_same, email_same, uri_same), group_name, initial_record[1][0][1]['cn'], group_room, initial_record[1][0][1]['roomNumber'], group_phone, initial_record[1][0][1]['telephoneNumber'])) #debug

                #return HttpResponse('before_dict: {0}<br/>after_dict: {1}'.format(before_dict, after_dict)) #debug
                #print 'group_dn: {0}\nbefore_dict: {1}\nafter_dict: {2}\nmy_creds: {3}'.format(group_dn, before_dict, after_dict, my_creds) #debug
                #return HttpResponse( 'group_dn: {0}<br/>before_dict: {1}<br/>after_dict: {2}<br/>my_creds: {3}'.format(group_dn, before_dict, after_dict, my_creds)) #debug
  
                try:
                    results = modify(group_dn,
                    #change from:
                    before_dict,
                    #change to:
                    after_dict,
                    my_creds)
                except Exception, error:
                    return HttpResponse('there was an error during modify\n\n{0}\n\n{1}'\
                        .format(Exception, error))

                try:
                    end_results = search('cn={0}'.format(group_name), {'basedn':'ou=groups,dc=pdx,dc=edu'}, my_creds)
                    group_dn = end_results[1][0][0]
                    result_dict = end_results[1][0][1]
                except Exception, error:
                    return HttpResponse('error fetching record for cn={0}'.format(group_name))

                try:
                    return HttpResponse('results:<br/>dn: {0}<br/>cn: {1}<br/>preferredcn: {2}<br/>room: {3}<br/>phone: {4}<br/>email: {5}<br/>labeledUri: {6}'.format(group_dn, result_dict['cn'], result_dict['preferredcn'], result_dict['roomNumber'], result_dict['telephoneNumber'], result_dict['mail'], result_dict['labeledUri']))
                except Exception, error:
                    return HttpResponse('results:<br/>dn: {0}<br/>cn: {1}<br/>preferredcn: {2}<br/>room: {3}<br/>phone: {4}<br/>email: {5}'.format(group_dn, result_dict['cn'], result_dict['preferredcn'], result_dict['roomNumber'], result_dict['telephoneNumber'], result_dict['mail']))

            else:
                return HttpResponse('dn="{0}" is not an existing record'.format(group_dn))


        #if its the query form that was submitted
        elif (u'query_group_name' in request.POST.keys()):
            form = LdapQueryForm( request.POST )
            #check if form valid
            if not form.is_valid():
                return HttpResponse("form not valid...")
            #handle form submission
            else:
                #print 'form.data: {0}'.format(form.data)
                group_name = form.cleaned_data['query_group_name']
                #print 'searched for: {0}'.format(group_name) #debug
                try:
                    result = search('cn={0}'.format(group_name),
                        {'basedn':'ou=groups,dc=pdx,dc=edu'}, my_creds)
                    print 'search result: {0}'.format( result ) #debug
                    if result == (101, []):
                        result = 'no matching record for this group name.'
                    else:
                        this_dn = result[1][0][0]
                        result = result[1][0][1]
                        if 'no' in result['psupublish']:
                            result = 'this group doesn\'t show up in the online directory.'
                        elif 'labeledUri' in result.keys():
                            result = \
                                'dn: {0}<br/>cn: {1}<br/>preferredcn: {2}<br/>roomNumber: {3}<br/>telephoneNumber: {4},<br/>mail: {5}<br/>labeledUri: {6}'\
                                .format(this_dn, result['cn'], result['preferredcn'],
                                result['roomNumber'], result['telephoneNumber'], result['mail'],
                                result['labeledUri'])
                        else:
                            result = \
                                'dn: {0}<br/>cn: {1}<br/>preferredcn: {2}<br/>roomNumber: {3}<br/>telephoneNumber: {4},<br/>mail: {5}'\
                                .format(this_dn, result['cn'], result['preferredcn'],
                                result['roomNumber'], result['telephoneNumber'], result['mail'])
                except Exception, error:
                    print 'search error: {0}\n\t{1}'.format(Exception, error)
                    result = ''
                return HttpResponse('results for: {0}<br/>{1}'.format(group_name, result)) #debug

        else:
            return HttpResponse( 'request fell through:<br/>{0}'.format(request.POST.keys()) )
