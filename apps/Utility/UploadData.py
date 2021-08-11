from apps.Configurations.models import YearRound

def UploadFolderName(instance, filename):
    year_round = YearRound.objects.filter(CurrentStep__in = [1,2,3])[0]
    year_round_text = f'{year_round.Year}-{year_round.Round}'
    
    return '/'.join([year_round_text,filename])
    # return '/'.join([year_round, instance.Unit.ShortName, instance.Requester.username, filename])
