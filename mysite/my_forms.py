from django import forms

#the group query form
class LdapQueryForm(forms.Form):
    query_group_name       = forms.CharField(max_length=100, required=True)  #group name

#the group modify form
class LdapModifyForm(forms.Form):
    group_dn          = forms.CharField(max_length=100, required=True)  #group dn
    modify_group_name = forms.CharField(max_length=100, required=True)  #group name
    group_preferredcn = forms.CharField(max_length=100, required=True)  #group preferredcn
    group_room        = forms.CharField(max_length=100, required=True)  #group room
    group_phone       = forms.CharField(max_length=100, required=True)  #group phone
    group_email       = forms.CharField(max_length=100, required=True)  #group email
    group_labeledUri  = forms.CharField(max_length=100, required=False) #group URI
