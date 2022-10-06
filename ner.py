# %%
from transformers import AutoTokenizer, AutoModelForTokenClassification
from transformers import pipeline

tokenizer = AutoTokenizer.from_pretrained("dslim/bert-base-NER")
base_model = AutoModelForTokenClassification.from_pretrained("dslim/bert-base-NER")

ner_model = pipeline("ner", model=base_model, tokenizer=tokenizer)

# %%
# example = "Narendra Modi to visit Guwahati on the eve of Friday."

# ner_results = nlp(example)
# print(ner_results)

# %%
def return_named_entities(sentence):
    ner_results = ner_model(sentence)
    named_entities_idx = set()
    word_list = sentence.split()
    charidx_to_wordidx_map = {}
    
    char_idx = 0
    word_idx = 0
    for word in word_list:
        for _ in word:
            charidx_to_wordidx_map[char_idx] = word_idx
            char_idx += 1
        
        word_idx += 1
        char_idx += 1

    for ner in ner_results:
        start_char_idx = ner['start']
        if start_char_idx in charidx_to_wordidx_map:
            word_idx = charidx_to_wordidx_map[start_char_idx]
            named_entities_idx.add(word_idx)

    named_entities = []
    for idx in named_entities_idx:
        if (idx < len(word_list) and idx >= 0):
            named_entities.append(word_list[idx])

    
    return named_entities

# %%



