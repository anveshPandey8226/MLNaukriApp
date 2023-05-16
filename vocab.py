import pickle

with open('vocab.pkl', 'rb') as file:
    vocab = pickle.load(file)
    print(vocab)

vocab_t = vocab.pop(0)
print(vocab)

#Open a file and use dump()
with open('vocab_3.pkl', 'wb') as file:
    
    # A new file will be created
    pickle.dump(vocab, file)