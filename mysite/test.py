'''/psu_gcal/mysite/test.py'''

import exceptions
import sys
sys.path.append('/var/www/psu_ldap/')
sys.path.append('/var/www/psu_ldap/mysite/')

from python_ldap_stuff.psu_ldap import *
from python_ldap_stuff.conf import conf
from support.query_util import *
from support.modify_util import *
from random import randint
from hashlib import md5
from time import sleep
from nose.tools import with_setup
from my_forms import LdapQueryForm, LdapModifyForm
from django.http import QueryDict

#@with_setup(initialize_cals, cleanup_cals)
class query_test:
    '''test class for calendar operations'''
    def __init__(self):
        '''init the client obj and the new cal's name to null'''
        self.creds  = None
        self.client = None
        self.before_dict = {'preferredcn':'AAUP','roomNumber':'232 SMC','telephoneNumber':'5-4414','mail':'aaup@psuaaup.net'} #,'labeledUri':'www.email.net'}
        self.after_dict = {'preferredcn':'AAUPa','roomNumber':'232 SMCee','telephoneNumber':'5-44141','mail':'aaup@psuaaup.com'} #,'labeledUri':'www.email.com'}
 
        self.before_dn = 'cn=aaup,ou=groups,dc=pdx,dc=edu'
        self.after_dn = 'cn=_aaup,ou=groups,dc=pdx,dc=edu'
        self.before_group_name = 'AAUP'
        self.after_group_name = '_aaup'

    def setUp(self):
        '''set the client obj to a new client, and set the cal name to the name we\'re using'''
        self.creds = credentials()
        self.creds.edit_creds(conf['username'],conf['password'],conf['server'])
        self.client = connect(self.creds)
        
    def tearDown(self):
        '''delete the newly created calendar object as well as the client we were using'''
        try:
            modify_rdn(self.after_dn, 'cn={0}'.format(self.before_group_name), self.creds, True)
        except Exception, error:
            print '{0}\n\t{1}'.format(Exception, error)
        try:
            modify('cn=aaup,ou=groups,dc=pdx,dc=edu','','', self.creds)
        except Exception, error:
            print '{0}\n\t{1}'.format(Exception, error)
        try:
            disconnect(self.creds, True)
        except Exception, error:
            print '{0}\n\t{1}'.format(Exception, error)

    @with_setup(setUp, tearDown)
    def test_query_existing(self):
        '''this function tests running psu_ldap.search on a known existing 
        ldap group'''
        results = search('cn=aaup', {'basedn':'ou=groups,dc=pdx,dc=edu'}, self.creds)
        #print "results: {0}".format(results) #debug
        assert ((results[0] == 101) and (results[1][0][0] == 'cn=AAUP, ou=groups, dc=pdx, dc=edu')) #(101, [('cn=AAUP, ou=groups, dc=pdx, dc=edu', {'telephoneNumber': ['5-4414'], 'cn': ['AAUP'], 'psupublish': ['yes'], 'facsimileTelephoneNumber': ['(503) 725-8124'], 'ou': ['DEPT', 'groups'], 'mailLocalAddress': ['aaup2@pdx.edu'], 'preferredcn': ['AAUP'], 'roomNumber': ['232 SMC'], 'objectClass': ['top', 'organizationalUnit', 'psuOrganizationalUnit', 'inetLocalMailRecipient', 'mailGroup', 'labeledURIObject'], 'mgrpRFC822MailMember': ['aaup@psuaaup.net'], 'mail': ['aaup@psuaaup.net'], 'postalAddress': ['Portland State University PO Box 751 Portland, OR 97207-0751'], 'labeledUri': ['www.email.net'], 'psumailcode': ['AAUP']})]))

    @with_setup(setUp, tearDown)
    def test_query_phony(self):
        '''this function tests running psu_ldap.search on a phony group'''
        results = search('cn=aaaaaaaa', {'basedn':'ou=groups,dc=pdx,dc=edu'}, self.creds)
        #print "results: {0}".format(results) #debug
        assert (results == (101, []))

    @with_setup(setUp, tearDown)
    def test_modify(self):
        '''this function tests running psu_ldap.modify on an existing
        group.'''
        modify('cn=aaup,ou=groups,dc=pdx,dc=edu', self.before_dict,
           self.after_dict, self.creds)
        results=search('cn=aaup', {'basedn':'ou=groups,dc=pdx,dc=edu'}, self.creds)
        #print 'results: {0}'.format(results) #debug
        modify('cn=aaup,ou=groups,dc=pdx,dc=edu', self.after_dict,
           self.before_dict, self.creds)
        assert ((results[0] == 101) and (results[1][0][0] == 'cn=AAUP, ou=groups, dc=pdx, dc=edu') and (type(results[1][0][1] == dict))) 

    @with_setup(setUp, tearDown)
    def test_modify_phony(self):
        '''this function tests running psu_ldap.modify on an existing
        group.'''
        try:
            modify('cn=aaupaa,ou=groups,dc=pdx,dc=edu', self.before_dict,
               self.after_dict, self.creds)
        except Exception, error:
            my_exception = Exception
            my_error = error
        results=search('cn=aaupaa', {'basedn':'ou=groups,dc=pdx,dc=edu'}, self.creds)
        assert(my_exception == exceptions.Exception)
        assert(my_error.args == ldap.NO_SUCH_OBJECT({'info':'','matched':'ou=groups,dc=pdx,dc=edu','desc':'No such object'}).args)
        assert(results == (101,[]))

    @with_setup(setUp, tearDown)
    def test_modify_insufficient(self):
        '''this function tests behavior from running psu_ldap.modify on an
            an object that the permissions shouldn't be able to modify'''
        try:
            modify('uid=magarvey,ou=people,dc=pdx,dc=edu', {'preferredcn':'Maxwell Garvey'},
               {'preferredcn':'Maxwel Garvey'}, self.creds)
        except Exception, error:
            my_exception = Exception
            my_error = error
            print 'my_exception: {0}'.format(my_exception) #debug
            print 'my_error: {0}'.format(my_error) #debug
        assert(my_exception == exceptions.Exception)
        assert(my_error.args == ldap.INSUFFICIENT_ACCESS({'info': "Insufficient 'write' privilege to the 'preferredcn' attribute of entry 'uid=magarvey,ou=people,dc=pdx,dc=edu'.\n", 'desc': 'Insufficient access'}).args)

    @with_setup(setUp, tearDown)
    def test_modify_rdn(self):
        '''this function tests the psu_ldap.modify_rdn method on
            an existing group.'''
        modify_rdn(self.before_dn, 'cn={0}'.format(self.after_group_name), self.creds, True)
        results = search('cn={0}'.format(self.after_group_name),
            {'basedn':'ou=groups,dc=pdx,dc=edu'}, self.creds)
        modify_rdn(self.after_dn, 'cn={0}'.format(self.before_group_name), self.creds, True)
        assert ((results[0] == 101) and (results[1][0][0] == 'cn=_aaup, ou=groups, dc=pdx, dc=edu')) #(101, [('cn=_aaup, ou=groups, dc=pdx, dc=edu', {'telephoneNumber': ['5-4414'], 'cn': ['_aaup'], 'psupublish': ['yes'], 'facsimileTelephoneNumber': ['(503) 725-8124'], 'ou': ['DEPT', 'groups'], 'mailLocalAddress': ['aaup2@pdx.edu'], 'preferredcn': ['AAUP'], 'roomNumber': ['232 SMC'], 'objectClass': ['top', 'organizationalUnit', 'psuOrganizationalUnit', 'inetLocalMailRecipient', 'mailGroup', 'labeledURIObject'], 'mgrpRFC822MailMember': ['aaup@psuaaup.net'], 'mail': ['aaup@psuaaup.net'], 'postalAddress': ['Portland State University PO Box 751 Portland, OR 97207-0751'], 'labeledUri': ['www.email.net'], 'psumailcode': ['AAUP']})]))

    @with_setup(setUp, tearDown)
    def test_modify_rdn_phony(self):
        '''this function tst s the psu_ldap.modify_rdn method on
            a non-existant group.'''
        try:
            modify_rdn(self.before_dn.replace('aaup','aaupaaa'), 'cn={0}'.format(self.after_group_name), self.creds, True)
        except Exception, error:
            my_exception_1 = Exception
            my_error_1 = error
        results = search('cn={0}'.format(self.after_group_name),
            {'basedn':'ou=groups,dc=pdx,dc=edu'}, self.creds)
        assert (my_exception_1 == exceptions.Exception)
        assert (my_error_1.args == ldap.NO_SUCH_OBJECT({'info':'','matched':'ou=groups,dc=pdx,dc=edu','desc':'No such object'}).args)
        assert (results == (101, []))

    #@with_setup(setUp, tearDown)
    #def test_modify_rdn_insufficient(self):
    #    '''this function tests behavior from running psu_ldap.modify on an
    #        an object that the permissions shouldn't be able to modify'''
    #    try:
    #        modify_rdn('uid=magarveyy,ou=people,dc=pdx,dc=edu',
    #            'uid=magarvey', self.creds, True)
    #    except Exception, error:
    #        my_exception = Exception
    #        my_error = error
    #        print 'my_exception: {0}'.format(my_exception) #debug
    #        print 'my_error: {0}'.format(my_error) #debug
    #    assert(my_exception == exceptions.Exception)
    #    assert(my_error.args == ldap.INSUFFICIENT_ACCESS(
    #         {'info': "Insufficient 'write' privilege to the 'preferredcn' attribute of entry 'uid=magarvey,ou=people,dc=pdx,dc=edu'.\n", 'desc': 'Insufficient access'}).args)

    def test_process_query_form(self):
        '''this tests the form objects and the process query form method'''

        my_post_string = 'csrftoken=blablabla&query_group_name=aaup'

        my_query_dict  = QueryDict(my_post_string)
        my_query_form  = LdapQueryForm(my_query_dict)
        my_query_valid = my_query_form.is_valid()
        my_query_data  = my_query_form.cleaned_data

        assert (my_query_valid)
        assert (my_query_data == {'query_group_name': u'aaup'})

    def test_process_modify_form(self):
        '''this tests the form objects and the process modify form method'''

        my_post_string = 'csrf=blablabla&group_dn=cn=aaup,ou=groups,dc=pdx,dc=edu&modify_group_name=aaup&group_preferredcn=AAUP&group_room=232 SMC&group_phone=5-4414&group_email=aaup@psuaaup.net&group_labeledUri=www.email.net'

        my_modify_dict  = QueryDict(my_post_string)
        my_modify_form  = LdapModifyForm(my_modify_dict)
        my_modify_valid = my_modify_form.is_valid()
        my_modify_data  = my_modify_form.cleaned_data

        print 'my_modify_data: {0}'.format(my_modify_data) #debug

        assert (my_modify_valid)
        assert (my_modify_data == {'group_dn':'cn=aaup,ou=groups,dc=pdx,dc=edu','modify_group_name':'aaup','group_preferredcn':'AAUP','group_room':'232 SMC','group_phone':'5-4414','group_email':'aaup@psuaaup.net', 'group_labeledUri':'www.email.net'})
