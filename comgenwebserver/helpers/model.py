import os
import json
import sys

from keras_wrapper.cnn_model import loadModel
from keras_wrapper.dataset import Dataset, loadDataset
from keras_wrapper.utils import decode_predictions_beam_search

from comgenwebserver.constants import MODEL_EPOCH


def get_model_predictions(asts_path):
    print("os.getcwd()", os.getcwd())
    cur_dir = os.path.dirname(os.path.abspath(__file__))
    print("cur_dir", cur_dir)

    # if not os.path.isdir(os.path.join(os.getcwd(), 'keras')):
    #     print(subprocess.run(f'git clone https://github.com/MarcBS/keras.git', shell=True,
    #                          stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True))

    # # nmt_keras_dir = os.path.join(os.getcwd, 'nmt-keras')
    # if not os.path.isdir(os.path.join(os.getcwd(), 'nmt-keras')):
    #     print(subprocess.run(f'git clone https://github.com/lvapeab/nmt-keras && cd "nmt-keras" && pipenv install -e .', shell=True,
    #                          stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True))
    #     # print(subprocess.run(f'cd {nmt_keras_dir} && pipenv install -e .', shell=True,
    #     #                      stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True))
    #     print("ran cmds!!!")

    # sys.path.insert(0, os.path.join(os.getcwd(), 'nmt-keras'))
    # print("sys path!!!", sys.path)

    dataset = loadDataset(
        f'{cur_dir}/assets/epoch_{MODEL_EPOCH}_model_wrapper.pkl')
    with open('{cur_dir}/assets/params.json', 'r') as params_file:
        params = json.load(params_file)

    dataset.setInput(asts_path,
                     'test',
                     type='text',
                     id='source_text',
                     pad_on_batch=True,
                     tokenization=params['tokenize_x'],
                     fill='end',
                     max_text_len=params['x_max_text_len'],
                     min_occ=0)

    dataset.setInput(None,
                     'test',
                     type='ghost',
                     id='state_below',
                     required=False)

    dataset.setRawInput(asts_path,
                        'test',
                        type='file-name',
                        id='raw_source_text',
                        overwrite_split=True)

    nmt_model = loadModel('{cur_dir}/assets', MODEL_EPOCH)

    prediction_params = get_prediction_params()

    predictions = nmt_model.predictBeamSearchNet(
        dataset, params_prediction)['test']

    vocab = dataset.vocabulary['target_text']['idx2words']
    samples = predictions['samples']  # Get word indices from the samples.

    predictions = decode_predictions_beam_search(
        samples, vocab, verbose=params['VERBOSE'])

    return predictions


def get_prediction_params():
    return {
        'language': 'en',
        'tokenize_f': eval('dataset.' + tokenize_x),
        'beam_size': beam_size,
        'optimized_search': True,
        'model_inputs': params['INPUTS_IDS_MODEL'],
        'model_outputs': params['OUTPUTS_IDS_MODEL'],
        'dataset_inputs':  params['INPUTS_IDS_DATASET'],
        'dataset_outputs':  params['OUTPUTS_IDS_DATASET'],
        'n_parallel_loaders': n_parallel_loaders,
        'maxlen': y_max_text_len,
        'normalize_probs': True,
        'pos_unk': True and not is_transformer,
        'heuristic': 0,
        'state_below_maxlen': -1,
        'predict_on_sets': ['test'],
        'verbose': 0,
        'attend_on_output': is_transformer
    }
