import asyncio
import logging
from typing import Optional
from telethon import TelegramClient
from telethon.sessions import StringSession
from telethon.errors import (
    SessionPasswordNeededError, 
    PhoneCodeInvalidError,
    PhoneNumberInvalidError,
    FloodWaitError
)
from database import get_userbot_settings, save_userbot_settings
from config import USERBOT_RECONNECT_INTERVAL

logger = logging.getLogger(__name__)


class UserbotClient:
    """Telethon userbot client for sending verification codes"""
    
    def __init__(self):
        self.client: Optional[TelegramClient] = None
        self.api_id: Optional[int] = None
        self.api_hash: Optional[str] = None
        self.phone: Optional[str] = None
        self.session_string: Optional[str] = None
        self.is_running = False
        self._reconnect_task = None
        
    async def initialize(self) -> bool:
        """Initialize userbot from database settings"""
        try:
            settings = get_userbot_settings()
            
            if not settings:
                logger.warning("No userbot settings found in database")
                return False
                
            self.api_id = settings['api_id']
            self.api_hash = settings['api_hash']
            self.phone = settings['phone']
            self.session_string = settings.get('session_string')
            
            if not self.api_id or not self.api_hash or not self.phone:
                logger.error("Incomplete userbot settings")
                return False
            
            # Create client with session string if available
            if self.session_string:
                session = StringSession(self.session_string)
            else:
                session = StringSession()
            
            self.client = TelegramClient(
                session,
                self.api_id,
                self.api_hash,
                connection_retries=5,
                retry_delay=1,
                auto_reconnect=True
            )
            
            await self.client.connect()
            
            # Check if authorized
            if not await self.client.is_user_authorized():
                logger.warning("Userbot not authorized, requires login")
                return False
            
            # Save session string if not already saved
            if not self.session_string:
                self.session_string = self.client.session.save()
                save_userbot_settings(
                    self.api_id, 
                    self.api_hash, 
                    self.phone, 
                    self.session_string
                )
                logger.info("Userbot session saved to database")
            
            self.is_running = True
            logger.info(f"Userbot initialized successfully for {self.phone}")
            
            # Start auto-reconnect monitoring
            self._reconnect_task = asyncio.create_task(self._monitor_connection())
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize userbot: {e}")
            return False
    
    async def login(self, api_id: int, api_hash: str, phone: str, 
                   code: str = None, password: str = None) -> dict:
        """
        Login userbot with phone number
        Returns dict with status and message
        """
        try:
            self.api_id = api_id
            self.api_hash = api_hash
            self.phone = phone
            
            session = StringSession()
            self.client = TelegramClient(session, api_id, api_hash)
            
            await self.client.connect()
            
            # Send code if not provided
            if not code:
                await self.client.send_code_request(phone)
                return {
                    'status': 'code_sent',
                    'message': 'Verification code sent to Telegram'
                }
            
            # Sign in with code
            try:
                await self.client.sign_in(phone, code)
                
                # Save session
                self.session_string = self.client.session.save()
                save_userbot_settings(api_id, api_hash, phone, self.session_string)
                
                self.is_running = True
                logger.info("Userbot logged in successfully")
                
                # Start auto-reconnect monitoring
                self._reconnect_task = asyncio.create_task(self._monitor_connection())
                
                return {
                    'status': 'success',
                    'message': 'Userbot logged in successfully'
                }
                
            except SessionPasswordNeededError:
                # 2FA enabled
                if password:
                    await self.client.sign_in(password=password)
                    
                    # Save session
                    self.session_string = self.client.session.save()
                    save_userbot_settings(api_id, api_hash, phone, self.session_string)
                    
                    self.is_running = True
                    logger.info("Userbot logged in successfully with 2FA")
                    
                    # Start auto-reconnect monitoring
                    self._reconnect_task = asyncio.create_task(self._monitor_connection())
                    
                    return {
                        'status': 'success',
                        'message': 'Userbot logged in successfully'
                    }
                else:
                    return {
                        'status': 'password_required',
                        'message': '2FA password required'
                    }
                    
        except PhoneCodeInvalidError:
            return {
                'status': 'error',
                'message': 'Invalid verification code'
            }
        except PhoneNumberInvalidError:
            return {
                'status': 'error',
                'message': 'Invalid phone number'
            }
        except FloodWaitError as e:
            return {
                'status': 'error',
                'message': f'Too many attempts. Try again in {e.seconds} seconds'
            }
        except Exception as e:
            logger.error(f"Login error: {e}")
            return {
                'status': 'error',
                'message': str(e)
            }
    
    async def send_verification_code(self, phone: str, code: str, language: str = 'ru') -> bool:
        """Send verification code via Telegram"""
        if not self.client or not self.is_running:
            logger.error("Userbot not initialized or not running")
            return False
        
        try:
            # Format phone number
            if not phone.startswith('+'):
                phone = '+' + phone
            
            # Create message in specified language
            messages = {
                'uz': f"🔐 Tasdiqlash kodi: {code}\n\n"
                      f"Bu kodni hech kimga bermang!\n"
                      f"Kod 5 daqiqa amal qiladi.",
                'ru': f"🔐 Ваш код подтверждения: {code}\n\n"
                      f"Не сообщайте этот код никому!\n"
                      f"Код действителен 5 минут."
            }
            message = messages.get(language, messages['ru'])
            
            # Send message
            await self.client.send_message(phone, message)
            logger.info(f"Verification code sent to {phone}")
            return True
            
        except FloodWaitError as e:
            logger.error(f"Flood wait error: need to wait {e.seconds} seconds")
            return False
        except Exception as e:
            logger.error(f"Failed to send verification code: {e}")
            return False
    
    async def _monitor_connection(self):
        """Monitor connection and auto-reconnect if needed"""
        while self.is_running:
            try:
                await asyncio.sleep(USERBOT_RECONNECT_INTERVAL)
                
                if self.client and not self.client.is_connected():
                    logger.warning("Userbot disconnected, attempting to reconnect...")
                    try:
                        await self.client.connect()
                        logger.info("Userbot reconnected successfully")
                    except Exception as e:
                        logger.error(f"Reconnection failed: {e}")
                        
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Connection monitor error: {e}")
    
    async def disconnect(self):
        """Disconnect userbot"""
        try:
            self.is_running = False
            
            # Cancel reconnect task
            if self._reconnect_task:
                self._reconnect_task.cancel()
                try:
                    await self._reconnect_task
                except asyncio.CancelledError:
                    pass
            
            # Disconnect client
            if self.client:
                await self.client.disconnect()
            
            logger.info("Userbot disconnected")
            
        except Exception as e:
            logger.error(f"Error disconnecting userbot: {e}")
    
    def is_active(self) -> bool:
        """Check if userbot is active and connected"""
        return (
            self.is_running and 
            self.client is not None and 
            self.client.is_connected()
        )


# Global userbot instance
userbot = UserbotClient()


async def get_userbot() -> UserbotClient:
    """Get or initialize global userbot instance"""
    if not userbot.is_active():
        await userbot.initialize()
    return userbot
