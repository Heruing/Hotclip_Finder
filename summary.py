import csv
 
f = open('result.csv', 'r')
rdr = csv.reader(f)
for line in rdr:
    counts = tuple(map(int, line))

second = []

for idx in range(0, len(counts)-1, 2):
    second.append((counts[idx] + counts[idx+1], idx//2))


summary =  []
for hot, time in sorted(second, reverse=True)[:10]:
    mm = time // 60
    ss = time % 60
    summary.append(f'{mm:02}:{ss:02}')


f = open('summary.csv','w', newline='')
wr = csv.writer(f)
wr.writerow(summary)
f.close()