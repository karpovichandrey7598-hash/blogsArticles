"""
Модуль штучного інтелекту для генерації резюме текстів.
Використовує Hugging Face Inference API для summarization.
"""
import os
from typing import Optional

import requests


class TextSummarizer:
    """
    Клас для генерації коротких резюме текстів за допомогою Hugging Face API.
    Використовує модель facebook/bart-large-cnn для англійської мови.
    """
    
    DEFAULT_MODEL = "facebook/bart-large-cnn"
    BASE_URL = "https://api-inference.huggingface.co/models"
    
    def __init__(self, api_token: Optional[str] = None, model: Optional[str] = None):
        """
        Ініціалізація summarizer.
        
        Args:
            api_token: Hugging Face API token (рекомендовано для стабільності)
            model: Назва моделі (за замовчуванням: facebook/bart-large-cnn)
        """
        self.api_token = api_token or os.getenv("HUGGINGFACE_API_TOKEN")
        self.model = model or os.getenv("HUGGINGFACE_MODEL", self.DEFAULT_MODEL)
        
        if not self.api_token and os.getenv("FLASK_ENV") == "production":
            print(
                "WARNING: HUGGINGFACE_API_TOKEN не вказано. "
                "API може працювати повільніше або з обмеженнями."
            )
    
    def summarize(
        self,
        text: str,
        max_length: int = 150,
        min_length: int = 50,
    ) -> Optional[str]:
        """
        Генерує коротке резюме тексту.
        
        Args:
            text: Вхідний текст для резюме
            max_length: Максимальна довжина резюме
            min_length: Мінімальна довжина резюме
            
        Returns:
            Резюме тексту або None у разі помилки
        """
        if not text or len(text.strip()) < 50:
            return None
        
        url = f"{self.BASE_URL}/{self.model}"
        
        headers = {}
        if self.api_token:
            headers["Authorization"] = f"Bearer {self.api_token}"
        
        payload = {
            "inputs": text,
            "parameters": {
                "max_length": max_length,
                "min_length": min_length,
                "do_sample": False,
            },
        }
        
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                if isinstance(result, list) and len(result) > 0:
                    summary = result[0].get("summary_text", "")
                    return summary.strip() if summary else None
                elif isinstance(result, dict) and "summary_text" in result:
                    return result["summary_text"].strip()
            elif response.status_code == 503:
                # Модель ще завантажується
                return None
            else:
                print(f"Hugging Face API error: {response.status_code} - {response.text}")
                return None
                
        except requests.exceptions.RequestException as e:
            print(f"Error calling Hugging Face API: {e}")
            return None
    
    def summarize_fallback(self, text: str, max_sentences: int = 3) -> str:
        """
        Просте резюме без ШІ (fallback метод).
        Використовується, якщо API недоступне.
        """
        if not text:
            return ""
        
        sentences = text.split(". ")
        if len(sentences) <= max_sentences:
            return text
        
        summary = ". ".join(sentences[:max_sentences])
        if not summary.endswith("."):
            summary += "."
        return summary


# Глобальний екземпляр
_summarizer_instance: Optional[TextSummarizer] = None


def get_summarizer() -> TextSummarizer:
    """Отримує або створює глобальний екземпляр summarizer."""
    global _summarizer_instance
    if _summarizer_instance is None:
        _summarizer_instance = TextSummarizer()
    return _summarizer_instance


def summarize_text(text: str, max_length: int = 150, min_length: int = 50) -> Optional[str]:
    """
    Зручна функція для генерації резюме.
    """
    summarizer = get_summarizer()
    summary = summarizer.summarize(text, max_length=max_length, min_length=min_length)
    
    # Якщо ШІ не спрацював, використовуємо fallback
    if summary is None and len(text) > 100:
        return summarizer.summarize_fallback(text)
    
    return summary

