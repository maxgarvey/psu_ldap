def modify_process_form( form ):
    '''this method gets the different fields from the calendar form'''
    #print "form_submit:\n\n{0}\n".format(form.cleaned_data) #debug
    #print 'form_group_name: {0}'.format(form.cleaned_data['modify_group_name']) #debug
    return form.data['group_dn'], form.cleaned_data['modify_group_name'], \
        form.cleaned_data['group_preferredcn'], form.cleaned_data['group_room'], \
        form.cleaned_data['group_phone'], form.cleaned_data['group_email'], \
        form.cleaned_data['group_labeledUri']

def process_input( string ):
   string_list = string.encode('ASCII').replace("'",'').split(',')
   modified_string_list = []
   for i in string_list:
       modified_string_list.append(i.strip())
   return modified_string_list
