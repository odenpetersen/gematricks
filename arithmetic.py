import numpy as np
import time
import pandas as pd
import numpy.random as random
import os
from scipy import stats

def generate_question(history):
    if random.uniform(0,1)<.75:#1/(1+0.001*len(set(history['question']))):
        op = random.choice(list("+-*/"))
        if op in "+-":
            args = [random.randint(2,101),random.randint(2,101)]
            if op == '-':
                args = sorted(args,reverse=True)
        else:
            args = [random.randint(2,13),random.randint(2,101)]
            if op == '/':
                args = sorted(args)
        question = "%d%s%d" % (args[0],op,args[1])
        if op == "/":
            answer = args[1]
            args[1] = args[0]
            args[0] = eval("%s*%s" % (answer,args[1]))
            question = "%d/%d" % tuple(args)
        else:
            answer = eval(question)
    else:
        score = 1/(1+(history['user_input']/history['answer']).apply(lambda t : max(t,0)).apply(np.log).apply(np.abs))
        score += 1/(1+history['time'])
        score += 10*(history['user_input']==history['answer']).apply(int)
        score = score.apply(float).apply(np.log)
        aggregates = history.copy()
        aggregates['score']=score
        aggregates = aggregates[['question','answer','score']]
        aggregates = aggregates.groupby('question',as_index=False)
        aggregates = aggregates.mean()
        argmax = aggregates['score'].idxmin()
        question = aggregates['question'][argmax]
        answer = aggregates['answer'][argmax]
    return (question,float(answer))

def main():
    os.system('clear')
    history = pd.read_csv("history.csv")
    history.index.rename('',inplace=True)
    for col in ['answer','user_input','time']:
        history[col] = history[col].apply(float)
    user_input = ""
    (question,answer) = generate_question(history)
    while True:
        start = time.time()
        print(question)
        user_input = input()
        end = time.time()
        if user_input.lower() == "q":
            break
        else:
            user_input = int(user_input)
            os.system('clear')
            print(question)
            print(user_input)
            if user_input != answer:
                print("Wrong")
            else:
                print()
                tmp = question
                while question == tmp:
                    (question,answer) = generate_question(history)
            print()
            history = history.append({'question':question,'answer':answer,'user_input':user_input,'time':end-start},ignore_index=True)
        with open("history.csv","w") as f:
            history.to_csv(f,index=False)

if __name__=="__main__":
    main()
