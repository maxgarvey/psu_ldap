'''/psu_gcal/mysite/test.py'''

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

#@with_setup(initialize_cals, cleanup_cals)
class query_test:
    '''test class for calendar operations'''
    def __init__(self):
        '''init the client obj and the new cal's name to null'''
        self.creds  = None
        self.client = None
        self.before_dict = {'preferredcn':'AAUP','roomNumber':'232 SMC','telephoneNumber':'5-4414','mail':'aaup@psuaaup.net','labeledUri':'www.email.net'}
        self.after_dict = {'preferredcn':'AAUP','roomNumber':'232 SMCee','telephoneNumber':'5-44141','mail':'aaup@psuaaup.com','labeledUri':'www.email.com'}
 
        self.before_dn = 'cn=aaup,ou=groups,dc=pdx,dc=edu'
        self.after_dn = 'cn=aaup_,ou=groups,dc=pdx,dc=edu'
        self.group_name = 'aaup'

    def setUp(self):
        '''set the client obj to a new client, and set the cal name to the name we\'re using'''
        self.creds = credentials()
        self.creds.edit_creds(conf['username'],conf['password'],conf['server'])
        self.client = connect(self.creds)
        
    def tearDown(self):
        '''delete the newly created calendar object as well as the client we were using'''
        try:
            modify_rdn(self.after_dn, self.before_dn)
        except Exception, error:
            print '{0}\n\t{1}'.format(Exception, error)
        try:
            modify_rdn(self.creds, 'cn=_aaup,ou=groups,dc=pdx,dc=edu','cn=aaup', True)
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

    def test_query_existing(self):
        '''this function tests running psu_ldap.search on a known existing 
        ldap group'''
        results = search('cn=aaup', {'basedn':'ou=groups,dc=pdx,dc=edu'}, self.creds)
        #print "results: {0}".format(results) #debug
        assert (results == (101, [('cn=AAUP, ou=groups, dc=pdx, dc=edu', {'telephoneNumber': ['5-4414'], 'cn': ['AAUP'], 'psupublish': ['yes'], 'facsimileTelephoneNumber': ['(503) 725-8124'], 'ou': ['DEPT', 'groups'], 'mailLocalAddress': ['aaup2@pdx.edu'], 'preferredcn': ['AAUP'], 'roomNumber': ['232 SMC'], 'objectClass': ['top', 'organizationalUnit', 'psuOrganizationalUnit', 'inetLocalMailRecipient', 'mailGroup', 'labeledURIObject'], 'mgrpRFC822MailMember': ['aaup@psuaaup.net'], 'mail': ['aaup@psuaaup.net'], 'postalAddress': ['Portland State University PO Box 751 Portland, OR 97207-0751'], 'labeledUri': ['www.email.net'], 'psumailcode': ['AAUP']})]))

    def test_query_phony(self):
        '''this function tests running psu_ldap.search on a phony group'''
        results = search('cn=aaaaaaaa', {'basedn':'ou=groups,dc=pdx,dc=edu'}, self.creds)
        #print "results: {0}".format(results) #debug
        assert (results == (101, []))

    def test_modify(self):
        '''this function tests running psu_ldap.modify on an existing
        group.'''
        results = modify('cn=aaup,ou=groups,dc=pdx,dc=edu', self.before_dict,
            self.after_dict, self.creds)
        print 'results: {0}'.format(results)
        _results = modify('cn=aaup,ou=groups,dc=pdx,dc=edu', self.after_dict,
            self.before_dict, self.creds)
        assert (results == (101, [('cn=AAUP, ou=groups, dc=pdx, dc=edu', {'telephoneNumber': ['5-44141'], 'cn': ['AAUP'], 'psupublish': ['yes'], 'facsimileTelephoneNumber': ['(503) 725-8124'], 'ou': ['DEPT', 'groups'], 'mailLocalAddress': ['aaup2@pdx.edu'], 'preferredcn': ['AAUPack'], 'roomNumber': ['232 SMCee'], 'objectClass': ['top', 'organizationalUnit', 'psuOrganizationalUnit', 'inetLocalMailRecipient', 'mailGroup', 'labeledURIObject'], 'mgrpRFC822MailMember': ['aaup@psuaaup.net'], 'mail': ['aaup@psuaaup.com'], 'postalAddress': ['Portland State University PO Box 751 Portland, OR 97207-0751'], 'labeledUri': ['www.email.com'], 'psumailcode': ['AAUP']})]))
