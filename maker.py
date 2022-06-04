import csv
import cv2
from PIL import Image
import pytesseract
from multiprocessing import Process, cpu_count, Manager, Value, Array
import sys


def work(filepath, progress, text_list, count_list, work_length, length,skip=12, processor_num=0):
    start_frame = work_length * processor_num
    if processor_num == cpu_count()-1:
        end_frame = length
    else:
        end_frame = start_frame + work_length + skip

    video = cv2.VideoCapture(filepath)

    pytesseract.pytesseract.tesseract_cmd = "./tesseract/tesseract.exe"
    for idx in range(start_frame, end_frame+1, skip):
        video.set(1, idx)
        image = video.read()[1]
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        text_list[idx] = pytesseract.image_to_string(image=Image.fromarray(gray), lang='kor')
        if idx != start_frame:
            t1 = text_list[idx-skip].split(":")
            t2 = text_list[idx].split(":")
            duple = len(t1 + t2) - len(set(t1 + t2))
            count_list[idx] += len(t1) - duple
            count_list[idx] += len(t2) - duple
        progress.value += 1/length
        percentage = float(progress.value * 100 * skip)
        if percentage > 99.99: percentage = 99.99
        print(f'\rProcess {percentage:0.2}% completed..', end='')
    

if __name__ == "__main__":
    filepath = './test.mp4'
    video = cv2.VideoCapture(filepath) #'' 사이에 사용할 비디오 파일의 경로 및 이름을 넣어주도록 함

    if not video.isOpened():
        print("Could not Open :", filepath)
        exit(0)

    #불러온 비디오 파일의 정보 출력
    length = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
    width = int(video.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = int(video.get(cv2.CAP_PROP_FPS))
    processor_nums = cpu_count()
    assined_len = length//processor_nums
    progress = [0.00] * processor_nums
    print("length :", length)
    print("width :", width)
    print("height :", height)
    print("fps :", fps)


    #프레임을 저장할 디렉토리를 생성
    skip = 12
    if int(fps) % skip != 0:
        raise ValueError("fps should be divided by skip")
    if skip > 60:
        raise ValueError("Skip can't over 60!")
    print('Number of CPU:',processor_nums)
    if processor_nums > 2:
        print('Use Multiprocess')
    print('')
    print('')
    print("Process Start")

    #make global Array, Value
    progress = Value('d', 0.00)
    tl = ['' for _ in range(length)]
    text_list = Manager().list(tl)
    count_list = Array('i', [0 for _ in range(length)])
    work_length = (length // (fps * processor_nums)) * fps

    for processor_num in range(processor_nums):
        globals()[f"th{processor_num}"] = Process(target=work, args=(filepath, progress, text_list, count_list, work_length, length, skip, processor_num))
        globals()[f"th{processor_num}"].start()

    for processor_num in range(processor_nums):
        globals()[f"th{processor_num}"].join()

    print(f'\rProcess Done!                                         ')


    f0 = open('test_temp.csv','w', newline='')
    wr = csv.writer(f0)
    wr.writerow(text_list)
    f0.close()

    f1 = open('temp.csv','w', newline='')
    wr = csv.writer(f1)
    wr.writerow(count_list[:])
    f1.close()

    counts = [count_list[i] for i in range(0, length, skip)]
    f2 = open('result.csv','w', newline='')
    wr = csv.writer(f2)
    wr.writerow(counts)
    f2.close()