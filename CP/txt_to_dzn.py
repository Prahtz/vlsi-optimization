import os
import sys
if __name__ == '__main__':
    args = sys.argv[1:]
    if len(args) < 2:
        print('Usage: python txt_to_dzn.py <src-txt-folder> <dst-dzn-folder>')
    else:
        src, dst = args
        if not os.path.exists(src):
            print('Source directory does not exists')
        else:
            if not os.path.exists(dst):
                os.makedirs(dst)
            for file in sorted(os.listdir(src)):
    
                file_name = file.split('.')[0]
                f_src = open(os.path.join(src, file), 'r')
                f_dst = open(os.path.join(dst, file_name + '.dzn'), 'w')

                w = f_src.readline().strip()
                f_dst.write('w = {};\n'.format(w))
                n = f_src.readline().strip()
                f_dst.write('n = {};\n'.format(n))
                f_dst.write('m = [')
                for i in range(int(n)):

                    item = f_src.readline().strip().split(' ')
                    if i != 0:
                        f_dst.write('\n\t |{},{}'.format(item[0], item[1]))
                    else:
                        f_dst.write('|{},{}'.format(item[0], item[1]))

                
                f_dst.write('|];')

