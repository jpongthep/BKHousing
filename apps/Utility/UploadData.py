from django.core.exceptions import ValidationError

from apps.Configurations.models import YearRound

def UploadFolderName(instance, filename):
    year_round = YearRound.objects.filter(CurrentStep__in = ["RS","UP","PP"])[0]
    year_round_text = f'{year_round.Year}-{year_round.Round}'
    
    return '/'.join([year_round_text,filename])
    # return '/'.join([year_round, instance.Unit.ShortName, instance.Requester.username, filename])

def UploadFolderCommandFile(instance, filename):

    year_round = YearRound.objects.filter(CurrentStep__in = ["RS","UP","PP"])[0]
    year_round_text = f'{year_round.Year}-{year_round.Round}'
    
    return '/'.join([year_round_text,"command", filename])  


def only_pdf(value):    
    if not value.name.lower().endswith('.pdf'):
        raise ValidationError(u'Error message', code='only pdf file allowed')