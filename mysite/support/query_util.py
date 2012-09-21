def query_process_form( form ):
    '''this method gets the different fields from the calendar form'''
    #print 'form.cleaned_data: ' + str(form.cleaned_data)
    return form.cleaned_data['query_group_name']
