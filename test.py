from multiprocessing import Process, cpu_count, Array, Value, Manager

import time

def f(progress, list_managed, process_num, process_nums):
    start = process_num * (100//process_nums)
    if process_num+1 == process_nums:
        end = 100
    else:
        end = start + (100//process_nums)
    
    for i in range(start, end):
        progress.value += 0.01
        time.sleep(0.5)
        list_managed[i] = 'x'
        #print(list_managed)
        print(f'\r{progress.value:0.2f}', end='')


if __name__ == '__main__':
    progress = Value('d', 0.000)
    shared_list = [f'{i}' for i in range(100)]
    list_managed = Manager().list(shared_list)
    process_nums = cpu_count()
    print(process_nums)
    for process_num in range(process_nums):
        globals()[f"p{process_num}"] = Process(target=f, args=(progress, list_managed, process_num, process_nums))
        globals()[f"p{process_num}"].start()

    for process_num in range(process_nums):
        globals()[f"p{process_num}"].join()


    #print(f'{progress.value:0.2f}')