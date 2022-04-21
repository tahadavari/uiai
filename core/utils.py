from datetime import timedelta

def convert_days_to_duration(difference,result = {}):
    if difference.days >= 365:
        years = difference.days // 365
        result['y'] = years
        return convert_days_to_duration(difference-timedelta(days=365*years),result)
    elif 30 <= difference.days < 365:
        months = difference.days // 30
        result['m'] =months
        return convert_days_to_duration(difference-timedelta(days=30*months),result)
    elif 7 <= difference.days < 30:
        weeks = difference.days // 7
        result['w'] =weeks
        return convert_days_to_duration(difference-timedelta(days=7*weeks),result)
    elif 1 <= difference.days < 7:
        days = difference.days 
        result['d'] =days
        return result
    else:
        return result
        
def convert_duration_to_persian(duration):
    years = duration.get('y')
    months = duration.get('m')
    weeks = duration.get('w')
    days = duration.get('d')

    if not duration:
        return "امروز"
    elif years:
        if months:
            return f"{years} سال و {months} ماه پیش"
        else:
            return f"{years} سال پیش"
    elif months:
        if weeks:
            return f"{months} ماه و {weeks} روز پیش"
        else:
            return f"{months} ماه پیش"
    elif weeks:
        if days:
            return f"{weeks} هفته و {days} روز پیش"
        else:
            return f"{weeks} هفته پیش"
    elif days:
        return f"{days} روز پیش"
       