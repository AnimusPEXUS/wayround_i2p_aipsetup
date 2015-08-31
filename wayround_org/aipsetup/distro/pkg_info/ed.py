
import os

lst = os.listdir()

for i in lst:

    if i.endswith('.json'):
        print(i)

        f = open(i)
        lines= f.readlines()
        f.close()

        for j in range(len(lines)):
            if '024' in lines[j]:
                print('found')
            lines[j] = lines[j].replace(r'- version !re ^\\d*\\.\\d*[02468][\\.&]' , '')

        f = open(i, 'w')
        f.writelines(lines)
        f.close()
