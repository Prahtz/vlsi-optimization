import os
import argparse
from utils import display_results
from vlsi_complete import VLSIComplete
from vlsi_rotation import VLSIRotation

def main(args):
    model_name, instance, dst_path = args.model_name, args.instance_path, args.dst_path
    display = args.display
    folder = args.folder
    encoding = args.sat_encoding
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
        if model_name == 'rotation':
            vlsi = VLSIRotation(instance_path=file_path, dst_path=dst_path, encoding=encoding)
        elif model_name == 'complete':
            vlsi = VLSIComplete(instance_path=file_path, dst_path=dst_path, encoding=encoding)
        else:
            raise RuntimeError('model_name not expected')
        result = vlsi.solve()
        if result:
            if display:
                display_results(os.path.join(dst_path, 'out-'+file_path.split('/')[-1].split('-')[-1]))
        else:
            print('UNSAT')

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('model_name', help='name of the model to run', choices=['complete', 'rotation'])
    parser.add_argument('instance_path', help='path of the instance file. If \"--folder\" is set, you must specify the folder containing all the instances')
    parser.add_argument('dst_path', help='path of the folder containing the solutions')
    parser.add_argument('-f', '--folder', help='solve all the instances contained in \"instance_path\"', action="store_true")
    parser.add_argument('-d', '--display', help='if found, display the solution', action="store_true")
    parser.add_argument('-e', '--sat-encoding', help='specify the encoding technique for the "exactly one" constraint', choices=['pairwise', 'sequential', 'heule', 'bitwise'], default='pairwise')
    args = parser.parse_args()
    main(args)