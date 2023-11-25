from notion_client import Client
import os
import json
import redis


class NotionConnector:
    def __init__(self, database_id=None, token=None):
        redis_host = os.getenv("REDIS_HOST", "localhost")
        redis_port = os.getenv("REDIS_PORT", 6379)
        redis_password = os.getenv("REDIS_PASSWORD", None)
        self.redis_client = redis.Redis(
            host=redis_host, port=redis_port, password=redis_password, db=1
        )

        self.client = Client(auth=token or os.getenv("NOTION_TOKEN"))
        self.database_id = database_id or os.getenv("NOTION_DATABASE_ID")

    def get_entries(self):
        entries = []
        start_cursor = None
        page_count = 0

        while True:
            response = self.client.databases.query(
                database_id=self.database_id,
                filter={"property": "Report", "select": {"equals": "Daily"}},
                start_cursor=start_cursor,
            )

            rows = response.get("results", [])
            page_count += 1

            for row in rows:
                entries.append(self.process_entry(row))

            print(f"Processed page {page_count}")

            if not response.get("next_cursor"):
                break
            start_cursor = response["next_cursor"]

        print("All pages processed.")

        return entries

    def process_entry(self, row):
        entry_data = {
            "date": row["properties"]["Date Combined"]["formula"]["string"],
            "text": "",
        }
        self.get_block_content(row["id"], row["last_edited_time"], entry_data)
        return entry_data

    def get_block_content(self, block_id, last_edited_time, entry_data):
        cache_key = f"${block_id}-${last_edited_time}"
        blocks = self.redis_client.get(cache_key)
        if blocks:
            blocks = json.loads(blocks)
        else:
            blocks = self.client.blocks.children.list(block_id=block_id).get(
                "results", []
            )
            self.redis_client.set(cache_key, json.dumps(blocks))

        for block in blocks:
            entry_data["text"] += self.extract_text_from_block(block)
            if block["has_children"]:
                self.get_block_content(block["id"], last_edited_time, entry_data)

    def extract_text_from_block(self, block):
        block_type = block["type"]
        text_contents = block[block_type].get("rich_text", [])

        return " ".join(
            text_component["plain_text"] for text_component in text_contents
        )
