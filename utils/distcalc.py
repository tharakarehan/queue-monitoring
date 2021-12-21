

def distance(d1, d2):
    x1, y1 = (d1[2] + d1[0]) / 2, (d1[1] + d1[3]) / 2
    x2, y2 = (d2[2]+d2[0])/2, (d2[1]+d2[3])/2
    x_d = (x2 - x1)
    y_d = (y2 - y1)
    dis = ((x_d)**2 + (y_d)**2)**0.5
    return dis

def filterbydis(trackers, Nmeter, qs):
    candidates = []
    ylist = []
    idxlist = []
    iylist = []
    for idx, d1 in enumerate(trackers):
        ylist.append((d1[4],(d1[0]+d1[2])/2))
        for d2 in trackers[idx:]:
            if d1[4] != d2[4] and distance(d1, d2) < Nmeter:
                candidates.append(d1[4])
                candidates.append(d2[4])
    if qs == 'R':     
        ylist.sort(key=lambda tup: tup[1],reverse=True)
    else:
        ylist.sort(key=lambda tup: tup[1],reverse=False)
    count = 0
    for idx, iy in ylist:
        count+=1
        if idx in list(set(candidates)):
            idxlist.append(idx)
            iylist.append(count)

    return idxlist, iylist, ylist, list(set(candidates))

                