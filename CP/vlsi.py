import os


def run_solver(model_name, instance, dst, args):
    model_path = os.path.join('models', model_name)
    if not os.path.exists(model_path):
        raise FileNotFoundError()

    if not os.path.exists(dst):
        os.makedirs(dst)
        
    file_suffix = instance.split('/')[-1].split('-')[-1]
    f_src = open(instance, 'r')
    f_dst = open(os.path.join(dst, '.tmp.dzn'), 'w')

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
    
    f_dst.write('|];\n')
    f_dst.write('h_var = "' + args.heuristic_var + '";\n')
    f_dst.write('h_dom = "' + args.heuristic_dom + '";\n')
    f_dst.write('restart = "' + args.restart + '";\n')
    f_dst.flush()

    f_src.close()
    f_dst.close()
    cmd = 'minizinc ' + model_path + ' {} --search-complete-msg \"\" --soln-sep \"\"'.format(os.path.join(dst, '.tmp.dzn'))
    cmd += f' --param-file models/{args.solver}.mpc'
    cmd += ' -f' if args.free_search else ''
    stream = os.popen(cmd)
    output = stream.read()
    f_out = open(os.path.join(dst, 'out-'+file_suffix), 'w')
    f_out.write(output)
    f_out.close()
    print(output.split('% ')[-1])
    os.remove(os.path.join(dst, '.tmp.dzn'))