import argparse
import os
from vlsi_rotation_standard import VLSIRotationStandard
from vlsi_rotation_complete import VLSIRotationComplete
from vlsi_complete import VLSIComplete
from vlsi_standard import VLSIStandard
from utils import display_results
import pulp

def main(args):
    model_name = args.model_name
    solver = args.solver
    instance =  args.instance_path
    dst_path = args.dst_path
    display = args.display
    folder = args.folder
    if not os.path.exists(instance):
        print('Input path does not exists')
        return
    if not os.path.exists(dst_path):
        os.makedirs(dst_path)
    if not folder:
        instances = [instance]
    else:
        instances = [os.path.join(instance, i) for i in sorted(os.listdir(instance))]
    for file_path in instances:
        print(file_path)
        if model_name == 'rotation_complete':
            vlsi = VLSIRotationComplete(instance_path=file_path, dst_path=dst_path)
        elif model_name == 'rotation_standard':
            vlsi = VLSIRotationStandard(instance_path=file_path, dst_path=dst_path)
        elif model_name == 'standard':
            vlsi = VLSIStandard(instance_path=file_path, dst_path=dst_path)
        elif model_name == 'complete':
            vlsi = VLSIComplete(instance_path=file_path, dst_path=dst_path)
        else:
            raise RuntimeError('model_name not expected')

        out_file = os.path.join(dst_path, 'out-'+file_path.split('/')[-1].split('-')[-1])
        result = vlsi.solve(solver, out_file)
        if result == 'Optimal':
            if display:
                display_results(out_file)
        else:
            print(result)
    

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('model_name', help='name of the model to run', choices=['standard', 'complete', 'rotation_standard', 'rotation_complete'])
    parser.add_argument('solver', help='define the solver to be used', choices=pulp.listSolvers(True), default=False)
    parser.add_argument('instance_path', help='path of the instance file. If \"--folder\" is set, you must specify the folder containing all the instances')
    parser.add_argument('dst_path', help='path of the folder containing the solutions')
    parser.add_argument('-f', '--folder', help='solve all the instances contained in \"instance_path\"', action="store_true")
    parser.add_argument('-d', '--display', help='if found, display the solution', action="store_true")
    args = parser.parse_args()
    main(args)