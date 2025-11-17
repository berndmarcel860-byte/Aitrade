"""
Telegram Notification Module
Sends professional trading signals to Telegram
"""
import asyncio
from telegram import Bot
from telegram.error import TelegramError
import config


class TelegramNotifier:
    """Send formatted trading signals to Telegram"""
    
    def __init__(self):
        """Initialize Telegram bot"""
        self.bot_token = config.TELEGRAM_BOT_TOKEN
        self.chat_id = config.TELEGRAM_CHAT_ID
        self.bot = None
        
        if self.bot_token and self.chat_id:
            self.bot = Bot(token=self.bot_token)
    
    def format_signal_message(self, signal, symbol):
        """
        Format trading signal into professional Telegram message
        
        Args:
            signal: Dict with trading signal information
            symbol: Trading pair symbol
            
        Returns:
            str: Formatted message
        """
        direction_emoji = "🟢" if signal['direction'] == 'LONG' else "🔴"
        trend_emoji = "📈" if signal['trend'] == 'UPTREND' else "📉" if signal['trend'] == 'DOWNTREND' else "➡️"
        
        message = f"""
{direction_emoji} 𝗣𝗥𝗢𝗙𝗘𝗦𝗦𝗜𝗢𝗡𝗔𝗟 𝗧𝗥𝗔𝗗𝗜𝗡𝗚 𝗦𝗜𝗚𝗡𝗔𝗟 {direction_emoji}

━━━━━━━━━━━━━━━━━━━━━━━━
📊 𝗦𝘆𝗺𝗯𝗼𝗹: {symbol}
{direction_emoji} 𝗗𝗶𝗿𝗲𝗰𝘁𝗶𝗼𝗻: {signal['direction']}
{trend_emoji} 𝗧𝗿𝗲𝗻𝗱: {signal['trend']}
━━━━━━━━━━━━━━━━━━━━━━━━

💰 𝗣𝗥𝗜𝗖𝗘 𝗜𝗡𝗙𝗢𝗥𝗠𝗔𝗧𝗜𝗢𝗡:
💵 Current Price: ${signal['current_price']}
🎯 Entry Range: ${signal['entry_range']}

━━━━━━━━━━━━━━━━━━━━━━━━

🎯 𝗧𝗔𝗞𝗘 𝗣𝗥𝗢𝗙𝗜𝗧 𝗧𝗔𝗥𝗚𝗘𝗧𝗦:
{signal['take_profit']}

🛡️ 𝗦𝗧𝗢𝗣 𝗟𝗢𝗦𝗦:
${signal['stop_loss']}

━━━━━━━━━━━━━━━━━━━━━━━━

💼 𝗣𝗢𝗦𝗜𝗧𝗜𝗢𝗡 𝗗𝗘𝗧𝗔𝗜𝗟𝗦:
⚡ Leverage: {signal['leverage']}x
💵 Position Size: ${signal['position_size']} USDT
📊 Risk/Reward: {signal['risk_reward']['rr_ratio']}:1

━━━━━━━━━━━━━━━━━━━━━━━━

📈 𝗧𝗘𝗖𝗛𝗡𝗜𝗖𝗔𝗟 𝗔𝗡𝗔𝗟𝗬𝗦𝗜𝗦:
🔹 RSI: {signal['rsi']}
🔹 MACD: {signal['macd']['value']} (Signal: {signal['macd']['signal']})
🔹 MACD Histogram: {signal['macd']['histogram']}
🔹 Volatility: {signal['volatility']['status']} ({signal['volatility']['atr_percentage']:.2f}%)

━━━━━━━━━━━━━━━━━━━━━━━━

⚠️ 𝗥𝗜𝗦𝗞 𝗠𝗔𝗡𝗔𝗚𝗘𝗠𝗘𝗡𝗧:
• Risk Amount: ${signal['risk_reward']['risk']}
• Potential Reward: ${signal['risk_reward']['reward']}
• Always use Stop Loss
• Never risk more than 2% of capital

━━━━━━━━━━━━━━━━━━━━━━━━
⏰ Signal Generated: {self._get_timestamp()}
🤖 AI Trading Bot v1.0
"""
        return message
    
    def _get_timestamp(self):
        """Get current timestamp formatted"""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")
    
    async def send_signal_async(self, signal, symbol):
        """
        Send signal message to Telegram asynchronously
        
        Args:
            signal: Trading signal dict
            symbol: Trading pair symbol
            
        Returns:
            bool: True if sent successfully, False otherwise
        """
        if not self.bot:
            print("⚠️  Telegram bot not configured. Printing signal instead:")
            print(self.format_signal_message(signal, symbol))
            return False
        
        try:
            message = self.format_signal_message(signal, symbol)
            await self.bot.send_message(
                chat_id=self.chat_id,
                text=message,
                parse_mode='HTML'
            )
            print(f"✅ Signal sent to Telegram successfully!")
            return True
        except TelegramError as e:
            print(f"❌ Failed to send Telegram message: {e}")
            print(self.format_signal_message(signal, symbol))
            return False
        except Exception as e:
            print(f"❌ Unexpected error sending message: {e}")
            return False
    
    def send_signal(self, signal, symbol):
        """
        Synchronous wrapper for sending signals
        
        Args:
            signal: Trading signal dict
            symbol: Trading pair symbol
            
        Returns:
            bool: True if sent successfully, False otherwise
        """
        return asyncio.run(self.send_signal_async(signal, symbol))
    
    async def send_error_alert_async(self, error_message):
        """
        Send error alert to Telegram
        
        Args:
            error_message: Error description
        """
        if not self.bot:
            print(f"⚠️  ERROR: {error_message}")
            return
        
        try:
            message = f"🚨 𝗧𝗥𝗔𝗗𝗜𝗡𝗚 𝗕𝗢𝗧 𝗔𝗟𝗘𝗥𝗧\n\n❌ {error_message}\n\n⏰ {self._get_timestamp()}"
            await self.bot.send_message(
                chat_id=self.chat_id,
                text=message
            )
        except Exception as e:
            print(f"❌ Failed to send error alert: {e}")
    
    def send_error_alert(self, error_message):
        """Synchronous wrapper for sending error alerts"""
        return asyncio.run(self.send_error_alert_async(error_message))
