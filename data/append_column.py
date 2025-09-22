import sqlite3
conn = sqlite3.connect('data/app.db')
cur = conn.cursor()
cur.execute("ALTER TABLE messagetemplate ADD COLUMN was_sent INTEGER DEFAULT 0")    #was_sent为新增的列
cur.execute("ALTER TABLE messagetemplate ADD COLUMN sent_at TEXT")                  #sent_at为新增的列
conn.commit()
conn.close()