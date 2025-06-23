# metrics.py
from nltk.translate.meteor_score import meteor_score
from rouge_score import rouge_scorer
from bert_score import score as bert_score
from nltk.translate.meteor_score import meteor_score
from nltk.tokenize import word_tokenize
from nltk.translate.meteor_score import meteor_score
from nltk.tokenize import word_tokenize
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
from typing import List, Dict
import numpy as np

# def evaluate_meteor(pred: str, ref: str) -> float:
#     return round(meteor_score([word_tokenize(ref)], word_tokenize(pred)), 4)
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
        "bert_precision": round(P[0].item(), 4),
        "bert_recall": round(R[0].item(), 4),
        "bert_f1": round(F1[0].item(), 4)
    }



def evaluate_character_descriptions(generated: List[Dict[str, str]], reference: List[Dict[str, str]]) -> Dict[str, float]:
    """
    Evaluate character descriptions by matching names and comparing text descriptions.
    Calculates METEOR, ROUGE-L (simplified), and Cosine Similarity.

    Parameters:
    - generated: list of dicts with "name" and "description" from model
    - reference: list of dicts with "name" and "description" from test case

    Returns:
    - Dictionary with average meteor, rougeL_f1, cosine_sim
    """
    gen_map = {c["name"]: c["description"] for c in generated}
    ref_map = {c["name"]: c["description"] for c in reference}

    common_names = set(gen_map.keys()) & set(ref_map.keys())
    if not common_names:
        return {"meteor": 0.0, "rougeL_f1": 0.0, "cosine_sim": 0.0}

    meteor_scores = []
    rouge_scores = []
    cosine_scores = []

    for name in common_names:
        pred = gen_map[name]
        ref = ref_map[name]

        meteor = meteor_score([word_tokenize(ref)], word_tokenize(pred))

        # Simple ROUGE-L: based on longest common subsequence length
        def lcs(X, Y):
            m, n = len(X), len(Y)
            L = [[0]*(n+1) for _ in range(m+1)]
            for i in range(m):
                for j in range(n):
                    if X[i] == Y[j]:
                        L[i+1][j+1] = L[i][j] + 1
                    else:
                        L[i+1][j+1] = max(L[i+1][j], L[i][j+1])
            return L[m][n]

        pred_tokens = word_tokenize(pred)
        ref_tokens = word_tokenize(ref)
        lcs_len = lcs(pred_tokens, ref_tokens)
        rouge_l = 2 * lcs_len / (len(pred_tokens) + len(ref_tokens))

        # Cosine similarity
        vectorizer = TfidfVectorizer().fit([pred, ref])
        vecs = vectorizer.transform([pred, ref])
        cosine = cosine_similarity(vecs[0], vecs[1])[0][0]

        meteor_scores.append(meteor)
        rouge_scores.append(rouge_l)
        cosine_scores.append(cosine)

    return {
        "meteor": round(np.mean(meteor_scores), 4),
        "rougeL_f1": round(np.mean(rouge_scores), 4),
        "cosine_sim": round(np.mean(cosine_scores), 4)
    }