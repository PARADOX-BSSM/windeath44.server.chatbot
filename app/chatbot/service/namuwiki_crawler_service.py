from typing import List, Tuple
from nadf.crawler import Crawler
from app.chatbot.exception.no_content_found_exception import NoContentFoundException


class NamuwikiCrawlerService:

    def __init__(self):
        self.crawler = Crawler()
    
    async def crawl_character(self, character_name: str) -> List[Tuple[str, str, str]]:
        print(f"Attempting to crawl Namuwiki for character: '{character_name}'")
        
        try:
            namuwiki_list = await self.crawler.get_namuwiki_list(name=character_name)
            print(f"Crawler returned {len(namuwiki_list) if namuwiki_list else 0} items")
            
            if not namuwiki_list:
                print(f"Warning: No namuwiki content found for character '{character_name}'")
                print(f"This could be due to:")
                print(f"  1. Character name not found in Namuwiki")
                print(f"  2. Network connectivity issues")
                print(f"  3. Character name format/encoding issues")
                raise NoContentFoundException(character_name=character_name)
            
            return namuwiki_list
        
        except IndexError as e:
            # 크롤러 내부에서 deque가 비어있을 때 발생
            print(f"IndexError caught while crawling Namuwiki for '{character_name}': {e}")
            print(f"Possible causes:")
            print(f"  1. No search results found in Namuwiki")
            print(f"  2. HTML parsing failed (structure changed)")
            print(f"  3. Network error or access blocked")
            print(f"  4. Character name encoding issue")
            raise NoContentFoundException(character_name=character_name) from e

namuwiki_crawler_service = NamuwikiCrawlerService()
