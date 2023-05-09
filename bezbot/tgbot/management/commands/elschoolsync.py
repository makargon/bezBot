import requests
import pandas as pd
from django.conf import settings
from tgbot.models import Students
from django.contrib.auth.models import Group



class Elschool:
    def __init__(self, login, password):
        # "Авторизация в системе Электронного дневника, требутся предварительное указание логина и пароля в обьекте класса"
        auth_url = f"https://elschool.ru/logon/index?login={login}&password={password}"
        self.payload = {}

        session = requests.Session()
        response = session.post(auth_url, data=self.payload)  # headers=self.headers
        try:
            self.headers = {
                'Cookie': f"JWToken={session.cookies.get_dict()['JWToken']}"
            }
        except:
            print("Неверные данные авторизации Elschool")
            exit(1)
        # soup = BeautifulSoup(response) # HTML, взятый по ссылке
        # img = soup.find('div.w3-container img.w3-image') # Вам придется продумать выборку
        # src = img.attrs.get('src')

    def download(self):
        "Скачивание общей XLSX таблицы с картами"
        self.download_url = "https://elschool.ru/districts/50/schools/442/setting/unload/unloadcard"  # TODO: Придумать генератор ссылки на загрузку

        self.payload = {}

        self.response = requests.request("GET", self.download_url, data=self.payload)
        with open('cards.xlsx', 'wb') as file:
            file.write(self.response.content)



# con = pymysql.connect('localhost', 'root', 'test1', 'tc-db-main')

licey_elschool = Elschool(settings.ELSCHOOL_LOGIN, settings.ELSCHOOL_PASSWORD)

licey_elschool.download()
# На этом моменте в рабочей папке лежит cards.xlsx

excel_data = pd.read_excel('cards.xlsx')
# ['Класс', 'ФИО', 'Номер карты', 'Чип карты', 'Декодированный чип', 'Десятичное значение декодированного чипа'])
df = pd.DataFrame(excel_data, columns=['Класс', 'ФИО', 'Декодированный чип'])

for i in df.iterrows():
    id = i[0]
    klass = i[1][0]
    last_name, first_name, sure_name = i[1][1].split()[:3]
    card = i[1][2]
    klass = Group.objects.get_or_create(name=klass.upper())[0]
    print(klass)
    students = Students.objects.get_or_create(
        first_name=first_name,
        last_name=last_name,
        sure_name=sure_name,
        klass=klass,
        )[0]
    students.card=card
    students.save()
