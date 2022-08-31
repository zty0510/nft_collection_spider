
from project.config import MYSQL_CONFIG
from project.utils.mysql_helper import Mysql
from project.utils.logger import Log


class Announcement:
    mysql = Mysql(MYSQL_CONFIG)
    list_table = 'announcement'
    detail_table = 'announcement_content'
    logger = Log(list_table)

    def found_hash_match(self, content_hash):
        return bool(self.mysql.read_one(f'select title from {self.list_table} where content_url = %s',
                                        (content_hash,)))

    def save_news(self, title, cover, publish, platform, content_hash, content):
        if self.found_hash_match(content_hash):
            return
        self.logger.info(f'saving {title}')
        self.mysql.write(f'insert into {self.detail_table} (content_url, content) values (%s, %s)',
                         (content_hash, content))
        self.mysql.write(f'insert into {self.list_table} (title, head_image, publish_time, platform_id, content_url) '
                         f'values (%s, %s, %s, %s, %s)', (title, cover, publish, platform, content_hash))


if __name__ == '__main__':
    print(Announcement().found_hash_match('068007e0ba9f50301e6beb262c28b06b'))

