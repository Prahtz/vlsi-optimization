import os

if __name__ == '__main__':
    for dir in sorted(os.listdir('./')):
        if 'out_' in dir:
            for file_name in os.listdir(dir):
                with open(os.path.join(dir, file_name), 'r') as f:
                    w, h = [int(c) for c in f.readline().strip().split(' ')]
                    n = int(f.readline().strip())
                    x, y, dx, dy = [0]*n, [0]*n, [0]*n, [0]*n
                    for i in range(n):
                        dx[i], dy[i], x[i], y[i] = [int(c) for c in f.readline().strip().split(' ')]
                    f.close()
                
                for i in range(n):
                    for j in range(i+1, n):
                        if not (   
                                x[i] + dx[i] <= x[j] or \
                                x[j] + dx[j] <= x[i] or \
                                y[i] + dy[i] <= y[j] or \
                                y[j] + dy[j] <= y[i]):
                            print(f'Dir: {dir}, file: {file_name}, error at circuits {i} {j}:\n{dx[i]} {dy[i]} {x[i]} {y[i]}\n{dx[j]} {dy[j]} {x[j]} {y[j]}')
