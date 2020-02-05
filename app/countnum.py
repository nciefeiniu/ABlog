import pymysql
import html2markdown
import re
import urllib.parse as urllib


store_db=pymysql.connect(host='127.0.0.1',port=3306,user='blog',passwd='cyx210210',db='blog',charset='utf8mb4')
store_cursor=store_db.cursor()


def update_tags():
    get_sql='select category_id,tags from posts;'
    store_cursor.execute(get_sql)
    tags=store_cursor.fetchall()
    tag_count={}
    cate_count={}
    for category_id,tag in tags:
        cate_count.setdefault(category_id,0)
        cate_count[category_id]+=1
        for t in tag.split(','):
            if t!='':
                tag_count.setdefault(t,0)
                tag_count[t]+=1
    for t,n in tag_count.items():
        update_sql='update tags set refer_num=%s where tag=%s;'
        store_cursor.execute(update_sql,(n,t))
        store_db.commit()
    for c,n in cate_count.items():
        update_sql='update category set refer_num=%s where id=%s;'
        store_cursor.execute(update_sql,(n,c))
        store_db.commit()


def main():
    update_tags()

main()
