import dataclasses
from enum import Enum
import random

class Place(Enum):
    wait = 1
    zarguz = 2
    road_to = 3
    razgruz = 4
    road_from = 5

@dataclasses.dataclass
class Samosval:
    name: str
    weight: int
    zarguz: int
    road_to: int
    razgruz: int
    road_from: int
    place: Place
    time_left: int
    move_made: bool

small_samosval = Samosval("small", 20, 5, 2.5, 2, 1.5, Place.wait, 0, False)
big_samosval = Samosval("big", 50, 10, 3, 4, 2, Place.wait, 0, False)

samosval_list = [ dataclasses.replace(small_samosval), dataclasses.replace(small_samosval), dataclasses.replace(big_samosval)]

hour = 60
    
line_count = 3

def get_place_samosval_from_list(samosval_list_temp: list[Samosval], place: Place) -> None | Samosval :
    for samosval in samosval_list_temp:
        if (samosval.move_made):
            continue
        if (samosval.place == place): return samosval
    return None

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

def renew_moves(samosval_list_temp: list[Samosval]):
    for samosval in samosval_list_temp:
        samosval.move_made = False

def simulation_line():
    delta_t = 1
    time = hour * 3
    weight_active = 0
    zagruz_active_time = 0
    zagruz_free_time = 0
    zagruz_is_free = True

    #При первой итерации самосвалы находяться рядом с эскаватором приступают к работе сразу
    samosval_list_temp = samosval_list.copy()

    for i in range(int(time/delta_t)):
        renew_moves(samosval_list_temp)
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

        zagruz_samosval = get_place_samosval_from_list(samosval_list_temp, Place.zarguz)
        if (zagruz_samosval): 
            zagruz_samosval.time_left -= delta_t
            if (zagruz_samosval.time_left <= 0):
                zagruz_samosval.place = Place.road_to
                zagruz_samosval.move_made = True
                zagruz_samosval.time_left = int(zagruz_samosval.road_to)
                zagruz_is_free = True

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

        razgruz_samosval_list = get_place_samosval_list_from_list(samosval_list_temp, Place.razgruz)
        if (razgruz_samosval_list): 
            for razgruz_samosval in razgruz_samosval_list:
                razgruz_samosval.time_left -= delta_t
                if (razgruz_samosval.time_left <= 0):
                    razgruz_samosval.place = Place.road_from
                    razgruz_samosval.move_made = True
                    razgruz_samosval.time_left = int(razgruz_samosval.road_from)    
                    weight_active += razgruz_samosval.weight    

        
        road_from_samosval_list = get_place_samosval_list_from_list(samosval_list_temp, Place.road_from)
        if (road_from_samosval_list): 
            for road_from_samosval in road_from_samosval_list:
                road_from_samosval.time_left -= delta_t
                if (road_from_samosval.time_left <= 0):
                    road_from_samosval.place = Place.wait
                    road_from_samosval.move_made = True
                    road_from_samosval.time_left = 0

    print(f'Вес = {weight_active}; Загруз активное время = {zagruz_active_time}; Загруз время простоя = {zagruz_free_time};')


def main():
    for i in range(line_count):
        simulation_line()


if __name__ == "__main__":
    main()