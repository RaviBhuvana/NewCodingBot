import pandas as pd
data = pd.read_csv("/home/vectone/Downloads/data_for_entity.csv",encoding="latin1" )

data.head(30)

data =data.fillna(method ="ffill")

data.head(30)

from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

data["Sentence #"] = LabelEncoder().fit_transform(data["Sentence #"] )

data.head(30)

data.rename(columns={"Sentence #":"sentence_id","Word":"words","Tag":"labels"}, inplace =True)

data["labels"] = data["labels"].str.upper()

X= data[["sentence_id","words"]]
Y =data["labels"]

x_train, x_test, y_train, y_test = train_test_split(X,Y, test_size =0.2)

#building up train data and test data
train_data = pd.DataFrame({"sentence_id":x_train["sentence_id"],"words":x_train["words"],"labels":y_train})
test_data = pd.DataFrame({"sentence_id":x_test["sentence_id"],"words":x_test["words"],"labels":y_test})

train_data

from simpletransformers.ner import NERModel,NERArgs

label = data["labels"].unique().tolist()
label

args = NERArgs()
args.num_train_epochs = 5
args.learning_rate = 1e-4
args.overwrite_output_dir =True
args.train_batch_size = 16
args.eval_batch_size = 128

model = NERModel('bert', 'bert-base-cased',labels=label,args =args ,use_cuda=False)

import torch
model.train_model(train_data,eval_data = test_data,acc=accuracy_score)
torch.save(model, 'bhuvana.pth')

result, model_outputs, preds_list = model.eval_model(test_data)
result

import dateutil.parser

while True:
    user_input = input()
    prediction, model_output = model.predict([user_input])
    prediction = prediction[0]

    entities = []
    current_entity = ""
    current_label = ""

    for token_label_pair in prediction:
        token, predicted_label = list(token_label_pair.items())[0]
        if predicted_label != 'O':
            if current_label == predicted_label:
                current_entity += " " + token
            else:
                if current_entity:
                    if current_label == 'ADDRESS':
                        entities.append({current_entity: current_label})
                    elif current_label == 'DATE':
                        if entities and list(entities[-1].values())[0] == 'DATE':
                            last_entity = list(entities[-1].keys())[0]
                            current_entity = last_entity + " " + current_entity
                            entities[-1] = {current_entity: current_label}
                        else:
                            entities.append({current_entity: current_label})
                    else:
                        entity_parts = current_entity.split(",")
                        for part in entity_parts:
                            if part.strip():
                                entities.append({part.strip(): current_label})
                current_entity = token
                current_label = predicted_label
        else:
            if current_entity:
                if current_label == 'ADDRESS':
                    entities.append({current_entity: current_label})
                elif current_label == 'DATE':
                    if entities and list(entities[-1].values())[0] == 'DATE':
                        last_entity = list(entities[-1].keys())[0]
                        current_entity = last_entity + " " + current_entity
                        entities[-1] = {current_entity: current_label}
                    else:
                        entities.append({current_entity: current_label})
                else:
                    entity_parts = current_entity.split(",")
                    for part in entity_parts:
                        if part.strip():
                            entities.append({part.strip(): current_label})
                current_entity = ""
                current_label = ""

    if current_entity:
        if current_label == 'ADDRESS':
            entities.append({current_entity: current_label})
        elif current_label == 'DATE':
            if entities and list(entities[-1].values())[0] == 'DATE':
                last_entity = list(entities[-1].keys())[0]
                current_entity = last_entity + " " + current_entity
                entities[-1] = {current_entity: current_label}
            else:
                entities.append({current_entity: current_label})
        else:
            entity_parts = current_entity.split(",")
            for part in entity_parts:
                if part.strip():
                    entities.append({part.strip(): current_label})

    if entities:
        print(entities)