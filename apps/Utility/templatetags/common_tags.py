import os 

from django import template
from django.contrib.auth.models import Group 

register = template.Library() 

@register.filter(name='has_group') 
def has_group(user, group_name):
    try:
        group =  Group.objects.get(name=group_name)
    except:
        return False
    
    # print("groups :  ", group)
    # print("user.groups.all :  ",user.groups.all())
    # print(group in user.groups.all())

    return group in user.groups.all() 

@register.filter(name='in_group')
def in_group(user, groups_name):
    GroupListText = groups_name.split(", ")
    GroupListText = [x.strip() for x in groups_name.split(',')]
    # print("GroupTextList = ",GroupListText)
    for GroupText in GroupListText:
        try:
            group = Group.objects.get(name=GroupText)
        except:
            # print("here")
            return False
            
        if group in user.groups.all():
            return True   
    return False

@register.filter(name='file_ext')
def file_ext(filename):
    '''Returns the given key from a dictionary.'''
    return filename[-3:].lower()

@register.filter(name='enc')
def enc(filename):

    '''Returns the given key from a dictionary.'''
    return "enc" in str(filename)

@register.filter(name='file_name')
def file_name(filename):
    '''Returns the given key from a dictionary.'''
    name = os.path.basename(str(filename))
    return name

@register.filter(name='dict_key')
def dict_key(d, k):
    '''Returns the given key from a dictionary.'''
    return d[k]