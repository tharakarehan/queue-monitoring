import pyttsx3
def announce(word):
    engine.say(word)
    engine.runAndWait()

engine = pyttsx3.init()
count = 0
while True:
    f = open(r'recite_audio.txt','r')
    f1 = f.readlines()
    L =len(list(f1))
    if L > count and L != 0:
        Str = list(f1)[count][:-2]
        announce(Str)
        count+=1
        f.close()
    else:
        f.close()
        continue
        