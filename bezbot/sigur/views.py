from django.shortcuts import render
import json
import requests
from tgbot.models import Students
from  django.http import HttpResponse, JsonResponse


def event_log(request):
    data = json.loads(request.body)
    login = data['l']
    time_zone = data['z']
    data = data['d']
    last_index = data[0]["i"]
    for i in data:
        last_index = i['i']
        if i["type"] == 1: # проверка прохода(1-разрешен, 2-запрещен)
            vector = i["d"] # направление (1=выход. 2=вход.)
            card = i["keyHex"]
            student = Students.objects.get(card=card)

            if vector == 1:
                student.presence = False
            elif vector == 2:
                student.presence = True
            print(student.presence)
            student.save()
    return JsonResponse({"i": last_index})
    # a = {
    #     "l": "login",
    #     "z": -14400,
    #     "d": [
    #         {
    #             "i": 1000,
    #             "type": 1,
    #             "reason": 6,
    #             "ap": 5,
    #             "e": "123",
    #             "t": 1356253200,
    #             "d": 2,
    #             "keyHex": "112233"
    #         }
    #     ]
    # }
    # Где
    # l логин доступа к сервису(строка)
    # z смещение временной зоны(целое число)
    # d массив передаваемых проходов, каждый элемент которого включает поля:
    # i номер прохода(целое число)
    # type код типа события(целое число, см.таблицу в конце раздела)
    # reason причина события(целое число)
    # ap идентификатор точки доступа(целое число)
    # e идентификатор сотрудника(строка)
    # t время прохода(целое число)
    # d код направления(целое число)
    # keyHex использованный номер пропуска в шестнадцатеричном формате
