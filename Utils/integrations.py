# Integraciones externas: Slack y Webhooks
import os
import json
import logging
from typing import List, Dict, Any

import requests

logger = logging.getLogger(__name__)

class SlackNotifier:
    def __init__(self, webhook_url: str | None = None):
        self.webhook_url = webhook_url or os.getenv('SLACK_WEBHOOK_URL')

    def is_configured(self) -> bool:
        return bool(self.webhook_url)

    def send_message(self, text: str, blocks: List[Dict[str, Any]] | None = None) -> bool:
        if not self.is_configured():
            logger.warning('Slack webhook no configurado')
            return False
        try:
            payload = {'text': text}
            if blocks:
                payload['blocks'] = blocks
            resp = requests.post(self.webhook_url, data=json.dumps(payload), headers={'Content-Type': 'application/json'}, timeout=10)
            if resp.status_code >= 200 and resp.status_code < 300:
                return True
            logger.error(f'Error Slack {resp.status_code}: {resp.text}')
            return False
        except Exception as e:
            logger.error(f'Excepción enviando Slack: {e}')
            return False

class WebhookPublisher:
    def __init__(self, urls: List[str] | None = None):
        urls_env = os.getenv('WEBHOOK_URLS', '')
        self.urls = urls or [u.strip() for u in urls_env.split(',') if u.strip()]

    def publish(self, event_type: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        results = {}
        for url in self.urls:
            try:
                resp = requests.post(url, json={'event_type': event_type, 'payload': payload}, timeout=10)
                results[url] = {'status': resp.status_code}
            except Exception as e:
                results[url] = {'error': str(e)}
        return results

slack_notifier = SlackNotifier()
webhook_publisher = WebhookPublisher()

# Telegram
class TelegramNotifier:
    def __init__(self, bot_token: str | None = None, chat_id: str | None = None):
        self.bot_token = bot_token or os.getenv('TELEGRAM_BOT_TOKEN')
        self.chat_id = chat_id or os.getenv('TELEGRAM_CHAT_ID')

    def is_configured(self) -> bool:
        return bool(self.bot_token and self.chat_id)

    def send_message(self, text: str) -> bool:
        if not self.is_configured():
            logger.warning('Telegram no configurado')
            return False
        try:
            url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
            resp = requests.post(url, json={"chat_id": self.chat_id, "text": text}, timeout=10)
            return 200 <= resp.status_code < 300
        except Exception as e:
            logger.error(f'Excepción enviando Telegram: {e}')
            return False

telegram_notifier = TelegramNotifier()
