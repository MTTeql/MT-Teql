from allennlp.predictors.predictor import Predictor
import allennlp_models.structured_prediction
import spacy

spacy_nlp = spacy.load("en_core_web_sm")
predictor = Predictor.from_path("https://storage.googleapis.com/allennlp-public-models/biaffine-dependency-parser-ptb-2020.04.06.tar.gz")

def dependency_parsing(sentence:str):
    return predictor.predict(sentence=sentence)

def spacy_doc(sentence:str):
    return spacy_nlp(sentence)
