# -*- coding: utf-8 -*-

import dataclasses
from enum import Enum
import random
import statistics

from matplotlib import pyplot as plt

#Перечесляемый тип для устновки текущей позиции самосвала в потоке моделирования
class Place(Enum):
    wait = 1
    zarguz = 2
    road_to = 3
    razgruz = 4
    road_from = 5

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
    move_made: bool #На текущей итерация совершенно действие

#Создание двух типов самосвалов
small_samosval = Samosval("small", 20, 5, 2.5, 2, 1.5, Place.wait, 0, False)
big_samosval = Samosval("big", 50, 10, 3, 4, 2, Place.wait, 0, False)


#Количество минут в часу
hour = 60

#Количество линий     
line_count = 30

#Получаем один самосвал на конкретном этапе моделирования
def get_place_samosval_from_list(samosval_list_temp: list[Samosval], place: Place) -> None | Samosval :
    for samosval in samosval_list_temp:
        if (samosval.move_made):
            continue
        if (samosval.place == place): return samosval
    return None

#Получаем список самосвалов на конкретном этапе моделирования
def get_place_samosval_list_from_list(samosval_list_temp: list[Samosval], place: Place) -> None | list[Samosval] :
    result = []
    for samosval in samosval_list_temp:
        if (samosval.move_made):
            continue
        if (samosval.place == place): 
            result.append(samosval)
    if result:
        return result
    return None

#Обновляем движения в начале новой итерации
def renew_moves(samosval_list_temp: list[Samosval]):
    for samosval in samosval_list_temp:
        samosval.move_made = False

def create_plot1(queue_length_list : list[int]) -> None:
    plt.title("Средняя длина очереди")
    plt.xlabel("Время, минуты")
    plt.ylabel("Длина очереди, ед.")
    plt.plot(queue_length_list)
    plt.show()
#Создание графика
def create_plot(free_zagruz : list[int]) -> None:
    plt.title("Средняя загрузка экскаватора")
    plt.xlabel("Время, минуты")
    plt.ylabel("Занято, 1; Свободно, 0")
    plt.bar( [i for i in range( len(free_zagruz) )], free_zagruz, width=1.0)
    plt.show()

#Симуляция одной линии
def simulation_line():
    mean_time = 0 

    delta_t = 1 #Дельта Т
    time = hour * 8 #Время
    weight_active = 0 #Вес
    zagruz_active_time = 0 #Время когда загруз активен
    zagruz_free_time = 0 #Время когда загруз простаивает
    zagruz_is_free = True #Свободен загруз

    queue_length = {
        0 : 0,
        1 : 0,
        2 : 0,
        3 : 0,
        4 : 0,
        5 : 0,
        6 : 0,
        7 : 0,
        8 : 0,
    }
    queue_length_list = []
    free_zarguz = []
    #При первой итерации самосвалы находяться рядом с эскаватором приступают к работе сразу
    samosval_list_temp = [ dataclasses.replace(small_samosval), dataclasses.replace(small_samosval), dataclasses.replace(small_samosval), dataclasses.replace(small_samosval), dataclasses.replace(small_samosval)]


    for i in range(int(time/delta_t) + 1):

        if (zagruz_is_free):
            free_zarguz.append(0)
        else:
            free_zarguz.append(1)

        #Обновляем движения в начале новой итерации
        renew_moves(samosval_list_temp)
        
        #Считаем очередь в начале итерации

        waitsamosval_list = get_place_samosval_list_from_list(samosval_list_temp, Place.wait)
        if (waitsamosval_list):
            queue_length_list.append(len(waitsamosval_list))
            queue_length[len(waitsamosval_list)] += 1
        else :
            queue_length[0] += 1
            queue_length_list.append(0)

        #Если загруз свободен и есть свободный самосвал заполняем разгруз
        if (zagruz_is_free):
            waitsamosval = get_place_samosval_from_list(samosval_list_temp, Place.wait)
            if (waitsamosval):
                zagruz_is_free = False
                waitsamosval.place = Place.zarguz
                waitsamosval.move_made = True
                waitsamosval.time_left = int(random.expovariate(lambd = 1.0 / waitsamosval.razgruz))
                if (waitsamosval.time_left == 0):
                    waitsamosval.time_left = 1
                
            else:
                zagruz_free_time += delta_t
        else:
            zagruz_active_time += delta_t

        #Если есть самосвали которые закончили загруз отправляем их до разгруза
        zagruz_samosval = get_place_samosval_from_list(samosval_list_temp, Place.zarguz)
        if (zagruz_samosval): 
            zagruz_samosval.time_left -= delta_t
            if (zagruz_samosval.time_left <= 0):
                zagruz_samosval.place = Place.road_to
                zagruz_samosval.move_made = True
                zagruz_samosval.time_left = int(zagruz_samosval.road_to)
                zagruz_is_free = True

        #Если есть самосвалы которые доехали до разгруза то начинаем разгруз
        road_to_samosval_list = get_place_samosval_list_from_list(samosval_list_temp, Place.road_to)
        if (road_to_samosval_list): 
            for road_to_samosval in road_to_samosval_list:
                road_to_samosval.time_left -= delta_t
                if (road_to_samosval.time_left <= 0):
                    road_to_samosval.place = Place.razgruz
                    road_to_samosval.move_made = True
                    road_to_samosval.time_left = int(random.expovariate(lambd = 1.0 / road_to_samosval.razgruz))
                    if (road_to_samosval.time_left == 0):
                        road_to_samosval.time_left = 1

        #Если загруз свободен и есть свободный самосвал заполняем разгруз
        razgruz_samosval_list = get_place_samosval_list_from_list(samosval_list_temp, Place.razgruz)
        if (razgruz_samosval_list): 
            for razgruz_samosval in razgruz_samosval_list:
                razgruz_samosval.time_left -= delta_t
                if (razgruz_samosval.time_left <= 0):
                    razgruz_samosval.place = Place.road_from
                    razgruz_samosval.move_made = True
                    razgruz_samosval.time_left = int(razgruz_samosval.road_from)    
                    weight_active += razgruz_samosval.weight    

        #Если самосвал разгрузился то отправляем его до разгрузки
        road_from_samosval_list = get_place_samosval_list_from_list(samosval_list_temp, Place.road_from)
        if (road_from_samosval_list): 
            for road_from_samosval in road_from_samosval_list:
                road_from_samosval.time_left -= delta_t
                if (road_from_samosval.time_left <= 0):
                    road_from_samosval.place = Place.wait
                    road_from_samosval.move_made = True
                    road_from_samosval.time_left = 0

    print("Количество итераций")
    print(i)

    return [zagruz_active_time, zagruz_free_time, queue_length_list, free_zarguz]
    
#Запускам симуляцию для трех линий
def main():
    res = []
    for i in range(line_count):

        res.append(simulation_line())
    
    zagruz_active_time = 0
    zagruz_free_time = 0

    queue_length_list = []
    free_zarguz = []
    for r in res:
        zagruz_active_time_t, zagruz_free_time_t, queue_length_list_t, free_zarguz_t = r
        zagruz_active_time += zagruz_active_time_t
        zagruz_free_time += zagruz_free_time_t
        
        if (queue_length_list):
            for i in range(len(queue_length_list)):
                queue_length_list[i] += queue_length_list_t[i]
        else:
            queue_length_list = queue_length_list_t

        if (free_zarguz):
            for i in range(len(free_zarguz)):
                free_zarguz[i] += free_zarguz_t[i]
        else:
            free_zarguz = free_zarguz_t

    print(f'Среднее время работы загрузки = { round(zagruz_active_time / line_count, 2) }; Среднее время простоя загрузки = { round(zagruz_free_time / line_count, 2)}; Процент загрузки = {round(zagruz_active_time / (zagruz_active_time + zagruz_free_time) * 100, 2)}%; ; Процент простоя = {round(zagruz_free_time / (zagruz_active_time + zagruz_free_time) * 100, 2)}%;')

    queue_length_list = [i / line_count for i in queue_length_list]
    free_zarguz = [i / line_count for i in free_zarguz]

    print("Средняя длина очереди", round(statistics.mean(queue_length_list),2))
    print("Средняя загруженность экскаватора", round(statistics.mean(free_zarguz), 2))

    # create_plot(free_zarguz)
    # create_plot1(queue_length_list)

# 2 маленьких 1 большой
# 1 маленький 2 больших
# 4 маленьких
# 3 маленьких 1 большой
# 2 маленьких 2 больших
# 5 маленьких

# test = [ [290.73, 64.2, 81.91, 18.09, 0.9, 0.61] , [305.87, 68.4, 81.72, 18.28, 0.86, 0.64] , [310.6, 5.33, 98.31, 1.69, 1.71, 0.66] , [310.6, 5.33, 98.31, 1.69, 1.71, 0.66] , [323.77, 7.87, 97.63, 2.37, 1.61, 0.67], [315.8, 0.2, 99.94, 0.06, 2.67, 0.66] ] 

# res_res = []
# for t in test:
#     res_res.append(t[0])


# print(res_res)
# plt.title("Среднее время работы экскаватора")
# plt.xlabel("Типы комбинаций самосвалов, номер")
# plt.ylabel("Время, минуты")
# plt.plot(res_res)
#plt.show()

# plt.title("Процент простоя экскаватора")
# plt.xlabel("Типы комбинаций самосвалов, номер")
# plt.ylabel("Загрузка, проценты")
# plt.plot(res_res)
# plt.show()

# plt.title("Срелняя загрузка экскаватора")
# plt.xlabel("Типы комбинаций самосвалов, номер")
# plt.ylabel("Занято, 1; Свободно, 0")
# plt.plot(res_res)
# plt.show()

if __name__ == "__main__":
    main()

#Показатели эффективности
#Длина очередей
#Время работы загрузки
#Время простоя загрузки