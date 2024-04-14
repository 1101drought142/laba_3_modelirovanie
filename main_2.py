import dataclasses
from enum import Enum
import random
import statistics

from matplotlib import pyplot as plt

#Перечесляемый тип для устновки текущей позиции самосвала в потоке моделирования
class Place(Enum):
    wait = 1
    road = 2
    zarguz = 3
    

#Обьект самосвала
@dataclasses.dataclass
class Samosval:
    name: str #Название
    weight: int #Вес
    zarguz: int #Мат ожидание загрузки
    road_to: int #Время дороги до разгрузки
    razgruz: int #Мат ожидание загрузки
    road_from: int #Дорога от разгрузки
    place: Place #Текщие место в потоке моделирования
    time_left: int #Осталось время текущего этапа моделирования

#Моделирование по принципу особых состояний
#Состояний 2 - 
#Окончания загрузки самосвала
#Возвращение самосвала на позицию загрузки

#Количество минут в часу
hour = 60
hours = 8
max_minutes = hour * hours

#Количество линий     
line_count = 3

#Количетсво повторов
iteration_ccount = 1

#Создание двух типов самосвалов
small_samosval = Samosval("small", 20, 5, 2.5, 2, 1.5, Place.wait, 0)
big_samosval = Samosval("big", 50, 10, 3, 4, 2, Place.wait, 0)
eskovator_free = True

# Очередь у экскаватора на старте моделирования
for iter_c in range(iteration_ccount):
    time_passed = 0
    samosval_list_temp = [ dataclasses.replace(small_samosval), dataclasses.replace(small_samosval), dataclasses.replace(big_samosval)]
    #while (time_passed < max_minutes):
    for i in range(2):
        time_passed_1 = 0
        time_passed_2 = 0
        # Отправляем самосвал на дорогу
        for samosval in samosval_list_temp:
            if (samosval.place == Place.zarguz):
                #samosval.place = Place.road
                time_passed_1 = samosval.road_to + samosval.road_from  + samosval.razgruz #+ random.expovariate(lambd = 1.0 / samosval.razgruz)
                samosval.time_left = time_passed_1
                break

        # Проверяем состояние экскаватора
        if (eskovator_free):
            # Помещаем самосвал на позицию загрузки
            for samosval in samosval_list_temp:
                if (samosval.place == Place.wait):
                    samosval.place = Place.zarguz
                    time_passed_2 = samosval.zarguz #random.expovariate(lambd = 1.0 / samosval.zarguz)
                    samosval.time_left = time_passed_2
                    break
        
        min_time = 999999999
        for index, samosval in enumerate(samosval_list_temp):
            if samosval.time_left < min_time and samosval.time_left > 0:
                min_time = samosval.time_left
                res_index = index
                break
        
        print("----------------------------------------")

        print(res_index)        

        for index, samosval in enumerate(samosval_list_temp):
            print(index, samosval)
            if (samosval.time_left > 0 and index != res_index):
                samosval.time_left -= min_time
                print(samosval.name, samosval.place, samosval.time_left)

        samosval_list_temp[res_index].time_left = 0
        if (samosval_list_temp[res_index].place == Place.zarguz):
            samosval_list_temp[res_index].place = Place.road
        elif(samosval_list_temp[res_index].place == Place.road):
            samosval_list_temp[res_index].place = Place.wait

        for samosval in samosval_list_temp:
            print(samosval.name, samosval.place, samosval.time_left)
        print(min_time)
        time_passed += min_time
        print(time_passed)
        print("----------------------------------------")

        