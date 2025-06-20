# metrics.py
from nltk.translate.meteor_score import meteor_score
from rouge_score import rouge_scorer
from bert_score import score as bert_score
from nltk.translate.meteor_score import meteor_score
from nltk.tokenize import word_tokenize

def evaluate_meteor(pred: str, ref: str) -> float:
    return round(meteor_score([word_tokenize(ref)], word_tokenize(pred)), 4)

def evaluate_rouge(pred: str, ref: str):
    scorer = rouge_scorer.RougeScorer(['rougeL'], use_stemmer=True)
    scores = scorer.score(ref, pred)["rougeL"]
    return {
        "rougeL_precision": round(scores.precision, 4),
        "rougeL_recall": round(scores.recall, 4),
        "rougeL_f1": round(scores.fmeasure, 4)
    }

def evaluate_bertscore(pred: str, ref: str):
    P, R, F1 = bert_score([pred], [ref], lang="en", model_type="bert-base-uncased")
    return {
        "bert_precision": round(P.item(), 4),
        "bert_recall": round(R.item(), 4),
        "bert_f1": round(F1.item(), 4)
    }
