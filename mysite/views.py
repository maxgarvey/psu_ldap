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

import logging
logger = logging.getLogger(__name__)

@login_required
def index(request):
    '''this is the index method, it serves and handles all functionality

        @params:
            request - the django request object.'''

    #check for correct permission
    if not request.user.has_perm('mysite.psu_ldap'):
        logger.info("user=\"{0}\" action=\"attempted app access by user. Improper permissions.\"".format(request.user))
        return render_to_response('invalid.html')

    else:
        #check if form submitted
        if not request.method == 'POST':
            #if asking for recent, then go to this block
            if request.path == '/recent/':
                #logger.info("user=\"{0} action=\"accessed app.\"")
                template = loader.get_template( 'recent.html' )
                context = Context()
                return render_to_response( 'recent.html',
                        { },
                        context_instance=RequestContext(request)  )

            elif request.path == '/query_form/':
                #if form not submitted, ie: no POST, then render the blank form(s)
                #logger.info("rendering blank query form.")
                query_form = LdapQueryForm(initial = {'query_group_name':''})
                template = loader.get_template( 'query.html' )
                context = Context()
                return render_to_response( 'query.html',
                        { 'query_form':query_form },
                        context_instance=RequestContext(request)  )

            else:
                return render_to_response( 'index.html',
                    {}, context_instance=RequestContext(request)  )

        #if it's the modify form that they submitted it will have this field:
        elif (request.path == '/modify/'):
            #logger.info("user: {0}".format(request.user))
            #get the form
            form = LdapModifyForm( request.POST )

            #check if form valid
            if not form.is_valid():
                logger.info("user=\"{0}\" action=\"invalid modify form submission\" form=\"{1}\"".format(request.user, form))
                template = loader.get_template( 'modify_results.html' )
                context = Context()
                return render_to_response( 'modify_results.html',
                        { result:"form not valid..." }, 
                        context_instance=RequestContext(request)  )

            #handle form submission
            else:
                #logger.debug("form: {0}".format(form)) #debug
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
                #logger.info("user:{0}\nlooked up cn: {1}".format(request.user, lookup_cn.replace('(','\(').replace(')','\)'))); #debug
                #initial_record = search(lookup_cn.replace('(','\(').replace(')','\)'), {'basedn':'ou=groups,dc=pdx,dc=edu'}, my_creds)
                #logger.info("user:{0}\nlooked up cn: {1}".format(request.user, lookup_cn)); #debug
                initial_record = search(lookup_cn.replace("(","*").replace(")","*"), {'basedn':'ou=groups,dc=pdx,dc=edu'}, my_creds)

            #logic to figure out what needs to change
            dn_same = False
            cn_same = False
            preferred_cn_same = False
            room_same = False
            phone_same = False
            email_same = False
            uri_same = False

            #logger.debug('initial_record: {0}\ninitial_record == (101, []): {1}'.format(initial_record, (initial_record == (101,[])))) #debug

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
                    #logger.debug("group_name: {0}\ninitial_record[1][0][1]['cn']: {1}".format(group_name, initial_record[1][0][1]['cn']))
 
                    rdn_results = modify_rdn(group_dn, 'cn={0}'.format(group_name), my_creds)
                    #logger.info("cn changed from {0} to {1}".format(initial_record[1][0][1]['cn'], group_name))
                    group_dn = search('cn={0}'.format(group_name.replace("(","*").replace(")","*")), {'basedn':'ou=groups,dc=pdx,dc=edu'}, my_creds)[1][0][0]

                if 'preferredcn' in initial_record[1][0][1].keys():
                    if group_preferredcn in initial_record[1][0][1]['preferredcn']:
                        preferred_cn_same = True
                    else:
                        before_dict['preferredcn'] = initial_record[1][0][1]['preferredcn']
                        after_dict['preferredcn']  = process_input(group_preferredcn)
                elif group_preferredcn is not '':
                    after_dict['preferredcn'] = process_input(group_preferredcn)
                else:
                    preferred_cn_same = True

                if 'roomNumber' in initial_record[1][0][1].keys():
                    if group_room in initial_record[1][0][1]['roomNumber']:
                        room_same = True
                    else:
                        before_dict['roomNumber'] = initial_record[1][0][1]['roomNumber']
                        after_dict['roomNumber']  = process_input(group_room)
                elif group_room is not '':
                    after_dict['roomNumber'] = process_input(group_room)
                else:
                    room_same = True

                if 'telephoneNumber' in initial_record[1][0][1].keys():
                    if group_phone in initial_record[1][0][1]['telephoneNumber']:
                        phone_same = True
                    else:
                        before_dict['telephoneNumber'] = initial_record[1][0][1]['telephoneNumber']
                        after_dict['telephoneNumber']  = process_input(group_phone)
                elif group_phone is not '':
                    after_dict['telephoneNumber'] = process_input(group_phone)
                else:
                    phone_same = True

                if 'mail' in initial_record[1][0][1].keys():
                    if group_email in initial_record[1][0][1]['mail']:
                        email_same = True
                    else:
                        before_dict['mail'] = initial_record[1][0][1]['mail']
                        after_dict['mail']  = process_input(group_email)
                elif group_email is not '':
                    after_dict['mail'] = process_input(group_email)
                else:
                    email_same = True

                try:
                    if group_labeledUri in initial_record[1][0][1]['labeledUri']:
                        uri_same = True
                    else:
                        if (group_labeledUri != 'NOT PERMITTED') and (group_labeledUri != ''):
                            before_dict['labeledUri'] = initial_record[1][0][1]['labeledUri']
                            after_dict['labeledUri']  = process_input(group_labeledUri)
                       
                except Exception, error:
                    uri_same = True

                if after_dict.keys() != []:
                    try:
                        #logger.info("modifying group with dn= '{0}'\nbefore={1}\nafter={2}".format(group_dn, before_dict, after_dict))
                        results = modify(group_dn,
                        #change from:
                        before_dict,
                        #change to:
                        after_dict,
                        my_creds)
                    except Exception, error:
                        logger.info("user=\"{0}\" action=\"Error modifying: {1} to: {2}\" error=\"{3}\"".format(request.user, before_dict, after_dict, error))
                        template = loader.get_template( 'modify_results.html' )
                        context = Context()
                        return render_to_response( 'modify_results.html',
                                { "result":"there was an error during modify for {0}: {1} {2}".format(Exception, error, after_dict.keys())},
                                context_instance=RequestContext(request)  )

                elif not cn_same:
                    logger.info("user=\"{0}\" action=\"changed cn for group: {1} to: {2}\"".format(request.user, group_dn, group_name))
                    template = loader.get_template( 'modify_results.html' )
                    context = Context()
                    return render_to_response( 'modify_results.html',
                            { "result":"Modified group\'s cn." },
                            context_instance=RequestContext(request)  )

                else:
                    logger.info("user=\"{0}\" action=\"attempted to modify with no changes\"".format(request.user))
                    template = loader.get_template( 'modify_results.html' )
                    context = Context()
                    return render_to_response( 'modify_results.html',
                            { "result":"No changes specified." },
                            context_instance=RequestContext(request)  )

                try:
                    if ',' in group_name:
                        group_name = group_name.split(',')[0]
                    #end_results = search('cn={0}'.format(clean_string(group_name)), {'basedn':'ou=groups,dc=pdx,dc=edu'}, my_creds)
                    #logger.info("search_term: {0}".format('cn={0}'.format(group_name.replace("(","*").replace(")","*")))) #debug
                    end_results = search('cn={0}'.format(group_name.replace("(","*").replace(")","*")), {'basedn':'ou=groups,dc=pdx,dc=edu'}, my_creds)
                    group_dn = end_results[1][0][0]
                    result_dict = end_results[1][0][1]
                except Exception, error:
                    logger.info("user=\"{0}\" action=\"error fetching record for cn: {1}\" error=\"{2}\"".format(request.user, group_name, error))
                    template = loader.get_template( 'modify_results.html' )
                    context = Context()
                    return render_to_response( 'modify_results.html',
                            { 'result':'Error fetching record for cn={0}<br/>{1}: {2}'.format(group_name, str(Exception), error) },
                            context_instance=RequestContext(request)  )


                try:
                    if 'labeledUri' in result_dict.keys():
                        logger.info("user=\"{0}\" action=\"modified: {1} to: {2}\"".format(request.user, group_name, result_dict))
                        template = loader.get_template( 'modify_results.html' )
                        context = Context()
                        return render_to_response( 'modify_results.html',
                                { 'result':json.dumps({'dn':group_dn, 'cn':result_dict['cn'], 'preferredcn':result_dict['preferredcn'], 'room':result_dict['roomNumber'], 'phone':result_dict['telephoneNumber'], 'email':result_dict['mail'], 'labeledUri':result_dict['labeledUri'], 'success':True}) },
                                context_instance=RequestContext(request)  )

                    else:
                        logger.info("user=\"{0}\" action=\"modified: {1} to: {2}\"".format(request.user, group_name, result_dict))
                        template = loader.get_template( 'modify_results.html' )
                        context = Context()
                        return render_to_response( 'modify_results.html',
                                { 'result':json.dumps({'dn':group_dn, 'cn':result_dict['cn'], 'preferredcn':result_dict['preferredcn'], 'room':result_dict['roomNumber'], 'phone':result_dict['telephoneNumber'], 'email':result_dict['mail'], 'success':True}) },
                                context_instance=RequestContext(request)  )
 
                except Exception, error:
                    logger.info("user=\"{0}\" action=\"modified: {1} to: {2}\" error=\"\"".format(request.user, group_name, result_dict, error))
                    template = loader.get_template( 'modify_results.html' )
                    context = Context()
                    return render_to_response( 'modify_results.html',
                            { 'result':json.dumps({'dn':group_dn, 'cn':result_dict['cn'], 'preferredcn':result_dict['preferredcn'], 'room':result_dict['roomNumber'], 'phone':result_dict['telephoneNumber'], 'email':result_dict['mail'], 'success':True}) },
                            context_instance=RequestContext(request)  )

            else:
                logger.info("user=\"{0}\" action=\"No existing record for: {1}\"".format(request.user, group_dn))
                template = loader.get_template( 'modify_results.html' )
                context = Context()
                return render_to_response( 'modify_results.html',
                    { 'result':json.dumps({'success':False, 'message':'dn="{0}" is not an existing record'.format(group_dn)}) },
                    context_instance=RequestContext(request)  )

        elif (request.path == '/query/'):

            #logger.info("user: {0}".format(request.user))
            form = LdapQueryForm( request.POST )

            #check if form valid
            if not form.is_valid():
                logger.info("user=\"{0}\" action=\"submitted invalid query form: {1}\"".format(request.user, form))
                template = loader.get_template( 'modify_results.html' )
                context = Context()
                return render_to_response( 'modify_results.html',
                    { "result":"form not valid..." },
                    context_instance=RequestContext(request)  )

            #handle form submission
            else:
                #get form info & log it
                #logger.debug('form.data: {0}'.format(form.data))
                group_name = form.cleaned_data['query_group_name']
                #logger.debug('searched for: {0}'.format(group_name))


                try:
                    #do the search
                    #result = search('cn=*{0}*'.format(clean_string(group_name)),
                    result = search(('cn=*{0}*'.format(group_name.replace("(","*").replace(")","*"))).replace("**","*"),
                        {'basedn':'ou=groups,dc=pdx,dc=edu'}, my_creds)
                    #logger.debug('search result: {0}'.format(result))

                    #no record found
                    if result == (101, []):
                        result = {'success':'false','no_match':'no matching record for this group name.'}

                    #success case, return the results, formatted in browser
                    else:
                        result = {'success':'true',"match":result[1]}

                #handle error
                except Exception, error:
                    #logger.info('search error: {0}\n\t{1}'.format(Exception, error))
                    result = 'search error: {0}\t{1}'.format(Exception, error)
                #logger.debug("search result: {0}".format(result))

                modify_form = LdapModifyForm(initial = {'group_dn':'','modify_group_name':'',
                    'group_preferredcn':'','group_room':'','group_phone':'','group_email':'',
                    'group_labeledUri':''})
                logger.info("user=\"{0}\" action=\"queried for {1}\"".format(request.user, group_name))
                template = loader.get_template( 'query_results.html' )
                context = Context()
                return render_to_response( 'query_results.html',
                        { 'modify_form':modify_form, 'result':json.dumps(result) },
                        context_instance=RequestContext(request)  )


        #catastrophic error case... bad request/url/etc
        else:
            logger.info("user=\"{0}\" action=\"bad request\"".format(request.user))
            return HttpResponse('request fell through:<br/>{0}'.format(request.POST.keys()))
