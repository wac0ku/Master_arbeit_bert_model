# load_model.py
import os
import gc
import time
import logging
import psutil
from typing import Optional
from transformers import pipeline, AutoModelForSeq2SeqLM, AutoTokenizer
from logging_progress import setup_logger
from accelerate import init_empty_weights, load_checkpoint_and_dispatch

logger = setup_logger("load_model")

class ModelManager:
    """Singleton-Klasse zur Memory-sicheren Modellverwaltung"""
    _instance = None
    MEMORY_THRESHOLD = 0.85  # 85% RAM-Auslastung als kritisch

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._model = None
            cls._instance._tokenizer = None
        return cls._instance

    @property
    def memory_usage(self) -> float:
        return psutil.virtual_memory().percent / 100

    def _check_memory(self):
        """Prüft Systemspeicher vor Modellladen"""
        if self.memory_usage > self.MEMORY_THRESHOLD:
            raise MemoryError(f"Memory usage exceeds {self.MEMORY_THRESHOLD*100}%")

    def _clear_cuda_cache(self):
        """Räumt GPU-Speicher gründlich auf"""
        if 'cuda' in str(self._model.device):
            import torch
            torch.cuda.empty_cache()
            torch.cuda.reset_peak_memory_stats()
            gc.collect()

    def load_model(self, model_name: str = "facebook/bart-large-cnn") -> Optional[pipeline]:
        """Lädt Modell mit Memory-Protection und Retry-Mechanismus"""
        if self._model:
            return self._model

        max_retries = 3
        model_path = os.path.join("models", model_name.replace("/", "_"))

        for attempt in range(max_retries):
            try:
                self._check_memory()
                logger.info(f"Memory check passed ({self.memory_usage:.1%} used)")

                if os.path.exists(model_path):
                    logger.info(f"Loading model from cache: {model_path}")
                    return self._load_cached_model(model_path)

                logger.info(f"Downloading model: {model_name}")
                self._download_and_cache_model(model_name, model_path)
                return self._load_cached_model(model_path)

            except MemoryError as e:
                logger.warning(f"Memory error (attempt {attempt+1}): {e}")
                self.unload_model()
                time.sleep(5 * (attempt + 1))
            except Exception as e:
                logger.error(f"Loading failed: {e}")
                break

        return None

    def _download_and_cache_model(self, model_name: str, save_path: str):
        """Lädt Modell mit optimiertem Memory-Handling"""
        try:
            with init_empty_weights():
                config = AutoModelForSeq2SeqLM.from_pretrained(model_name).config

            self._model = load_checkpoint_and_dispatch(
                AutoModelForSeq2SeqLM.from_config(config),
                model_name,
                device_map="auto"
            )
            self._tokenizer = AutoTokenizer.from_pretrained(model_name)

            self._model.save_pretrained(save_path)
            self._tokenizer.save_pretrained(save_path)
            logger.info(f"Model saved to {save_path}")

        except Exception as e:
            logger.error(f"Model download failed: {e}")
            raise

    def _load_cached_model(self, model_path: str) -> pipeline:
        """Lädt lokal gespeichertes Modell mit Memory-Optimierung"""
        try:
            self._tokenizer = AutoTokenizer.from_pretrained(model_path)
            self._model = AutoModelForSeq2SeqLM.from_pretrained(
                model_path,
                device_map="auto",
                low_cpu_mem_usage=True
            )

            summarizer = pipeline(
                "summarization",
                model=self._model,
                tokenizer=self._tokenizer,
                framework="pt",
                device=self._model.device
            )

            logger.info(f"Model loaded successfully on {summarizer.device}")
            return summarizer

        except Exception as e:
            logger.error(f"Error loading cached model: {e}")
            self.unload_model()
            raise

    def unload_model(self):
        """Gibt Modellspeicher explizit frei"""
        if self._model:
            del self._model
            del self._tokenizer
            self._model = None
            self._tokenizer = None

        self._clear_cuda_cache()
        gc.collect()
        logger.info("Model memory released")

    def __del__(self):
        """Destruktor für automatische Bereinigung"""
        self.unload_model()

def summarize_text(text: str, summarizer: pipeline, **kwargs) -> Optional[str]:
    """Textzusammenfassung mit Memory-Überwachung"""
    try:
        if not text.strip():
            logger.error("Empty input text")
            return None

        if len(text) < 50:
            logger.warning("Input text too short")
            return text

        logger.info(f"Summarizing text ({len(text)} chars)")
        result = summarizer(
            text,
            max_length=kwargs.get('max_length', 130),
            min_length=kwargs.get('min_length', 30),
            num_beams=4,
            early_stopping=True,
            truncation=True
        )

        return result[0]['summary_text'] if result else None

    except Exception as e:
        logger.error(f"Summarization failed: {e}")
        return None