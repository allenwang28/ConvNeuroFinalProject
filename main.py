import numpy as np

from rnn import RNN
import activation

import argparse
import pickle

import os
import matplotlib.pyplot as plt

if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument('learning_rule', 
                        choices=['modified', 'bptt', 'fa'],                    
                        action='store',
                        help="Choose between \'bptt\' \'fa\' and \'modified\'")

    parser.add_argument('--mode',
                        choices=['normal','compete'],
                        action='store',
                        default='normal',
                        help='Either choose a learning rule or compare the gradients for different learning rules')

    parser.add_argument('--training_data_path',
                        default='none',
                        type=str,
                        help='Path to pickled training data')

    # Optional args
    parser.add_argument('--bptt_truncate',
                        type=int,
                        action='store',
                        default=None,
                        help='Truncation for BPTT - Not providing this means there is no truncation')

    parser.add_argument('--kernel', help='TODO')
    parser.add_argument('--tau', type=float,
                        default=10000.)

    parser.add_argument('--validation_size', type=float,
                        default=0.3)


    parser.add_argument('--state_layer_activation',
                        choices=activation.activation_choices,
                        action='store',
                        help='State layer activation',
                        default='sigmoid')
    parser.add_argument('--output_layer_activation',
                        choices=activation.activation_choices,
                        action='store',
                        help='Output layer activation',
                        default='linear')
    parser.add_argument('--state_layer_size',
                        action='store',
                        type=int,
                        help='state layer size',
                        default=2)

    parser.add_argument('--eta', help='Learning Rate', type=float, default=0.001)
    parser.add_argument('--epochs', help='Epochs', type=int, default=1000)
    parser.add_argument('--v', '--verbose',
                        type=int,
                        help='Between 0-2', 
                        dest='verbose')

    parser.add_argument('--rand',
                        type=int,
                        help='Random seed',
                        default=None)

    args = parser.parse_args()

    input_layer_size = 2
    output_layer_size = input_layer_size
    if args.mode == 'normal':
        rnn = RNN(input_layer_size,
              args.state_layer_size, args.state_layer_activation,
              output_layer_size, args.output_layer_activation,
              epochs=args.epochs,
              bptt_truncate = args.bptt_truncate,
              learning_rule = args.learning_rule,
              tau = args.tau,
              eta=args.eta,
              rand=args.rand,
              verbose=args.verbose)
    elif args.mode == 'compete':
         rnn_bptt = RNN(input_layer_size,
                    args.state_layer_size, args.state_layer_activation,
                    output_layer_size, args.output_layer_activation,
                    epochs=args.epochs,
                    bptt_truncate = args.bptt_truncate,
                    learning_rule = 'bptt',
                    kernel = kernel,
                    eta=args.eta,
                    rand=args.rand,
                    verbose=args.verbose)       
         rnn_mlr =  RNN(input_layer_size,
                    args.state_layer_size, args.state_layer_activation,
                    output_layer_size, args.output_layer_activation,
                    epochs=args.epochs,
                    bptt_truncate = args.bptt_truncate,
                    learning_rule = 'modified',
                    kernel = kernel,
                    eta=args.eta,
                    rand=args.rand,
                    verbose=args.verbose)  

    # TODO - dummy placeholder simulation below
    trajectories = None
    if os.path.exists(args.training_data_path):
        with open(args.training_data_path, 'rb') as f:
            print "training"
            trajectories = pickle.load(f)
            if not trajectories:
                raise Exception('Invalid pkl file')
            X = []
            Y = []
            for trajectory in trajectories:
                X.append(np.array(trajectory[:-1])/600 - 0.5)
                Y.append(np.array(trajectory[1:])/600 - 0.5)
    else:
        X = []
        Y = []
        for i in range(10):
            x = np.random.normal(0, 1, (5,2))
            y = x / 10.

            X.append(x)
            Y.append(y)

    if args.mode == 'normal':
        training_losses, validation_losses = rnn.fit(X, Y, validation_size=args.validation_size)   
        plt.plot(range(args.epochs),training_losses, label='Training Loss')
        plt.plot(range(args.epochs),validation_losses, label='Validation Loss')
        plt.title("Training and validation losses for {0}".format(args.learning_rule))
        plt.legend()
        plt.show()
    elif args.mode == 'compete':
        training_losses, validation_losses = rnn_bptt.fit(X,Y)


