from django import template
from django.contrib.auth.models import Group 

register = template.Library() 

@register.filter(name='has_group') 
def has_group(user, group_name):
    try:
        group =  Group.objects.get(name=group_name) 
    except:
        return False

    return group in user.groups.all() 

@register.filter(name='in_group')
def in_group(user, groups_name):
    # GroupListText = groups_name.split(", ")
    GroupListText = [x.strip() for x in groups_name.split(',')]
    
    for GroupText in GroupListText:
        try:
            group = Group.objects.get(name=groups_name)
        except:
            return False
            
        if group in user.groups.all():
            return True   
    return False