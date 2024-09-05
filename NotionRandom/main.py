import os
import asyncio
from typing import List, Dict
from dotenv import load_dotenv
from utils import load_database_configs
from utils.scheduler import schedule_updates, run_scheduled_updates
from updater.random_display import update_notion_random_display
from utils.logger import setup_logger

load_dotenv()
logger = setup_logger()

async def main():
    try:
        configs: List[Dict[str, any]] = load_database_configs()
        logger.info("Starting Multi-Database Notion Random Display Updater...")
        
        # 初回の更新を並行して実行
        tasks = [update_notion_random_display(config) for config in configs]
        await asyncio.gather(*tasks)
        
        # スケジュールを設定
        schedule_updates(configs)
        
        # スケジュールされた更新を実行
        await run_scheduled_updates()
    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main())