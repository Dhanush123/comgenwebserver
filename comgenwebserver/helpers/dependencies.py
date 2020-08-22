import os
import sys
import subprocess


def install_some_dependencies():
    if not os.path.isdir(os.path.join(os.getcwd(), 'keras')):
        print(subprocess.run(f'git clone https://github.com/MarcBS/keras.git', shell=True,
                             stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True))

    # nmt_keras_dir = os.path.join(os.getcwd, 'nmt-keras')
    if not os.path.isdir(os.path.join(os.getcwd(), 'comgenwebserver', 'helpers', 'nmt-keras')):
        print(subprocess.run(f'git clone https://github.com/lvapeab/nmt-keras {os.getcwd()}/comgenwebserver/helpers/nmt-keras && cd "nmt-keras" && pipenv install -d {os.getcwd()}/helpers/nmt-keras -e .', shell=True,
                             stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True))
        # print(subprocess.run(f'cd {nmt_keras_dir} && pipenv install -e .', shell=True,
        #                      stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True))

    sys.path.insert(0, os.path.join(os.getcwd(), 'nmt-keras'))
    sys.path.insert(0, os.path.join(os.getcwd(), 'nmt-keras', 'nmt_keras'))
    sys.path.append(os.path.dirname(os.path.realpath(__file__)) + '/../')
    sys.path.append(os.path.dirname(os.path.realpath(__file__)) + '/../../')
    sys.path.append(os.path.dirname(os.path.realpath(__file__)) + '/../../../')
    print("sys path!!!", sys.path)

    print("ran cmds??!!")


if __name__ == "__main__":
    install_some_dependencies()
