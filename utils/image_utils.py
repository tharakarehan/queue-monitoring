import cv2
import numpy as np

global lines
lines = []

drawing = False
x2,y2 = -1,-1

def draw_box(frame, det,width,height, ylist, canlist):
    
    # if (abs(det[2] - det[0]) > 0.04 * width) and (abs(det[3] - det[1]) > 0.04 * height):
    if det[4] in canlist:
        color = (0, 0, 255)
        Qidx = list(map(lambda x:x[0],ylist)).index(det[4])+1
        draw_text(frame, 'QueueId={} TrackId={}'.format(Qidx,det[4]), (det[0]-10, det[1]-10), cv2.FONT_HERSHEY_SIMPLEX, 0.4,(0,0,0),1,color)
    else:
        color = (0, 255, 0)
        Qidx = list(map(lambda x:x[0],ylist)).index(det[4])+1
        draw_text(frame, 'QueueId={} TrackId={}'.format(Qidx,det[4]), (det[0]-10, det[1]-10), cv2.FONT_HERSHEY_SIMPLEX, 0.4,(0,0,0),1,color)
    cv2.rectangle(frame, (det[0], det[1]), (det[2], det[3]), color, 2)
    
    return frame
    # else:
    #     return frame

def draw_info(frame, ListQ, ListT):
    draw_text(frame, 'Queue Indexes: {}'.format(ListQ), (10,10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255), 1, (0,0,0))
    draw_text(frame, 'Track Indexes: {}'.format(ListT), (10,30), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255), 1, (0,0,0))
    return frame

def draw_text(img, text,
          pos=(0, 0),
          font=cv2.FONT_HERSHEY_PLAIN,
          font_scale=3,
          text_color=(0, 255, 0),
          font_thickness=2,
          text_color_bg=(0, 0, 0)
          ):

    x, y = pos
    text_size, _ = cv2.getTextSize(text, font, font_scale, font_thickness)
    text_w, text_h = text_size
    cv2.rectangle(img, pos, (x + text_w, y + text_h), text_color_bg, -1)
    cv2.putText(img, text, (x, int(y + text_h + font_scale - 1)), font, font_scale, text_color, font_thickness)
    return text_w, text_h

def draw_shape(event,x,y,flag,parm):
    global x2,y2,drawing, img, img2
    
    if len(lines) < 2:
        if event == cv2.EVENT_LBUTTONDOWN:
            print('Clicked: ', (x,y))
            lines.append((x, y))
            drawing = True
            img2 = img.copy()
            x2,y2 = x,y
            cv2.line(img,(x2,y2),(x,y),(0,0,255),1, cv2.LINE_AA)

        elif event == cv2.EVENT_MOUSEMOVE:
            if drawing == True:
                # print('Moving: ',(x,y))
                a, b = x, y
                if a != x & b != y:
                    img = img2.copy()
                    cv2.line(img,(x2,y2),(x,y),(0,255,0),1, cv2.LINE_AA)

        elif event == cv2.EVENT_LBUTTONUP:
            drawing = False
            print('Released: ',(x,y))
            lines.append((x, y))
            img = img2.copy()
            cv2.line(img,(x2,y2),(x,y),(0,0,255),1, cv2.LINE_AA)
    else:
        return

def get_first_frame(video_path):
    vidcap = cv2.VideoCapture(video_path)
    success, image = vidcap.read()
    if success:
        print("yes")
        return image

def draw_lines(video_path):
    global img, img2
    img = get_first_frame(video_path)
    img2 = img.copy()
    cv2.namedWindow("Pedestron")
    cv2.setMouseCallback("Pedestron",draw_shape)
    
    # press the escape button to exit
    while True:
        cv2.imshow("Pedestron",img)
        k = cv2.waitKey(1) & 0xFF
        if k == 27:
            break

    cv2.destroyAllWindows()
  
    return lines

def define_ROI( video_path, height, width):
    """
    Define Region of Interest based on user input.
   """
    
    lines = draw_lines(video_path)
    print(lines)
    return [lines[0], lines[1]]