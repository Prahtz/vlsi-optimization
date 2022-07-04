import os
from utils import *
import argparse
from vlsi import run_solver

def main(args):
    model_name, instance_path, dst_path = args.model_name, args.instance_path, args.dst_path
    display = args.display
    folder = args.folder
    model_name = 'vlsi_' + model_name + '.mzn'
    if not os.path.exists(instance_path):
        print('Input path does not exists')
        return
    if not os.path.exists(dst_path):
        os.makedirs(dst_path)
    if not folder:
        instances = [instance_path]
    else:
        instances = [os.path.join(instance_path, i) for i in sorted(os.listdir(instance_path))]
    for file_path in instances:
        run_solver(model_name=model_name, instance=file_path, dst=dst_path, args=args)
        if display:
            display_results(os.path.join(dst_path, 'out-'+file_path.split('/')[-1].split('-')[-1]))
                

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('model_name', help='name of the MiniZinc model to run', choices=['final','complete', 'rotation'])
    parser.add_argument('solver', help='name of the solver to use to address the problem', choices=['chuffed', 'geocode'])
    parser.add_argument('instance_path', help='path of the instance file. If \"--folder\" is set, you must specify the folder containing all the instances')
    parser.add_argument('dst_path', help='path of the folder containing the solutions')
    parser.add_argument('-f', '--folder', help='solve all the instances contained in \"instance_path\"', action="store_true")
    parser.add_argument('-F', '--free-search', help='solve allowing free search', action="store_true")
    parser.add_argument('-hv', '--heuristic-var', help='specify the heuristic strategy for choosing variables', choices=['dom_w_deg', 'first_fail', 'input_order'], default='input_order')
    parser.add_argument('-hd', '--heuristic-dom', help='specify the heuristic strategy for choosing domain values', choices=['indomain_random', 'indomain_min'], default='indomain_min')
    parser.add_argument('-r', '--restart', help='specify the restart strategy', choices=['restart_luby', 'restart_linear', 'restart_none'], default='restart_none')
    parser.add_argument('-d', '--display', help='if found, display the solution', action="store_true")
    args = parser.parse_args()

    if args.solver == 'chuffed' and args.heuristic_dom == 'indomain_random':
        parser.error('Value "indomain_random" for --heuristic-dom is not supported while using Chuffed as solver')
    main(args)