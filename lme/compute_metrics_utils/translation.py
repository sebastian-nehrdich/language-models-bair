from typing import Any, Callable, Dict

import evaluate

from transformers.tokenization_utils import PreTrainedTokenizerBase


__all__ = ["get_translation_compute_metrics"]


def get_translation_compute_metrics(tokenizer: PreTrainedTokenizerBase) -> Callable:
    chrf = evaluate.load("chrf")
    bleu = evaluate.load("bleu")

    def compute_metrics(eval_preds):
        logits, label_ids = eval_preds
        label_ids[label_ids == -100] = tokenizer.pad_token_id

        references = tokenizer.batch_decode(label_ids, skip_special_tokens=True)
        predictions = tokenizer.batch_decode(logits, skip_special_tokens=True)

        chrf_metrics = chrf.compute(
            predictions=predictions,
            references=references,
            word_order=2,    
        )

        for reference, prediction in zip(references, predictions):
            print("R: ", reference, "\nP: ", prediction)

        bleu_metrics = bleu.compute(predictions=predictions, references=references)

        # Remove the "bleu" value and call is score
        # The original bleu score is from 0 to 1, but we scale it up to 0 to 100
        bleu_metrics["score"] = bleu_metrics["bleu"] * 100
        del bleu_metrics["bleu"]

        print("CHRF", chrf_metrics)
        print("BLEU", bleu_metrics)

        def prepend_to_keys(d: Dict[str, Any], prefix: str) -> Dict[str, Any]:
            return {f"{prefix}_{k}": v for k, v in d.items()}

        return {
            **prepend_to_keys(chrf_metrics, "chrf"),
            **prepend_to_keys(bleu_metrics, "bleu"),
        }

    return compute_metrics
