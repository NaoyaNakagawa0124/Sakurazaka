# custom_pipeline.py

from transformers import TextClassificationPipeline
from typing import Any, Dict, List, Optional, Tuple

class CustomTextClassificationPipeline(TextClassificationPipeline):
    def _sanitize_parameters(
        self,
        task: str,
        **kwargs
    ) -> Tuple[Dict[str, Any], Dict[str, Any], Dict[str, Any]]:
        """
        Override the _sanitize_parameters method to modify tokenizer_kwargs.
        """
        tokenizer_kwargs = kwargs.pop("tokenizer_kwargs", {})
        tokenizer_kwargs['return_token_type_ids'] = False
        kwargs["tokenizer_kwargs"] = tokenizer_kwargs
        return super()._sanitize_parameters(task, **kwargs)

    def preprocess(self, text: str, **kwargs) -> Dict[str, Any]:
        """
        Preprocess the input text by tokenizing it.
        """
        return self.tokenizer(text, **kwargs)

    def _forward(self, model_inputs: Dict[str, Any], **kwargs) -> Any:
        """
        Forward pass: Remove 'token_type_ids' if present and pass inputs to the model.
        """
        if 'token_type_ids' in model_inputs:
            del model_inputs['token_type_ids']
        return self.model(**model_inputs)

    def postprocess(self, model_outputs: Any, **kwargs) -> List[Dict[str, Any]]:
        """
        Postprocess the model outputs.
        """
        return self.task.postprocess(model_outputs, **kwargs)
