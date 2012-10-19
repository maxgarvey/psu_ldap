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

import json
import os

#for debug
import logging
__logger__ = logging.getLogger(__name__)

#helper function for processing form input
def clean_string(my_string):
    #get parens right
    my_string = my_string.replace('(','\(').replace(')','\)')
    #get ampersand
    #my_string.replace("%26","&")
    #my_string.replace("&amp","&")
    return my_string

@login_required
def index(request):
    '''this is the index method, it serves and handles all functionality

        @params:
            request - the django request object.'''

    #check for correct permission
    if not request.user.has_perm('mysite.psu_ldap'):
        __logger__.info("attempted app access by user: {0}".format(request.user))
        return render_to_response('invalid.html')

    else:
        #check if form submitted
        if not request.method == 'POST':
            #if asking for recent, then go to this block
            if request.path == '/recent/':
                __logger__.info("serving recent page.")
                recent = 'couldn\'t open the recent file.'

                #we're only showing the last 15 transactions, so this block
                #makes that happen
                more_than_15 = False
                with open('/var/www/psu_ldap/recent.txt','r') as fd:
                    lines = fd.readlines()
                    recent = ''
                    if (len(lines)>15):
                        early_index = 15
                        more_than_15 = True
                    else:
                        early_index = len(lines)
                    early_index = (early_index*(-1))
                    lines = lines[early_index:]
                    lines.reverse()
                    for i in lines:
                        try:
                            recent += i.replace('\n','<br/>')
                        except:
                            break
                if more_than_15:
                    with open('/var/www/psu_ldap/recent.txt','w') as fd:
                        lines.reverse()
                        for i in lines:
                            fd.write(i)

                return HttpResponse("<strong>Most Recent Interactions:</strong><br/><br/>{0}".format(recent))

            else:
                #if form not submitted, ie: no POST, then render the blank form(s)
                __logger__.info("rendering blank forms.")
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
            __logger__.info("user: {0}".format(request.user))
            #get the form
            form = LdapModifyForm( request.POST )

            #check if form valid
            if not form.is_valid():
                __logger__.info("invalid form submission")
                return HttpResponse("form not valid...")

            #handle form submission
            else:
                __logger__.debug("form: {0}".format(form)) #debug
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

            initial_record = (101, [])
            if lookup_cn is not '':
                #lookup_cn = clean_string(lookup_cn)
                __logger__.info("user:{0}\nlooked up cn: {1}".format(request.user, lookup_cn.replace('(','\(').replace(')','\)'))); #debug
                initial_record = search(lookup_cn.replace('(','\(').replace(')','\)'), {'basedn':'ou=groups,dc=pdx,dc=edu'}, my_creds)

            #logic to figure out what needs to change
            dn_same = False
            cn_same = False
            preferred_cn_same = False
            room_same = False
            phone_same = False
            email_same = False
            uri_same = False

            __logger__.debug('initial_record: {0}\ninitial_record == (101, []): {1}'.format(initial_record, (initial_record == (101,[])))) #debug

            before_dict = {}
            after_dict  = {}

            if initial_record != (101, []):
                if group_dn == initial_record[1][0][0]:
                    dn_same = True

                if ',' in group_name:
                    group_cn_s = group_name.split(",")
                    for group_cn in group_cn_s:
                        if group_cn in initial_record[1][0][1]['cn']:
                            cn_same = True

                if group_name in initial_record[1][0][1]['cn']:
                    cn_same = True

                if not cn_same:
                    __logger__.debug("group_name: {0}\ninitial_record[1][0][1]['cn']: {1}".format(group_name, initial_record[1][0][1]['cn']))
                    rdn_results = modify_rdn(group_dn, 'cn={0}'.format(group_name), my_creds)
                    __logger__.info("cn changed from {0} to {1}".format(initial_record[1][0][1]['cn'], group_name))
                    group_dn = search('cn={0}'.format(clean_string(group_name)), {'basedn':'ou=groups,dc=pdx,dc=edu'}, my_creds)[1][0][0]

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

                try:
                    __logger__.info("modifying group with dn= '{0}'\nbefore={1}\nafter={2}".format(group_dn, before_dict, after_dict))
                    results = modify(group_dn,
                    #change from:
                    before_dict,
                    #change to:
                    after_dict,
                    my_creds)
                except Exception, error:
                    with open('/var/www/psu_ldap/recent.txt', 'a') as fd:
                        fd.write('there was an error during modify for {0}: {1}\n'\
                        .format(Exception, error))
                    return HttpResponse('there was an error during modify\n\n{0}\n\n{1}'\
                        .format(Exception, error))

                try:
                    if ',' in group_name:
                        group_name = group_name.split(',')[0]
                    end_results = search('cn={0}'.format(clean_string(group_name)), {'basedn':'ou=groups,dc=pdx,dc=edu'}, my_creds)
                    group_dn = end_results[1][0][0]
                    result_dict = end_results[1][0][1]
                except Exception, error:
                    with open('/var/www/psu_ldap/recent.txt', 'a') as fd:
                        fd.write('error fetching record for cn={0}\n'.format(group_name))
                    return HttpResponse('error fetching record for cn={0}<br/>{1}: {2}'.format(group_name, str(Exception), error))

                try:
                    with open('/var/www/psu_ldap/recent.txt', 'a') as fd:
                        fd.write("modified: {0} to have: {1}\n".format(group_dn, after_dict))
                    if 'labeledUri' in result_dict.keys():
                        return HttpResponse('results:<br/>dn: {0}<br/>cn: {1}<br/>preferredcn: {2}<br/>room: {3}<br/>phone: {4}<br/>email: {5}<br/>labeledUri: {6}'.format(group_dn, result_dict['cn'], result_dict['preferredcn'], result_dict['roomNumber'], result_dict['telephoneNumber'], result_dict['mail'], result_dict['labeledUri']))
                    else:
                        return HttpResponse('results:<br/>dn: {0}<br/>cn: {1}<br/>preferredcn: {2}<br/>room: {3}<br/>phone: {4}<br/>email: {5}'.format(group_dn, result_dict['cn'], result_dict['preferredcn'], result_dict['roomNumber'], result_dict['telephoneNumber'], result_dict['mail'])) 
                except Exception, error:
                    with open('/var/www/psu_ldap/recent.txt', 'a') as fd:
                        fd.write("Attempted to modify: {0} to have: {1}, but there was a {2}: {3}\n".format(group_dn, after_dict, Exception, error))
                    return HttpResponse('results:<br/>dn: {0}<br/>cn: {1}<br/>preferredcn: {2}<br/>room: {3}<br/>phone: {4}<br/>email: {5}'.format(group_dn, result_dict['cn'], result_dict['preferredcn'], result_dict['roomNumber'], result_dict['telephoneNumber'], result_dict['mail']))
            else:
                with open('/var/www/psu_ldap/recent.txt', 'a') as fd:
                    fd.write("FAILED: attempted to modify: {0}. No matching record\n".format(group_dn, after_dict))
                return HttpResponse('dn="{0}" is not an existing record'.format(group_dn))


        #if its the query form that was submitted
        elif (u'query_group_name' in request.POST.keys()):
            __logger__.info("user: {0}".format(request.user))
            form = LdapQueryForm( request.POST )

            #check if form valid
            if not form.is_valid():
                return HttpResponse("form not valid...")
            #handle form submission

            else:
                #get form info & log it
                __logger__.debug('form.data: {0}'.format(form.data))
                group_name = form.cleaned_data['query_group_name']
                __logger__.debug('searched for: {0}'.format(group_name))

                try:
                    #do the search
                    result = search('cn=*{0}*'.format(clean_string(group_name)),
                        {'basedn':'ou=groups,dc=pdx,dc=edu'}, my_creds)
                    __logger__.debug('search result: {0}'.format(result))

                    #no record found
                    if result == (101, []):
                        result = {'success':'false','no_match':'no matching record for this group name.'}

                    #success case, return the results, formatted in browser
                    else:
                        result = {'success':'true',"match":result[1]}

                    #add a line to the recent transactions file
                    with open('/var/www/psu_ldap/recent.txt','a') as fd:
                        if (result == {'no_match':'no matching record for this group name.'}): 
                            fd.write('Queried for: cn={0}<br/>results: {1}\n'.format(group_name, result))
                        else:
                            fd.write('Queried for: cn=*{0}*\n'.format(group_name))

                #handle error
                except Exception, error:
                    __logger__.info('search error: {0}\n\t{1}'.format(Exception, error))
                    result = 'search error: {0}\t{1}'.format(Exception, error)
                    with open('/var/www/psu_ldap/recent.txt', 'a') as fd:
                        fd.write(result + '\n')
                __logger__.debug("search result: {0}".format(result))
                return HttpResponse(json.dumps(result), mimetype="application/json")

        #catastrophic error case... bad request/url/etc
        else:
            __logger__.info("user: {0}".format(request.user))
            with open('/var/www/psu_ldap/recent.txt', 'a') as fd:
                fd.write('request fell through:\n\t'.format(request.POST))
            return HttpResponse('request fell through:<br/>{0}'.format(request.POST.keys()))
