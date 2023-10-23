import dataclasses
from enum import Enum
import random

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

#Список самосвалов
samosval_list = [ dataclasses.replace(small_samosval), dataclasses.replace(small_samosval), dataclasses.replace(big_samosval)]

#Количество минут в часу
hour = 60

#Количество линий     
line_count = 3

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


#Симуляция одной линии
def simulation_line():
    delta_t = 1 #Дельта Т
    time = hour * 3 #Время
    weight_active = 0 #Вес
    zagruz_active_time = 0 #Время когда загруз активен
    zagruz_free_time = 0 #Время когда загруз простаивает
    zagruz_is_free = True #Свободен загруз

    queue_length = {
        0 : 0,
        1 : 0,
        2 : 0,
        3 : 0,
    }

    #При первой итерации самосвалы находяться рядом с эскаватором приступают к работе сразу
    samosval_list_temp = samosval_list.copy()

    for i in range(int(time/delta_t)):
        #Обновляем движения в начале новой итерации
        renew_moves(samosval_list_temp)
        
        #Считаем очередь в начале итерации

        waitsamosval_list = get_place_samosval_list_from_list(samosval_list_temp, Place.wait)
        if (waitsamosval_list):
            queue_length[len(waitsamosval_list)] += 1
        else :
            queue_length[0] += 1
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

    print(f'Вес = {weight_active}; Загруз активное время = {zagruz_active_time}; Загруз время простоя = {zagruz_free_time};')
    print("Длинна очереди")
    print(queue_length)
    print("Количество итераций")
    print(i)
#Запускам симуляцию для трех линий
def main():
    for i in range(line_count):
        simulation_line()


if __name__ == "__main__":
    main()