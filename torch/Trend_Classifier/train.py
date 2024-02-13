import os
import torch
import torch.nn as nn
import torch.optim as optim
import math
import matplotlib.pyplot as plt
from torch.utils.data import DataLoader
import argparse
import data_loader

# set hyperparameters
num_epochs = 5
num_batches = 32
hidden_units = 10
learning_rate = 0.001

# Setup directories for loading data

# Target Device
device = "cuda" if torch.cuda.is_available() else "cpu"

# --------------------------------------------------------------------
# Models
# --------------------------------------------------------------------

# Define the binary classification model
class BinaryClassifier(nn.Module):
    def __init__(self):
        super(BinaryClassifier, self).__init__()
        self.hidden = nn.Linear(2, 10)  # 5 input features (o, h, l, c, t)
        self.relu = nn.ReLU()
        self.dropout = nn.Dropout(p=0.5)
        self.output = nn.Linear(10, 1)

    def forward(self, x):
        x = self.relu(self.hidden(x))
        x = self.output(x)  # Output without sigmoid for numerical stability with BCEWithLogitsLoss
        return x


# --------------------------------------------------------------------
# Evaluation function for accuracy
def calculate_accuracy(y_true, predicted):
    y_true = y_true.to(device)
    predicted = predicted.to(device)

    # print("Calculate Accuracy\n yTrue", y_true,"\n Predicted\n", predicted, "\n")
    # output_true = torch.round(torch.sigmoid(y_true))
    y_pred = torch.round(torch.sigmoid(predicted))  # Convert logits to probabilities and then to binary labels
    # print('YPRED', y_pred.size(), "\n Output", output_true.size() )
    # for i in range(y_pred):
    #     print(i)
    # print(f"\n True \n{y_true} Predictions \n{y_pred}\n")
    correct = (y_pred == y_true).float()  # Compare predicted labels with true labels
    # print(f"Correct {correct}")
    accuracy = correct.sum() / len(y_true)  # Calculate accuracy
    return accuracy.item() * 100  # Return accuracy as a percentage


# --------------------------------------------------------------------
# Train the Model
# --------------------------------------------------------------------

model = BinaryClassifier().to(device)
optimizer = optim.Adam(model.parameters(), lr=5e-3, weight_decay=5e-5)

def evaluate(input, output):
    # print(f"Evaluate \n{input.size()} \n{output.size()}\n")
    # Evaluation on training data
    model.eval()
    with torch.no_grad():
        train_logits = model(input).squeeze()
        train_accuracy = calculate_accuracy(output, train_logits)
        # print(f"Train_Logits \n {train_logits} \n Train_Accuracy \n {train_accuracy} \n")
    return train_accuracy

def train(model: nn.Module, data: torch.utils.data.DataLoader, optimizer: torch.optim.Optimizer):


    print("DATA", data)
    # Training loop

    # Loss function
    loss_fn = nn.BCEWithLogitsLoss()
    # Optimizer (using Adam)
    
    model.train()
    num_epochs = 10001
    # TODO add batch later

    X_train, y_train, X_test, y_test = data
    # X_train, y_train = data[0].to(device), data[1].to(device)
    # X_test, y_test = data[2].to(device), data[3].to(device)

    loss_array = []
    train_accuracies = []
    test_accuracies = []

    train_loss, train_acc = 0, 0


    for epoch in range(num_epochs):
        for batch, (X, y) in enumerate(data):
            X, y = X.to(device), y.to(device)

            # Forward pass
            outputs = model(X).squeeze()  # Squeeze the output to match target shape
            
            # Calculate and accumulate loss
            loss = loss_fn(outputs, y_train)
            loss_array.append(loss.item() * 100)
            train_loss += loss.item()
            
            # Optimizer zero grad
            optimizer.zero_grad()
        
            # Loss backward
            loss.backward()

            # Optimizer step
            optimizer.step()

            # Calculate and accumulate accuracy metric accross all batches
            y_pred_class = torch.argmax(torch.softmax(outputs, dim=1), dim=1)
            train_acc += (y_pred_class == y).sum().item()/len(outputs)

        # Adjust metrics to get average loss and accuracy per batch
        train_loss = train_loss / len(data)
        train_acc = train_acc / len(data)
        print(f"Train_Loss: {train_loss}\nTrain_ACC: {train_acc}")
        # return train_loss, train_acc
    
        # # Print training progress
        # if (epoch+1) % 100 == 0:
        #     print(f'Epoch [{epoch+1}/{num_epochs}], Loss: {loss.item():.4f}')

        # # Evaluation on training data
        
        # train_accuracy = evaluate(X_train, y_train)
        # test_accuracy = evaluate(X_test, y_test)

        # train_accuracies.append(train_accuracy)
        # test_accuracies.append(test_accuracy)
        
        # if (epoch+1) % 100 == 0:
        #     print(f'Epoch [{epoch+1}/{num_epochs}], Training Accuracy: {train_accuracy:.2f}%, Test Accuracy: {test_accuracy:.2f}%')
    
    # Save Model and Weights
    torch.save(model.state_dict(), './weights/model_weights.pth')
    # Plotting
    plt.figure(figsize=(10, 5), facecolor='#212f3d')
    plt.plot(train_accuracies, label='Training Accuracy')
    plt.plot(test_accuracies, label='Test Accuracy')
    plt.plot(loss_array, label='Loss')
    plt.xlabel('Epoch')
    plt.ylabel('Accuracy (%)')
    plt.title('Training and Test Accuracy')
    plt.legend()

    ax = plt.gca()
    ax.set_facecolor('#212f3d')
    plt.show()

    return

def load_weights(model: nn.Module):
    return model.load_state_dict(torch.load('./weights/model_weights.pth', map_location=device))
    


# --------------------------------------------------------------------
# ARG-Parse
# --------------------------------------------------------------------

# Create the parser
parser = argparse.ArgumentParser(description="A script to train a model or run inference")

# Add the 'train' argument
parser.add_argument('--train', action='store_true', help='Train the model')

# Add the 'inf' argument
parser.add_argument('--inf', action='store_true', help='Run inference on saved model')

# Parse the arguments
args = parser.parse_args()

def eval_inf(X, y):
    print(X, "\n", y)
    model.eval()
    with torch.no_grad():
        X = X.to(device)
        predictions = model(X).to(device).squeeze()
        print("Predictions", predictions)
        # for i in range(predictions[0]):
            # print(f"Prediction | {X[i]} | {y[i]} |")

        inf_accuracy = calculate_accuracy(y, predictions)
        print(f"INF ACCURACY \n {inf_accuracy}")
    
    # print(f"Predictions: {predictions}")




# Use the arguments in your script
if args.train:
    # Train the model
    print("TRAIN")
    test_data = data_loader.generate_data(10000)
    print(f"{test_data}")
    train(model=model, data=test_data, optimizer=optimizer)

if args.inf:
    # Run Inference
    print("Inference")
    X_train, y_train, X_test, y_test = data_loader.load_dataset("BTCUSD")
    loaded_model = load_weights(model)
    eval_inf( X_train, y_train)
    print("Model Loaded", model.state_dict())