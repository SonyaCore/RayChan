#!/usr/bin/env python3
"""
ChanEXT : Telegram Folder Channel Username Extractor
"""

import asyncio
import os
from telethon import TelegramClient
from telethon.tl.functions.chatlists import CheckChatlistInviteRequest
from telethon.sessions import StringSession
from urllib.parse import urlparse

__version__ = "1.0.0"

API_ID = os.getenv('TELEGRAM_API_ID', 'SET_API_ID')
API_HASH = os.getenv('TELEGRAM_API_HASH', 'SET_API_HASH')
STRING_SESSION = os.getenv('TELEGRAM_STRING_SESSION', 'SET_STRING_SESSION')

class TelegramFolderExtractor:
    def __init__(self, api_id, api_hash, session):
        # Use string session instead of file-based session
        api_id = int(api_id) if isinstance(api_id, str) else api_id
        self.client = TelegramClient(StringSession(session), api_id, api_hash)
        
    def parse_folder_link(self, folder_link):
        """Extract the slug from the folder link"""
        try:
            parsed_url = urlparse(folder_link)
            path_parts = parsed_url.path.split('/')
            if len(path_parts) >= 3 and path_parts[1] == 'addlist':
                return path_parts[2]
            return None
        except:
            return None
    
    async def get_channel_usernames(self, folder_link):
        """Extract only channel usernames from folder invitation"""
        slug = self.parse_folder_link(folder_link)
        if not slug:
            return []
        
        try:
            await self.client.start()
            
            # Check folder contents
            result = await self.client(CheckChatlistInviteRequest(slug=slug))
            
            usernames = []
            if hasattr(result, 'chats'):
                for chat in result.chats:
                    if hasattr(chat, 'username') and chat.username:
                        usernames.append(chat.username)
            
            return usernames
            
        except Exception as e:
            print(f"Error: {e}")
            return []
        finally:
            await self.client.disconnect()


async def generate_string_session():
    """Generate a string session (run this once locally to get your session)"""
    if API_ID == 'YOUR_API_ID':
        print("Set your API_ID and API_HASH first")
        return
    
    phone = input("Enter your phone number: ")
    client = TelegramClient('temp_session', API_ID, API_HASH)
    
    await client.start(phone=phone)
    session_string = StringSession.save(client.session)
    print(f"\nYour string session:")
    print(session_string)
    print(f"\nSave this as TELEGRAM_STRING_SESSION environment variable")
    
    await client.disconnect()
    
    # remove temp session
    try:
        os.remove('temp_session.session')
    except:
        pass

async def main():
    print(f"ChanEXT v{__version__}")
    
    # Check if we need to generate string session
    if len(os.sys.argv) > 1 and os.sys.argv[1] == '--generate-session':
        await generate_string_session()
        return []
    
    # Check credentials
    if API_ID == 'SET_API_ID' or not STRING_SESSION or STRING_SESSION == 'SET_STRING_SESSION':
        print("Missing credentials!")
        print("Either set environment variables:")
        print("  TELEGRAM_API_ID")
        print("  TELEGRAM_API_HASH") 
        print("  TELEGRAM_STRING_SESSION")
        print("\nOr generate string session with:")
        print("  python telegram_extractor.py --generate-session")
        return []
    
    # Read folder link from file
    try:
        with open('folder.txt', 'r') as f:
            folder_link = f.read().strip()
    except FileNotFoundError:
        print("Error: folder.txt not found. Please create it with your folder link.")
        return []
    except Exception as e:
        print(f"Error reading folder.txt: {e}")
        return []
    
    if not folder_link:
        print("Error: folder.txt is empty")
        return []
    
    extractor = TelegramFolderExtractor(API_ID, API_HASH, STRING_SESSION)    
    usernames = await extractor.get_channel_usernames(folder_link)
    
    # save to file
    if usernames:
        with open('channels.txt', 'w') as f:
            for username in usernames:
                f.write(f"{username}\n")
        print(f"\nSaved {len(usernames)} usernames to channels.txt")
    else:
        print("No usernames found")
    
    return usernames


if __name__ == "__main__":
    usernames = asyncio.run(main())