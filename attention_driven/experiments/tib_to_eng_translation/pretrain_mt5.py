from transformers import TrainingArguments
from transformers.tokenization_utils import PreTrainedTokenizer

from datasets import DatasetDict, concatenate_datasets

from attention_driven.data_processors.pretrain import PretrainDataProcessor
from attention_driven.experiments.model_mixins.mt5_model_mixins import MT5Base580MModelMixin, MT5Large1_2BModelMixin
from attention_driven.experiments.tib_to_eng_translation.tib_zh_eng_pretrain_mixin import TibZhEngPretrainExperimentMixin
from attention_driven.experiments.training_pipelines import PretrainExperimentBase
from attention_driven.modeling.t5_span_mlm import (
    compute_input_and_target_lengths, get_group_texts_fn
)


class PretrainMT5TestExperiment(MT5Base580MModelMixin, TibZhEngPretrainExperimentMixin, PretrainExperimentBase):
    """
    This is just a dummy experiment to test if the pretraining process actually works.
    """

    # This is an exact copy of `TibZhEngPretrainExperimentMixin.get_pretrain_dataset` unless specified otherwise
    def get_pretrain_dataset(self, tokenizer: PreTrainedTokenizer, pretrain_training_arguments: TrainingArguments) -> DatasetDict:
        max_input_length = self.MAX_INPUT_LENGTH
        mlm_probability = self.MLM_PROBABILITY
        mean_noise_span_length = self.MEAN_NOISE_SPAN_LENGTH

        # T5-like span masked language modeling will fuse consecutively masked tokens to a single sentinel token.
        # To ensure that the input length is `max_seq_length`, we need to increase the maximum length
        # according to `mlm_probability` and `mean_noise_span_length`. We can also define the label length accordingly.
        expanded_inputs_length, targets_length = compute_input_and_target_lengths(
            inputs_length=max_input_length,
            noise_density=mlm_probability,
            mean_noise_span_length=mean_noise_span_length,
        )
        self.TARGETS_LENGTH = targets_length
        group_texts = get_group_texts_fn(expanded_inputs_length)

        dataset_dict = PretrainDataProcessor()(pretrain_training_arguments)

        ###############################
        # START reduce dataset size for test experiment
        ###############################

        for key in dataset_dict:
            dataset_dict[key] = dataset_dict[key].select(range(10000))

        ###############################
        # END reduce dataset size for test experiment
        ###############################

        def tokenize_fn(examples):
            return tokenizer(examples["text"])

        with pretrain_training_arguments.main_process_first(desc="Mapping dataset"):
            tokenized_grouped_dataset_dict = dataset_dict \
                .map(tokenize_fn, batched=True, remove_columns=["text"]) \
                .map(group_texts, batched=True, remove_columns=["attention_mask"])

            tokenized_group_dataset = concatenate_datasets(list(tokenized_grouped_dataset_dict.values()))

            shuffled_tokenized_grouped_dataset = tokenized_group_dataset.shuffle(seed=42)

            pretrain_dataset = DatasetDict({"train": shuffled_tokenized_grouped_dataset})

        return pretrain_dataset

    def get_pretrain_training_arguments(self, batch_size: int) -> TrainingArguments:
        pretrain_training_arguments = super().get_pretrain_training_arguments(batch_size)

        pretrain_training_arguments.max_steps = 10

        return pretrain_training_arguments

    def get_finetune_training_arguments(self, batch_size: int, learning_rate: float) -> TrainingArguments:
        finetune_training_arguments = super().get_finetune_training_arguments(batch_size, learning_rate)

        finetune_training_arguments.max_steps = 10

        return finetune_training_arguments


class PretrainMT5Base580MExperiment(MT5Base580MModelMixin, TibZhEngPretrainExperimentMixin, PretrainExperimentBase):
    pass


class PretrainMT5Large1_2BExperiment(MT5Large1_2BModelMixin, TibZhEngPretrainExperimentMixin, PretrainExperimentBase):
    pass