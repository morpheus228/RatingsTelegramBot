import datetime


def check_age(birthday, low_board=0, high_board=300):
    if birthday.count('.') == 2:
        birthday = datetime.datetime.strptime(birthday, "%d.%m.%Y")
        now = datetime.datetime.now()
        years = int((now - birthday).total_seconds() / 31536000)
        return low_board <= years <= high_board
    else:
        return True

print(check_age('10.8.2004'))