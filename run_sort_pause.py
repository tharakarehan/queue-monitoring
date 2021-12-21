import time
import cv2
import numpy as np
import argparse
from utils import image_utils
from utils import distcalc
from utils.model_utils import pedestrianDetector
from sort import Sort
import pyttsx3

def announce(word):
    engine.say(word)
    engine.runAndWait()

def audio():
    global audio_list_pos
    if len(audio_list_pos) != 0:
        pos_x = audio_list_pos.pop(0)
        announce(reciteList[pos_x-1])

def audio_list(List):
    if len(List) > 1: 
        Listword = list(map(lambda x:reciteList[x-1],List))
        STR = ' and '.join(Listword)
    else:
        STR = reciteList[List[0]-1]
    announce(STR)
            
if __name__ == "__main__":

    reciteList = ['First','Second','Third','Fourth','Fifth','Sixth','Seventh','Eighth','Nineth','Tenth']
    parser = argparse.ArgumentParser(description='Run SORT')
    parser.add_argument('-i','--input_file', type=str, required=True, help='Input videos file path name')
    parser.add_argument('-m','--model_path', type=str, required=True, help='path to the model')
    parser.add_argument('-t', '--threshold', type=float, default=0.7, help='threshold for detections')
    parser.add_argument('-d', '--duration', type=float, default=30, help='duration to check before label as parked')
    parser.add_argument('-o','--output_file', type=str, help='Output video file path name')
    parser.add_argument('-f','--queue_start', type=str, default= 'R', help='Start of the Queue L or R')
    parser.add_argument('--save', action='store_true')
    args = parser.parse_args()

    # initialize the video stream, pointer to output video file, and frame dimensions
    inputFile = args.input_file
    vs = cv2.VideoCapture(inputFile)
    fps = int(vs.get(cv2.CAP_PROP_FPS))
    total = int(vs.get(cv2.CAP_PROP_FRAME_COUNT))
    (W, H) = (int(vs.get(cv2.CAP_PROP_FRAME_WIDTH)), int(vs.get(cv2.CAP_PROP_FRAME_HEIGHT)))

    print("Original FPS:", fps)
    dis = args.duration
    Tr = args.threshold
    tracker = Sort()
    qs = args.queue_start
    if args.save:
        print('Save')
        result = cv2.VideoWriter(args.output_file,  
                                cv2.VideoWriter_fourcc(*'MP4V'), 
                                fps, (W,H))

    model = pedestrianDetector(args.model_path, H, W, Tr)
    model.load()
    line = image_utils.define_ROI(inputFile, H, W)
    meter = ((line[0][0] - line[1][0])** 2 + (line[0][1] - line[1][1])** 2)** 0.5
    pastlog = {}
    final_dict_ck = {}
    engine = pyttsx3.init()

    while True:
        (grabbed, frame) = vs.read()
        if not grabbed:
            break
        
        detections = model.predict(frame)
        trackers = tracker.update(detections, frame)
        closeid , iylist, ylist, canlist  = distcalc.filterbydis(trackers, meter, qs)
       
        for d in trackers:
            d = d.astype(np.int32)
            # print(d)
            frame = image_utils.draw_box(frame, d, W, H, ylist, canlist)
            if d[4] not in pastlog:
                pastlog[d[4]] = []
            if d[4] in closeid:

                if len(pastlog[d[4]]) < dis:
                    pastlog[d[4]].append(True)
                else:
                    pastlog[d[4]].pop(0)
                    pastlog[d[4]].append(True)
            else:

                if len(pastlog[d[4]]) < dis:
                    pastlog[d[4]].append(False)
                else:
                    pastlog[d[4]].pop(0)
                    pastlog[d[4]].append(False)

        # print(pastlog)
        final_list_pos = []
        final_list_idx = []
        audio_list_pos = []
        audio_list_idx = []
        strQ = ''
        strT = ''
        for idx, iy in list(zip(closeid, iylist)):
            if idx not in final_dict_ck:
                final_dict_ck[idx] = True

            if len(pastlog[idx]) == dis and all(pastlog[idx]):
                final_list_idx.append(idx)
                final_list_pos.append(iy)
            
            if (len(pastlog[idx]) == dis and all(pastlog[idx])) and final_dict_ck[idx]:
                audio_list_pos.append(iy)
                audio_list_idx.append(idx)
                final_dict_ck[idx] = False
            elif not (len(pastlog[idx]) == dis and all(pastlog[idx])):
                final_dict_ck[idx] = True

        if len(final_list_idx) == 1:
            strQ = str(final_list_pos[0])
            strT = str(final_list_idx[0])
            frame = image_utils.draw_info(frame,strQ,strT)
        elif len(final_list_idx) > 1:
            strQ = ','.join(list(map(str,final_list_pos)))
            strT = ','.join(list(map(str,final_list_idx)))
        frame = image_utils.draw_info(frame,strQ,strT)
        # print(final_list_pos)
        # print(pastlog)

        if args.save:
            result.write(frame)
           
        cv2.imshow('pedestron', frame)
        if fps < 20:
            cv2.waitKey(5)
        k = cv2.waitKey(1) & 0xFF
        if k == 27:
            cv2.destroyAllWindows()
            break
        
        if len(audio_list_pos) != 0:
            audio_list(audio_list_pos)

    if args.save:
        result.release()
    vs.release()
    