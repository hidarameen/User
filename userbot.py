"""
Telegram Userbot - Core forwarding functionality with Concurrent Task Support
"""

import asyncio
import configparser
import logging
import os
import json
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from telethon import TelegramClient, events
from telethon.errors import (
    FloodWaitError, 
    ChatWriteForbiddenError, 
    MessageNotModifiedError,
    RPCError
)
from telethon.tl.types import (
    MessageMediaPhoto, 
    MessageMediaDocument
)
from utils import ConfigManager, RateLimiter
from stats_manager import StatsManager

# Initialize global stats manager
stats_manager = StatsManager()

@dataclass
class SteeringTaskConfig:
    """Configuration for a single steering task"""
    task_id: str
    name: str
    source_chat: str
    target_chat: str
    enabled: bool = True
    forward_delay: float = 1.0
    max_retries: int = 3
    forward_mode: str = 'copy'  # 'forward' or 'copy'
    
    # Message type filters
    forward_text: bool = True
    forward_photos: bool = True
    forward_videos: bool = True
    forward_music: bool = True
    forward_audio: bool = True
    forward_voice: bool = True
    forward_video_messages: bool = True
    forward_files: bool = True
    forward_links: bool = True
    forward_gifs: bool = True
    forward_contacts: bool = True
    forward_locations: bool = True
    forward_polls: bool = True
    forward_stickers: bool = True
    forward_round: bool = True
    forward_games: bool = True
    
    # Text processing
    header_enabled: bool = False
    footer_enabled: bool = False
    header_text: str = ''
    footer_text: str = ''
    
    # Content filtering
    blacklist_enabled: bool = False
    whitelist_enabled: bool = False
    blacklist_words: str = ''
    whitelist_words: str = ''
    
    # Text cleaning
    clean_links: bool = False
    clean_buttons: bool = False
    clean_hashtags: bool = False
    clean_formatting: bool = False
    clean_empty_lines: bool = False
    clean_lines_with_words: bool = False
    clean_words_list: str = ''
    
    # Custom buttons
    buttons_enabled: bool = False
    button1_text: str = ''
    button1_url: str = ''
    button2_text: str = ''
    button2_url: str = ''
    button3_text: str = ''
    button3_url: str = ''
    
    # Text replacement
    replacer_enabled: bool = False
    replacements: str = ''
    

    # Advanced filters - Language Filter
    language_filter_enabled: bool = False
    language_filter_type: str = 'allow'  # 'allow' or 'block'
    allowed_languages: str = ''
    blocked_languages: str = ''
    
    # Advanced filters - Link Filter
    link_filter_enabled: bool = False
    allow_telegram_links: bool = True
    allow_external_links: bool = True
    allowed_domains: str = ''
    blocked_domains: str = ''
    
    # Advanced filters - Forwarded Message Filter
    forwarded_filter_enabled: bool = False
    
    # Advanced filters - User Filter
    user_filter_enabled: bool = False
    user_filter_type: str = 'allow'  # 'allow' or 'block'
    allowed_users: str = ''
    blocked_users: str = ''
    
    # ===== الوظائف المتقدمة الجديدة =====
    
    # Language Filter
    language_filter_enabled: bool = False
    language_filter_type: str = 'allow'  # 'allow' or 'block'
    allowed_languages: str = ''  # comma-separated language codes
    blocked_languages: str = ''  # comma-separated language codes
    
    # Link Filter
    link_filter_enabled: bool = False
    allow_telegram_links: bool = True
    allow_external_links: bool = True
    allowed_domains: str = ''  # comma-separated domains
    blocked_domains: str = ''  # comma-separated domains
    
    # Forwarded Messages Filter
    forwarded_filter_enabled: bool = False
    
    # Character Limit Filter
    
    char_limit_enabled: bool = False
    min_chars: int = 0
    max_chars: int = 4096
    

    # Advanced filters - Duplicate Filter
    duplicate_filter_enabled: bool = False
    duplicate_check_period: int = 24  # hours
    similarity_threshold: int = 90  # percentage
    
    # Message Formatting
    message_formatting_enabled: bool = False
    message_format: str = 'original'  # original, regular, bold, italic, underline, strike, code, mono, quote, spoiler, hyperlink
    message_formats: str = ''  # comma-separated list of formats for multiple formatting
    custom_spoiler_url: str = ''  # Custom URL for spoiler formatting
    custom_hyperlink_url: str = ''  # Custom URL for hyperlink formatting
    clean_original_formatting: bool = True  # Clean original formatting before applying new ones
    
    # Admin Filter
    admin_filter_enabled: bool = False
    admin_filter_mode: str = 'block'  # 'block' or 'allow'
    admin_list: str = ''  # comma-separated list of admin IDs/usernames
    # User Filter
    user_filter_enabled: bool = False
    user_filter_type: str = 'allow'  # 'allow' or 'block'
    allowed_users: str = ''  # comma-separated user IDs/usernames
    blocked_users: str = ''  # comma-separated user IDs/usernames
    
    # Transparent Buttons Filter
    transparent_buttons_enabled: bool = False
    remove_inline_buttons: bool = False
    remove_reply_buttons: bool = False
    
    # Duplicate Filter
    duplicate_filter_enabled: bool = False
    similarity_threshold: int = 90  # percentage
    duplicate_check_period: int = 24  # hours
    
    # Message Formatting
    message_formatting_enabled: bool = False
    message_format: str = 'original'  # original, bold, italic, etc.
    message_formats: str = ''  # comma-separated list of formats for multiple formatting
    custom_spoiler_url: str = ''  # Custom URL for spoiler formatting
    custom_hyperlink_url: str = ''  # Custom URL for hyperlink formatting
    clean_original_formatting: bool = True  # Clean original formatting before applying new ones
    
    # Link Preview
    link_preview_enabled: bool = True
    
    # Delays
    forward_delay_enabled: bool = False
    message_delay_enabled: bool = False
    message_delay: float = 0.0
    
    # Sync Settings
    sync_delete_enabled: bool = False
    sync_edit_enabled: bool = False
    
    # Notification Settings
    silent_mode_enabled: bool = False
    notifications_enabled: bool = True
    
    # Pin Messages
    pin_messages_enabled: bool = False
    pin_notify_enabled: bool = True
    
    # Reply Preservation
    reply_preservation_enabled: bool = False
    
    # Forwarding Type Extended
    admin_chat_id: str = ''
    
    # ===== نهاية الوظائف المتقدمة =====

@dataclass
class TaskStats:
    """Statistics for a steering task"""
    task_id: str
    messages_processed: int = 0
    messages_forwarded: int = 0
    messages_failed: int = 0
    last_activity: Optional[str] = None
    start_time: Optional[str] = None
    errors: List[str] = None
    
    def __post_init__(self):
        if self.errors is None:
            self.errors = []
        if self.start_time is None:
            self.start_time = datetime.now().isoformat()

class SteeringTask:
    """Individual steering task handler"""
    
    def __init__(self, config: SteeringTaskConfig, client: TelegramClient, logger: logging.Logger):
        self.config = config
        self.client = client
        self.logger = logger
        self.stats = TaskStats(config.task_id)
        self.rate_limiter = RateLimiter()
        self.processed_messages = set()
        self.is_running = False
        self.task_handle = None
        
    async def start(self):
        """Start the steering task"""
        if self.is_running:
            self.logger.warning(f"Task {self.config.task_id} is already running")
            return False
            
        try:
            # Validate chat access
            await self._validate_chats()
            
            # Register message handler for this specific source chat
            self._register_handler()
            
            self.is_running = True
            self.stats.start_time = datetime.now().isoformat()
            self.logger.info(f"✅ Steering task '{self.config.name}' started: {self.config.source_chat} → {self.config.target_chat}")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to start task {self.config.task_id}: {e}")
            return False
    
    async def stop(self):
        """Stop the steering task"""
        self.is_running = False
        if self.task_handle:
            self.task_handle.cancel()
        self.logger.info(f"⏹️ Steering task '{self.config.name}' stopped")
    
    async def _validate_chats(self):
        """Validate access to source and target chats"""
        try:
            # Validate source chat
            try:
                source_entity = await self.client.get_entity(int(self.config.source_chat))
            except ValueError:
                source_entity = await self.client.get_entity(self.config.source_chat)
            
            # Validate target chat
            try:
                target_entity = await self.client.get_entity(int(self.config.target_chat))
            except ValueError:
                target_entity = await self.client.get_entity(self.config.target_chat)
                
            self.logger.info(f"Task {self.config.task_id}: Chats validated")
            
        except Exception as e:
            self.logger.warning(f"Task {self.config.task_id}: Chat validation failed: {e}")
    
    def _register_handler(self):
        """Register message handler for this task's source chat"""
        try:
            source_chat_id = int(self.config.source_chat)
        except ValueError:
            source_chat_id = self.config.source_chat
        
        @self.client.on(events.NewMessage(chats=[source_chat_id]))
        async def handle_message(event):
            if not self.is_running or not self.config.enabled:
                return
            
            # Enhanced duplicate prevention with timestamp
            import time
            current_time = time.time()
            message_key = f"{self.config.task_id}_{event.chat_id}_{event.message.id}_{int(current_time/60)}"
            
            # Check if already processed recently (within 1 minute)
            if hasattr(self, '_recent_messages'):
                if message_key in self._recent_messages:
                    self.logger.debug(f"Task {self.config.task_id}: Duplicate message blocked: {message_key}")
                    return
            else:
                self._recent_messages = set()
            
            # Add to recent messages and clean old entries
            self._recent_messages.add(message_key)
            
            # Clean old entries (keep only last 1000 entries)
            if len(self._recent_messages) > 1000:
                old_messages = list(self._recent_messages)[:500]
                for old_msg in old_messages:
                    self._recent_messages.discard(old_msg)
            
            # Process the message
            await self._process_message(event)
    
    async def _process_message(self, event):
        """Process and forward a message for this task"""
        try:
            message = event.message
            
            # Skip if message is from self
            if message.sender_id == (await self.client.get_me()).id:
                return
            
            # Enhanced rate limiting to prevent rapid forwarding
            import time
            current_time = time.time()
            
            # Initialize last forward time if not exists
            if not hasattr(self, '_last_forward_time'):
                self._last_forward_time = 0
            
            # Enforce minimum delay between forwards (prevent rapid fire)
            min_delay = max(0.5, self.config.forward_delay)  # At least 0.5 seconds
            time_since_last = current_time - self._last_forward_time
            
            if time_since_last < min_delay:
                sleep_time = min_delay - time_since_last
                self.logger.debug(f"Task {self.config.task_id}: Rate limit applied, sleeping {sleep_time:.2f}s")
                await asyncio.sleep(sleep_time)
            
            self.stats.messages_processed += 1
            self.stats.last_activity = datetime.now().isoformat()
            
            # Apply original rate limiting
            await self.rate_limiter.wait()
            
            # Check if message should be forwarded based on task config
            if not self._should_forward_message(message):
                self.logger.debug(f"Task {self.config.task_id}: Skipping message due to filters")
                return
            
            # Update last forward time before attempting forward
            self._last_forward_time = time.time()
            
            # Forward the message
            success = await self._forward_message_to_target(message)
            
            if success:
                self.stats.messages_forwarded += 1
                self.logger.info(f"Task {self.config.task_id}: Message forwarded successfully")
                # Additional delay after successful forward to prevent flood
                await asyncio.sleep(0.2)
            else:
                self.stats.messages_failed += 1
                
        except Exception as e:
            self.stats.messages_failed += 1
            self.stats.errors.append(f"{datetime.now().isoformat()}: {str(e)}")
            self.logger.error(f"Task {self.config.task_id}: Error processing message: {e}")
    
    def _should_forward_message(self, message):
        """Check if message should be forwarded based on task configuration"""
        message_text = message.text or getattr(message, 'caption', '') or ""
        
        # 1. Forwarded Message Filter
        if self.config.forwarded_filter_enabled:
            if message.forward:
                self.logger.info(f"Task {self.config.task_id}: Message blocked - forwarded message filter")
                return False
        
        # 2. User Filter
        if self.config.user_filter_enabled and message.sender_id:
            sender_id = str(message.sender_id)
            sender_username = getattr(message.sender, 'username', '') or ''
            
            if self.config.user_filter_type == 'allow' and self.config.allowed_users:
                allowed_users = [u.strip().replace('@', '') for u in self.config.allowed_users.split(',') if u.strip()]
                user_allowed = any(
                    user in [sender_id, sender_username.lower(), f"@{sender_username.lower()}"] 
                    for user in allowed_users
                )
                if not user_allowed:
                    self.logger.info(f"Task {self.config.task_id}: Message blocked - user not in allowed list")
                    return False
            
            elif self.config.user_filter_type == 'block' and self.config.blocked_users:
                blocked_users = [u.strip().replace('@', '') for u in self.config.blocked_users.split(',') if u.strip()]
                user_blocked = any(
                    user in [sender_id, sender_username.lower(), f"@{sender_username.lower()}"] 
                    for user in blocked_users
                )
                if user_blocked:
                    self.logger.info(f"Task {self.config.task_id}: Message blocked - user in blocked list")
                    return False
        
        # 3. Character Limit Filter
        if self.config.char_limit_enabled and message_text:
            text_length = len(message_text)
            if text_length < self.config.min_chars:
                self.logger.info(f"Task {self.config.task_id}: Message blocked - too short ({text_length} < {self.config.min_chars})")
                return False
            if text_length > self.config.max_chars:
                self.logger.info(f"Task {self.config.task_id}: Message blocked - too long ({text_length} > {self.config.max_chars})")
                return False
        
        # 4. Language Filter (basic implementation)
        if self.config.language_filter_enabled and message_text:
            try:
                # Simple language detection based on character patterns
                detected_lang = self._detect_language(message_text)
                
                if self.config.language_filter_type == 'allow' and self.config.allowed_languages:
                    allowed_langs = [l.strip().lower() for l in self.config.allowed_languages.split(',') if l.strip()]
                    if detected_lang not in allowed_langs:
                        self.logger.info(f"Task {self.config.task_id}: Message blocked - language not allowed ({detected_lang})")
                        return False
                
                elif self.config.language_filter_type == 'block' and self.config.blocked_languages:
                    blocked_langs = [l.strip().lower() for l in self.config.blocked_languages.split(',') if l.strip()]
                    if detected_lang in blocked_langs:
                        self.logger.info(f"Task {self.config.task_id}: Message blocked - language blocked ({detected_lang})")
                        return False
            except Exception as e:
                self.logger.warning(f"Task {self.config.task_id}: Language detection failed: {e}")
        
        # 5. Link Filter
        if self.config.link_filter_enabled and message_text:
            import re
            
            # Check for links
            telegram_links = re.findall(r't\.me/\w+', message_text.lower())
            external_links = re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', message_text.lower())
            
            # Check telegram links
            if telegram_links and not self.config.allow_telegram_links:
                self.logger.info(f"Task {self.config.task_id}: Message blocked - contains telegram links")
                return False
            
            # Check external links
            if external_links and not self.config.allow_external_links:
                self.logger.info(f"Task {self.config.task_id}: Message blocked - contains external links")
                return False
            
            # Check domain filters
            if external_links:
                if self.config.allowed_domains:
                    allowed_domains = [d.strip().lower() for d in self.config.allowed_domains.split(',') if d.strip()]
                    link_allowed = any(
                        any(domain in link for domain in allowed_domains)
                        for link in external_links
                    )
                    if not link_allowed:
                        self.logger.info(f"Task {self.config.task_id}: Message blocked - domain not in allowed list")
                        return False
                
                if self.config.blocked_domains:
                    blocked_domains = [d.strip().lower() for d in self.config.blocked_domains.split(',') if d.strip()]
                    link_blocked = any(
                        any(domain in link for domain in blocked_domains)
                        for link in external_links
                    )
                    if link_blocked:
                        self.logger.info(f"Task {self.config.task_id}: Message blocked - domain in blocked list")
                        return False
        
        # 6. Duplicate Filter (basic implementation)
        if self.config.duplicate_filter_enabled and message_text:
            if hasattr(self, '_message_history'):
                # Simple duplicate detection based on text similarity
                for prev_text in self._message_history:
                    similarity = self._calculate_text_similarity(message_text, prev_text)
                    if similarity >= self.config.similarity_threshold:
                        self.logger.info(f"Task {self.config.task_id}: Message blocked - duplicate detected ({similarity}% similar)")
                        return False
                
                # Add to history (keep last 100 messages)
                if not hasattr(self, '_message_history'):
                    self._message_history = []
                self._message_history.append(message_text)
                if len(self._message_history) > 100:
                    self._message_history.pop(0)
            else:
                self._message_history = [message_text]
        
        # 7. Content filtering (blacklist/whitelist)
        if message_text:
            # Check blacklist
            if self.config.blacklist_enabled and self.config.blacklist_words:
                blacklist = [word.strip().lower() for word in self.config.blacklist_words.split(',') if word.strip()]
                message_lower = message_text.lower()
                for word in blacklist:
                    if word in message_lower:
                        self.logger.info(f"Task {self.config.task_id}: Message blocked by blacklist: {word}")
                        return False
            
            # Check whitelist
            if self.config.whitelist_enabled and self.config.whitelist_words:
                whitelist = [word.strip().lower() for word in self.config.whitelist_words.split(',') if word.strip()]
                message_lower = message_text.lower()
                found_allowed = any(word in message_lower for word in whitelist)
                if not found_allowed:
                    self.logger.info(f"Task {self.config.task_id}: Message blocked by whitelist")
                    return False
        
        # 8. Media type filtering
        if message.text and not message.media:
            return self.config.forward_text
        
        if message.media:
            if message.photo:
                return self.config.forward_photos
            if message.video:
                if message.gif:
                    return self.config.forward_gifs
                return self.config.forward_videos
            if message.document:
                if message.sticker:
                    return self.config.forward_stickers
                if message.voice:
                    return self.config.forward_voice
                if message.video_note:
                    return self.config.forward_round
                if message.audio:
                    return self.config.forward_music if hasattr(message.audio, 'title') and message.audio.title else self.config.forward_audio
                return self.config.forward_files
            if message.contact:
                return self.config.forward_contacts
            if message.geo or message.venue:
                return self.config.forward_locations
            if message.poll:
                return self.config.forward_polls
            if message.game:
                return self.config.forward_games
        
        # Check for links
        if message.text and any(url in message.text.lower() for url in ['http://', 'https://', 'www.', 't.me/']):
            return self.config.forward_links
        
        # Advanced filters
        if not self._should_forward_by_language(message):
            return False
        
        if not self._should_forward_by_links(message):
            return False
        
        if not self._should_forward_by_forwarded(message):
            return False
        
        if not self._should_forward_by_char_limit(message):
            return False
        
        if not self._should_forward_by_user(message):
            return False
        
        return True
    
    async def _forward_message_to_target(self, message):
        """Forward message to target with improved retry logic"""
        # Limit max retries to prevent excessive attempts
        max_retries = min(self.config.max_retries, 3)  # Cap at 3 retries maximum
        
        for attempt in range(max_retries):
            try:
                target_entities_to_try = [
                    self.config.target_chat,
                ]
                
                # Only try numeric conversion if it looks like a number
                if str(self.config.target_chat).lstrip('-').isdigit():
                    target_entities_to_try.append(int(self.config.target_chat))
                
                forwarded = False
                last_error = None
                
                for target_entity in target_entities_to_try:
                    try:
                        if self.config.forward_mode == 'copy':
                            await self._copy_message(message, target_entity)
                        else:
                            await self.client.forward_messages(
                                entity=target_entity,
                                messages=message
                            )
                        
                        forwarded = True
                        
                        # Pin message if enabled
                        if self.config.pin_messages_enabled:
                            await self._pin_forwarded_message(message, target_entity)
                        
                        self.logger.debug(f"Task {self.config.task_id}: Successfully forwarded to {target_entity}")
                        break
                    except (ValueError, TypeError) as e:
                        last_error = e
                        continue
                    except Exception as e:
                        last_error = e
                        self.logger.warning(f"Task {self.config.task_id}: Forward attempt failed: {e}")
                        break
                
                if not forwarded:
                    if last_error:
                        raise last_error
                    raise ValueError(f"Could not forward to any target entity")
                
                # Success - apply appropriate delay
                if self.config.forward_delay > 0:
                    delay = max(0.2, self.config.forward_delay)  # Minimum 200ms delay
                    await asyncio.sleep(delay)
                
                return True
                
            except FloodWaitError as e:
                wait_time = min(e.seconds, 300)  # Cap flood wait at 5 minutes
                self.logger.warning(f"Task {self.config.task_id}: Flood wait {wait_time}s (attempt {attempt + 1}/{max_retries})")
                await asyncio.sleep(wait_time)
                continue
            except Exception as e:
                if attempt == max_retries - 1:
                    self.logger.error(f"Task {self.config.task_id}: Failed to forward after {max_retries} attempts: {e}")
                    return False
                
                # Exponential backoff with cap
                backoff_delay = min(2 ** attempt, 10)  # Cap at 10 seconds
                self.logger.debug(f"Task {self.config.task_id}: Retrying in {backoff_delay}s (attempt {attempt + 1}/{max_retries})")
                await asyncio.sleep(backoff_delay)
        
        return False
    
    async def _copy_message(self, message, target_entity):
        """Copy message as new message (copy mode)"""
        # Process text content
        original_text = message.text or getattr(message, 'caption', '') or ""
        processed_text = self._process_text_content(original_text)
        
        # Create inline buttons if enabled
        buttons = self._create_inline_buttons() if self.config.buttons_enabled else None
        
        # Determine parse mode based on formatting type
        parse_mode = None
        format_type = getattr(self.config, 'message_format', 'original')
        format_list = getattr(self.config, 'message_formats', '')
        
        if getattr(self.config, 'message_formatting_enabled', False):
            # Get all formats to check
            formats_to_check = []
            if format_list and format_list.strip():
                formats_to_check = [f.strip() for f in format_list.split(',') if f.strip()]
            elif format_type != 'original':
                formats_to_check = [format_type]
            
            # Check if any format requires HTML parsing
            html_formats = ['underline', 'strike']
            markdown_formats = ['spoiler', 'hyperlink']
            
            uses_html = any(fmt in html_formats for fmt in formats_to_check)
            uses_markdown = any(fmt in markdown_formats for fmt in formats_to_check)
            
            # Check for custom URLs in spoiler/hyperlink
            if uses_markdown:
                custom_spoiler_url = getattr(self.config, 'custom_spoiler_url', '')
                custom_hyperlink_url = getattr(self.config, 'custom_hyperlink_url', '')
                has_custom_urls = (custom_spoiler_url and custom_spoiler_url.strip()) or \
                                (custom_hyperlink_url and custom_hyperlink_url.strip())
                if not has_custom_urls:
                    uses_markdown = False
            
            # Set parse mode priority: HTML > Markdown
            if uses_html:
                parse_mode = 'HTML'
            elif uses_markdown:
                parse_mode = 'Markdown'
        
        # Send based on message type
        sent_message = None
        if message.media:
            if processed_text or buttons:
                sent_message = await self.client.send_message(
                    target_entity,
                    processed_text,
                    file=message.media,
                    buttons=buttons,
                    parse_mode=parse_mode
                )
            else:
                sent_message = await self.client.send_file(target_entity, message.media)
        else:
            sent_message = await self.client.send_message(
                target_entity,
                processed_text,
                buttons=buttons,
                parse_mode=parse_mode
            )
        
        # Pin message if enabled
        if self.config.pin_messages_enabled and sent_message:
            await self._pin_message(sent_message, target_entity)
    
    def _process_text_content(self, text: str) -> str:
        """Process text with all enabled modifications"""
        if not text:
            return text
        
        # Apply text replacements
        if self.config.replacer_enabled and self.config.replacements:
            text = self._replace_text_content(text)
        
        # Apply message formatting
        if getattr(self.config, 'message_formatting_enabled', False):
            text = self._apply_message_formatting(text)
        
        # Clean text content
        text = self._clean_message_text(text)
        
        # Add header and footer
        text = self._add_header_footer(text)
        
        return text
    
    def _add_header_footer(self, original_text: str) -> str:
        """Add header and footer to text"""
        text_parts = []
        
        if self.config.header_enabled and self.config.header_text:
            text_parts.append(self.config.header_text)
        
        if original_text:
            text_parts.append(original_text)
        
        if self.config.footer_enabled and self.config.footer_text:
            text_parts.append(self.config.footer_text)
        
        return '\n\n'.join(text_parts)
    
    def _create_inline_buttons(self):
        """Create inline buttons from configuration"""
        # Implementation similar to the original, but using task config
        buttons = []
        
        row1 = []
        if self.config.button1_text and self.config.button1_url:
            from telethon import Button
            row1.append(Button.url(self.config.button1_text, self.config.button1_url))
        if self.config.button2_text and self.config.button2_url:
            from telethon import Button
            row1.append(Button.url(self.config.button2_text, self.config.button2_url))
        
        if row1:
            buttons.append(row1)
        
        if self.config.button3_text and self.config.button3_url:
            from telethon import Button
            buttons.append([Button.url(self.config.button3_text, self.config.button3_url)])
        
        return buttons if buttons else None
    
    def _replace_text_content(self, text: str) -> str:
        """Apply text replacements"""
        if not self.config.replacements:
            return text
        
        try:
            replacements = [r.strip() for r in self.config.replacements.split(',') if '->' in r]
            for replacement in replacements:
                if '->' in replacement:
                    old, new = replacement.split('->', 1)
                    text = text.replace(old.strip(), new.strip())
        except Exception as e:
            self.logger.error(f"Task {self.config.task_id}: Error in text replacement: {e}")
        
        return text
    
    async def _pin_forwarded_message(self, original_message, target_entity):
        """Pin the last forwarded message in target chat"""
        try:
            # Get the last message in target chat (should be our forwarded message)
            async for msg in self.client.iter_messages(target_entity, limit=1):
                await self._pin_message(msg, target_entity)
                break
        except Exception as e:
            self.logger.error(f"Task {self.config.task_id}: Error pinning forwarded message: {e}")
    
    async def _pin_message(self, message, target_entity):
        """Pin a specific message"""
        try:
            await self.client.pin_message(
                target_entity, 
                message, 
                notify=self.config.pin_notify_enabled
            )
            self.logger.debug(f"Task {self.config.task_id}: Message pinned successfully")
        except Exception as e:
            self.logger.error(f"Task {self.config.task_id}: Error pinning message: {e}")
    
    def _should_forward_by_language(self, message) -> bool:
        """فحص اللغة"""
        if not self.config.language_filter_enabled:
            return True
        
        try:
            # استخدام مكتبة langdetect أو التحليل البسيط
            text = message.text or getattr(message, 'caption', '')
            if not text:
                return True
            
            # تحليل بسيط للغة (يمكن تحسينه)
            import unicodedata
            
            # فحص النصوص العربية
            arabic_chars = sum(1 for char in text if 'ARABIC' in unicodedata.name(char, ''))
            is_arabic = arabic_chars > len(text) * 0.3
            
            # فحص النصوص الإنجليزية
            english_chars = sum(1 for char in text if char.isascii() and char.isalpha())
            is_english = english_chars > len(text) * 0.5
            
            detected_lang = 'ar' if is_arabic else 'en' if is_english else 'other'
            
            if self.config.language_filter_type == 'allow':
                allowed = self.config.allowed_languages.split(',') if self.config.allowed_languages else []
                return detected_lang in allowed if allowed else True
            else:
                blocked = self.config.blocked_languages.split(',') if self.config.blocked_languages else []
                return detected_lang not in blocked
                
        except Exception as e:
            self.logger.error(f"Language filter error: {e}")
            return True
    
    def _should_forward_by_links(self, message) -> bool:
        """فحص الروابط"""
        if not self.config.link_filter_enabled:
            return True
        
        try:
            text = message.text or getattr(message, 'caption', '') or ''
            
            # فحص وجود روابط
            import re
            telegram_links = re.findall(r't\.me/\w+', text)
            external_links = re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', text)
            
            # فحص روابط تليجرام
            if telegram_links and not self.config.allow_telegram_links:
                return False
            
            # فحص الروابط الخارجية
            if external_links and not self.config.allow_external_links:
                return False
            
            # فحص المواقع المسموحة/المحظورة
            if external_links:
                allowed_domains = [d.strip() for d in self.config.allowed_domains.split(',') if d.strip()] if self.config.allowed_domains else []
                blocked_domains = [d.strip() for d in self.config.blocked_domains.split(',') if d.strip()] if self.config.blocked_domains else []
                
                for link in external_links:
                    domain = re.findall(r'://([^/]+)', link)
                    if domain:
                        domain = domain[0].lower()
                        
                        if blocked_domains and any(bd in domain for bd in blocked_domains):
                            return False
                        
                        if allowed_domains and not any(ad in domain for ad in allowed_domains):
                            return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Link filter error: {e}")
            return True
    
    def _should_forward_by_forwarded(self, message) -> bool:
        """فحص الرسائل المعاد توجيهها"""
        if not self.config.forwarded_filter_enabled:
            return True
        
        # حظر الرسائل المعاد توجيهها
        return not message.forward
    
    def _should_forward_by_char_limit(self, message) -> bool:
        """فحص حد الأحرف"""
        if not self.config.char_limit_enabled:
            return True
        
        text = message.text or getattr(message, 'caption', '') or ''
        text_length = len(text)
        
        return self.config.min_chars <= text_length <= self.config.max_chars
    
    def _should_forward_by_user(self, message) -> bool:
        """فحص المستخدمين"""
        if not self.config.user_filter_enabled:
            return True
        
        try:
            user_id = str(message.sender_id) if message.sender_id else ''
            username = message.sender.username if hasattr(message, 'sender') and message.sender else ''
            
            allowed_users = [u.strip() for u in self.config.allowed_users.split(',') if u.strip()] if self.config.allowed_users else []
            blocked_users = [u.strip() for u in self.config.blocked_users.split(',') if u.strip()] if self.config.blocked_users else []
            
            # فحص القائمة المحظورة
            if blocked_users:
                if user_id in blocked_users or username in blocked_users:
                    return False
            
            # فحص القائمة المسموحة
            if allowed_users:
                return user_id in allowed_users or username in allowed_users
            
            return True
            
        except Exception as e:
            self.logger.error(f"User filter error: {e}")
            return True
    
    def _process_transparent_buttons(self, message):
        """معالجة الأزرار الشفافة"""
        if not self.config.transparent_buttons_enabled:
            return message
        
        try:
            # إزالة الأزرار المدمجة
            if self.config.remove_inline_buttons and hasattr(message, 'reply_markup'):
                message.reply_markup = None
            
            # إزالة أزرار الرد (يتم التعامل معها في معالجة أخرى)
            # هذا يحتاج تنفيذ خاص
            
        except Exception as e:
            self.logger.error(f"Transparent buttons processing error: {e}")
        
        return message
    


    def _clean_message_text(self, text: str) -> str:
        """Clean message text based on configuration"""
        if not text:
            return text
        
        lines = text.split('\n')
        cleaned_lines = []
        
        for line in lines:
            # Skip empty lines if configured
            if self.config.clean_empty_lines and not line.strip():
                continue
            
            # Skip lines containing specific words
            if self.config.clean_lines_with_words and self.config.clean_words_list:
                clean_words = [w.strip() for w in self.config.clean_words_list.split(',') if w.strip()]
                if any(word in line for word in clean_words):
                    continue
            
            # Clean links
            if self.config.clean_links:
                import re
                line = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', line)
                line = re.sub(r't\.me/\w+', '', line)
            
            # Clean hashtags
            if self.config.clean_hashtags:
                import re
                line = re.sub(r'#\w+', '', line)
            
            # Clean formatting
            if self.config.clean_formatting:
                import re
                line = re.sub(r'[*_`~]', '', line)
            
            cleaned_lines.append(line)
        
        return '\n'.join(cleaned_lines)
    
    def _detect_language(self, text: str) -> str:
        """Simple language detection based on character patterns"""
        try:
            # Count different script characters
            arabic_count = sum(1 for c in text if '\u0600' <= c <= '\u06FF')
            latin_count = sum(1 for c in text if c.isalpha() and c.isascii())
            cyrillic_count = sum(1 for c in text if '\u0400' <= c <= '\u04FF')
            chinese_count = sum(1 for c in text if '\u4e00' <= c <= '\u9fff')
            
            total_chars = arabic_count + latin_count + cyrillic_count + chinese_count
            
            if total_chars == 0:
                return 'unknown'
            
            # Determine dominant script
            if arabic_count / total_chars > 0.3:
                return 'ar'
            elif cyrillic_count / total_chars > 0.3:
                return 'ru'
            elif chinese_count / total_chars > 0.3:
                return 'zh'
            elif latin_count / total_chars > 0.3:
                return 'en'
            else:
                return 'mixed'
        except Exception:
            return 'unknown'
    
    def _calculate_text_similarity(self, text1: str, text2: str) -> int:
        """Calculate text similarity percentage using simple word matching"""
        try:
            if not text1 or not text2:
                return 0
            
            # Simple word-based similarity
            words1 = set(text1.lower().split())
            words2 = set(text2.lower().split())
            
            if not words1 or not words2:
                return 100 if text1.strip() == text2.strip() else 0
            
            intersection = len(words1.intersection(words2))
            union = len(words1.union(words2))
            
            if union == 0:
                return 0
            
            similarity = (intersection / union) * 100
            return int(similarity)
        except Exception:
            return 0
    
    def _apply_message_formatting(self, text: str) -> str:
        """Apply formatting to message text based on configuration"""
        try:
            # Check if formatting is enabled and text exists
            if not text or not getattr(self.config, 'message_formatting_enabled', False):
                return text
            
            # Get formatting configuration
            format_type = getattr(self.config, 'message_format', 'original')
            format_list = getattr(self.config, 'message_formats', '')
            clean_original = getattr(self.config, 'clean_original_formatting', True)
            
            # Clean original formatting if enabled
            if clean_original:
                text = self._clean_all_formatting(text)
            
            # Use multi-format if specified, otherwise use single format
            formats_to_apply = []
            if format_list and format_list.strip():
                formats_to_apply = [f.strip() for f in format_list.split(',') if f.strip()]
            elif format_type != 'original':
                formats_to_apply = [format_type]
            
            # Apply each format
            for format_item in formats_to_apply:
                text = self._apply_single_format(text, format_item)
            
            return text
                
        except Exception as e:
            self.logger.error(f"Task {self.config.task_id}: Error applying formatting: {e}")
            return text
    
    def _clean_all_formatting(self, text: str) -> str:
        """Remove all existing formatting from text"""
        import re
        # Remove markdown formatting
        text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)  # Bold
        text = re.sub(r'__(.*?)__', r'\1', text)      # Italic
        text = re.sub(r'`(.*?)`', r'\1', text)        # Code
        text = re.sub(r'```(.*?)```', r'\1', text, flags=re.DOTALL)  # Code block
        text = re.sub(r'~~(.*?)~~', r'\1', text)      # Strikethrough
        text = re.sub(r'\|\|(.*?)\|\|', r'\1', text)  # Spoiler
        
        # Remove HTML formatting
        text = re.sub(r'<u>(.*?)</u>', r'\1', text)   # Underline
        text = re.sub(r'<s>(.*?)</s>', r'\1', text)   # Strikethrough
        text = re.sub(r'<b>(.*?)</b>', r'\1', text)   # Bold
        text = re.sub(r'<i>(.*?)</i>', r'\1', text)   # Italic
        text = re.sub(r'<code>(.*?)</code>', r'\1', text)  # Code
        
        # Remove quote formatting
        lines = text.split('\n')
        cleaned_lines = []
        for line in lines:
            # Remove quote prefix
            if line.strip().startswith('>'):
                line = line.lstrip('> ')
            cleaned_lines.append(line)
        text = '\n'.join(cleaned_lines)
        
        # Remove hyperlinks but keep text
        text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)
        
        return text
    
    def _apply_single_format(self, text: str, format_type: str) -> str:
        """Apply a single formatting type to text"""
        if format_type == 'original' or format_type == 'regular':
            return text
        elif format_type == 'bold':
            return f"**{text}**"
        elif format_type == 'italic':
            return f"__{text}__"
        elif format_type == 'underline':
            return f"<u>{text}</u>"
        elif format_type == 'strike':
            return f"<s>{text}</s>"
        elif format_type == 'code':
            return f"`{text}`"
        elif format_type == 'mono':
            return f"```\n{text}\n```"
        elif format_type == 'quote':
            # Apply quote formatting properly
            lines = text.split('\n')
            formatted_lines = []
            for line in lines:
                if line.strip():
                    formatted_lines.append(f"> {line}")
                else:
                    formatted_lines.append(">")
            return '\n'.join(formatted_lines)
        elif format_type == 'spoiler':
            # Check if custom spoiler URL is set
            custom_spoiler_url = getattr(self.config, 'custom_spoiler_url', '')
            if custom_spoiler_url and custom_spoiler_url.strip():
                return f"[{text}]({custom_spoiler_url.strip()})"
            else:
                return f"||{text}||"
        elif format_type == 'hyperlink':
            # Check if custom hyperlink URL is set
            custom_hyperlink_url = getattr(self.config, 'custom_hyperlink_url', '')
            if custom_hyperlink_url and custom_hyperlink_url.strip():
                return f"[{text}]({custom_hyperlink_url.strip()})"
            else:
                return text
        else:
            return text

class TelegramForwarder:
    """Enhanced Telegram forwarder with concurrent task support"""
    
    def __init__(self, config_path='config.ini'):
        self.logger = logging.getLogger(__name__)
        self.config_manager = ConfigManager(config_path)
        
        # Task management
        self.steering_tasks: Dict[str, SteeringTask] = {}
        self.task_configs: Dict[str, SteeringTaskConfig] = {}
        
        # Telegram client
        self.client = None
        
        # Legacy support
        self.source_chat = None
        self.target_chat = None
        self.forward_options = {}
        
        self._setup_client()
        self._load_config()
        self._load_steering_tasks()
    
    def _setup_client(self):
        """Setup Telegram client with credentials"""
        try:
            api_id = os.getenv('TELEGRAM_API_ID') or self.config_manager.get('telegram', 'api_id')
            api_hash = os.getenv('TELEGRAM_API_HASH') or self.config_manager.get('telegram', 'api_hash')
            
            if not api_id or not api_hash or api_id == 'YOUR_API_ID':
                raise ValueError("Please set TELEGRAM_API_ID and TELEGRAM_API_HASH environment variables or update config.ini")
            
            string_session = os.getenv('TELEGRAM_STRING_SESSION')
            
            if string_session and len(string_session) > 10:
                try:
                    from telethon.sessions import StringSession
                    self.client = TelegramClient(StringSession(string_session), int(api_id), api_hash)
                    self.logger.info("Using string session for authentication")
                except Exception as e:
                    self.logger.warning(f"Failed to use string session: {e}, falling back to file session")
                    self.client = TelegramClient('userbot_session', int(api_id), api_hash)
            else:
                self.client = TelegramClient('userbot_session', int(api_id), api_hash)
            
        except Exception as e:
            self.logger.error(f"Failed to setup Telegram client: {e}")
            raise
    
    def _load_config(self):
        """Load legacy configuration for backward compatibility"""
        try:
            source_chat_raw = self.config_manager.get('forwarding', 'source_chat')
            target_chat_raw = self.config_manager.get('forwarding', 'target_chat')

            if ',' in source_chat_raw:
                self.source_chats = [chat.strip() for chat in source_chat_raw.split(',') if chat.strip()]
            else:
                self.source_chats = [source_chat_raw.strip()] if source_chat_raw.strip() else []
            
            if ',' in target_chat_raw:
                self.target_chats = [chat.strip() for chat in target_chat_raw.split(',') if chat.strip()]
            else:
                self.target_chats = [target_chat_raw.strip()] if target_chat_raw.strip() else []
            
            self.source_chat = self.source_chats[0] if self.source_chats else None
            self.target_chat = self.target_chats[0] if self.target_chats else None
            
            # Load other options for legacy compatibility
            self.forward_options = {
                'delay': self.config_manager.getfloat('forwarding', 'forward_delay', fallback=1.0),
                'max_retries': self.config_manager.getint('forwarding', 'max_retries', fallback=3),
                'forward_mode': self.config_manager.get('forwarding', 'forward_mode', fallback='forward'),
                'multi_mode_enabled': self.config_manager.getboolean('forwarding', 'multi_mode_enabled', fallback=False)
            }
            
        except Exception as e:
            self.logger.warning(f"Legacy config loading failed: {e}")
    
    def _load_steering_tasks(self):
        """Load steering tasks from configuration"""
        try:
            # Try to load from tasks.json file
            if os.path.exists('steering_tasks.json'):
                with open('steering_tasks.json', 'r', encoding='utf-8') as f:
                    tasks_data = json.load(f)
                    for task_data in tasks_data:
                        config = SteeringTaskConfig(**task_data)
                        self.task_configs[config.task_id] = config
            else:
                # Create default task from legacy config if available
                if self.source_chat and self.target_chat:
                    default_config = self._create_default_task_config()
                    self.task_configs[default_config.task_id] = default_config
                    self._save_steering_tasks()
            
            self.logger.info(f"Loaded {len(self.task_configs)} steering task configurations")
            
        except Exception as e:
            self.logger.error(f"Failed to load steering tasks: {e}")
    
    def _create_default_task_config(self) -> SteeringTaskConfig:
        """Create default task config from legacy settings"""
        return SteeringTaskConfig(
            task_id="default_task",
            name="Default Task",
            source_chat=self.source_chat,
            target_chat=self.target_chat,
            forward_delay=self.forward_options.get('delay', 1.0),
            max_retries=self.forward_options.get('max_retries', 3),
            forward_mode=self.forward_options.get('forward_mode', 'copy')
        )
    
    def _save_steering_tasks(self):
        """Save steering tasks to JSON file"""
        try:
            tasks_data = [asdict(config) for config in self.task_configs.values()]
            with open('steering_tasks.json', 'w', encoding='utf-8') as f:
                json.dump(tasks_data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            self.logger.error(f"Failed to save steering tasks: {e}")
    
    async def start(self):
        """Start the userbot and all enabled steering tasks"""
        try:
            await self.client.start()
            
            me = await self.client.get_me()
            self.logger.info(f"Logged in as: {me.first_name} {me.last_name or ''} (@{me.username or 'N/A'})")
            
            # Register admin commands
            self._register_admin_handlers()
            
            # Start all enabled steering tasks
            started_tasks = 0
            for config in self.task_configs.values():
                if config.enabled:
                    success = await self.start_steering_task(config.task_id)
                    if success:
                        started_tasks += 1
            
            self.logger.info(f"✅ Userbot started with {started_tasks}/{len(self.task_configs)} steering tasks")
            
        except Exception as e:
            self.logger.error(f"Failed to start userbot: {e}")
            raise
    
    async def start_steering_task(self, task_id: str) -> bool:
        """Start a specific steering task"""
        if task_id not in self.task_configs:
            self.logger.error(f"Task {task_id} not found")
            return False
        
        if task_id in self.steering_tasks:
            self.logger.warning(f"Task {task_id} is already running")
            return False
        
        config = self.task_configs[task_id]
        task = SteeringTask(config, self.client, self.logger)
        
        success = await task.start()
        if success:
            self.steering_tasks[task_id] = task
        
        return success
    
    async def stop_steering_task(self, task_id: str) -> bool:
        """Stop a specific steering task"""
        if task_id not in self.steering_tasks:
            self.logger.warning(f"Task {task_id} is not running")
            return False
        
        task = self.steering_tasks[task_id]
        await task.stop()
        del self.steering_tasks[task_id]
        
        return True
    
    async def restart_steering_task(self, task_id: str) -> bool:
        """Restart a specific steering task"""
        await self.stop_steering_task(task_id)
        return await self.start_steering_task(task_id)
    
    def add_steering_task(self, config: SteeringTaskConfig):
        """Add a new steering task configuration"""
        self.task_configs[config.task_id] = config
        self._save_steering_tasks()
        self.logger.info(f"Added steering task: {config.name}")
    
    def remove_steering_task(self, task_id: str) -> bool:
        """Remove a steering task configuration"""
        try:
            if task_id in self.steering_tasks:
                asyncio.create_task(self.stop_steering_task(task_id))
            
            if task_id in self.task_configs:
                del self.task_configs[task_id]
                self._save_steering_tasks()
                self.logger.info(f"Removed steering task: {task_id}")
                return True
            else:
                self.logger.warning(f"Task {task_id} not found in configurations")
                return False
        except Exception as e:
            self.logger.error(f"Failed to remove task {task_id}: {e}")
            return False
    
    def get_task_stats(self) -> Dict[str, Dict]:
        """Get statistics for all tasks"""
        stats = {}
        for task_id, task in self.steering_tasks.items():
            config = self.task_configs[task_id]
            stats[task_id] = {
                'name': config.name,
                'status': 'running' if task.is_running else 'stopped',
                'source_chat': config.source_chat,
                'target_chat': config.target_chat,
                'stats': asdict(task.stats)
            }
        
        # Add stopped tasks
        for task_id, config in self.task_configs.items():
            if task_id not in stats:
                stats[task_id] = {
                    'name': config.name,
                    'status': 'stopped',
                    'source_chat': config.source_chat,
                    'target_chat': config.target_chat,
                    'stats': None
                }
        
        return stats
    
    def get_task_config(self, task_id: str) -> Optional[SteeringTaskConfig]:
        """Get configuration for a specific task"""
        return self.task_configs.get(task_id)
    
    def update_task_config(self, task_id: str, **kwargs) -> bool:
        """Update configuration for a specific task"""
        try:
            if task_id not in self.task_configs:
                return False
            
            config = self.task_configs[task_id]
            
            # Track which settings need restart vs simple update
            restart_required_settings = {
                'source_chat', 'target_chat', 'enabled', 'forward_delay', 
                'max_retries', 'forward_mode'
            }
            
            needs_restart = False
            
            for key, value in kwargs.items():
                if hasattr(config, key):
                    setattr(config, key, value)
                    # Check if this setting requires restart
                    if key in restart_required_settings:
                        needs_restart = True
            
            self._save_steering_tasks()
            
            # Only restart if necessary for critical settings
            if needs_restart and task_id in self.steering_tasks:
                self.logger.info(f"Restarting task {task_id} due to critical setting changes")
                asyncio.create_task(self.restart_steering_task(task_id))
            elif task_id in self.steering_tasks:
                # For non-critical settings like formatting, just update the running task
                task = self.steering_tasks[task_id]
                task.config = config
                self.logger.info(f"Updated task {task_id} configuration without restart")
            
            return True
        except Exception as e:
            self.logger.error(f"Failed to update task config {task_id}: {e}")
            return False
    
    def get_all_task_configs(self) -> Dict[str, SteeringTaskConfig]:
        """Get all task configurations"""
        return self.task_configs.copy()
    
    def _register_admin_handlers(self):
        """Register admin command handlers"""
        
        @self.client.on(events.NewMessage(pattern='/ping', from_users='me'))
        async def ping_handler(event):
            try:
                import time
                start_time = time.time()
                
                # Get task statistics
                task_stats = self.get_task_stats()
                running_tasks = sum(1 for t in task_stats.values() if t['status'] == 'running')
                total_tasks = len(task_stats)
                
                # Create status summary
                status_lines = []
                for task_id, stats in task_stats.items():
                    if stats['status'] == 'running':
                        task_stats_data = stats['stats']
                        processed = task_stats_data['messages_processed'] if task_stats_data else 0
                        forwarded = task_stats_data['messages_forwarded'] if task_stats_data else 0
                        status_lines.append(f"  ✅ {stats['name']}: {forwarded}/{processed}")
                    else:
                        status_lines.append(f"  ⏹️ {stats['name']}: stopped")
                
                response_text = (
                    "🤖 **Userbot Status - Multi-Task Mode**\n\n"
                    f"✅ **Active Tasks:** {running_tasks}/{total_tasks}\n"
                    f"⚡ **Response time:** {round((time.time() - start_time) * 1000)}ms\n\n"
                    "📊 **Task Status:**\n" + 
                    ("\n".join(status_lines) if status_lines else "  No tasks configured")
                )
                
                await event.respond(response_text)
                
            except Exception as e:
                self.logger.error(f"Error in ping handler: {e}")
        
        @self.client.on(events.NewMessage(pattern='/tasks', from_users='me'))
        async def tasks_handler(event):
            """Show detailed task information"""
            try:
                task_stats = self.get_task_stats()
                
                if not task_stats:
                    await event.respond("📋 No steering tasks configured")
                    return
                
                response_lines = ["📋 **Steering Tasks Overview**\n"]
                
                for task_id, stats in task_stats.items():
                    status_emoji = "🟢" if stats['status'] == 'running' else "🔴"
                    response_lines.append(f"{status_emoji} **{stats['name']}** (`{task_id}`)")
                    response_lines.append(f"   📥 Source: `{stats['source_chat']}`")
                    response_lines.append(f"   📤 Target: `{stats['target_chat']}`")
                    
                    if stats['stats']:
                        task_data = stats['stats']
                        response_lines.append(f"   📊 Processed: {task_data['messages_processed']}")
                        response_lines.append(f"   ✅ Forwarded: {task_data['messages_forwarded']}")
                        response_lines.append(f"   ❌ Failed: {task_data['messages_failed']}")
                    
                    response_lines.append("")
                
                await event.respond("\n".join(response_lines))
                
            except Exception as e:
                self.logger.error(f"Error in tasks handler: {e}")
                await event.respond(f"❌ Error: {e}")
    
    async def run_until_disconnected(self):
        """Run until disconnected"""
        try:
            await self.client.run_until_disconnected()
        except KeyboardInterrupt:
            self.logger.info("Received interrupt signal")
        finally:
            await self.stop()
    
    async def stop(self):
        """Stop all tasks and disconnect"""
        self.logger.info("Stopping all steering tasks...")
        
        # Stop all running tasks
        for task_id in list(self.steering_tasks.keys()):
            await self.stop_steering_task(task_id)
        
        # Disconnect client
        if self.client and self.client.is_connected():
            await self.client.disconnect()
        
        self.logger.info("Userbot stopped")
