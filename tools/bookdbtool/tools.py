import logging
import pymysql
import pandas as pd

from spellchecker import SpellChecker

class bookDBTool:
    def __init__(self, DBHOST, UN, PWD, DB):
        self.db = pymysql.connect(host=DBHOST, port=3306, user=UN, passwd=PWD, db=DB)

    def show_tags(self):
        spell = SpellChecker()
        st = []
        c = self.db.cursor()
        try:
            c.execute(
                "SELECT Tag, COUNT(Tag) as count FROM tags GROUP BY Tag ORDER BY count DESC")
        except pymysql.Error as e:
            logging.error(e)
        else:
            s = c.fetchall()
            print("{} {} {}".format("#"*20, "tags", "#"*20))
            for i in s:
                w = spell.unknown(i[0].split(" "))
                suggest = []
                if len(w) > 0:
                    for j in w:
                        suggest.append(str(spell.candidates(j)))
                    suggest = ";".join(suggest)
                else:
                    suggest = ""
                print("  {}  ({})    {}".format(i[0], i[1], suggest))
                st.append(i[0])
        return st

    def show_locations(self):
        sl = []
        c = self.db.cursor()
        try:
            c.execute(
                "SELECT Location, COUNT(Location) as count FROM `book collection` GROUP BY Location ORDER BY count DESC")
        except pymysql.Error as e:
            logging.error(e)
        else:
            s = c.fetchall()
            print("{} {} {}".format("#" * 20, "locations", "#" * 20))
            for i in s:
                print("  {}  ({})".format(*i))
                sl.append(i[0])
        return sl

    def tag_from_category(self, tag, cat):
        cl = self.get_category_ID_list(cat)
        self.add_tag(cl, tag)

    def lower_case_tags(self):
        c = self.db.cursor()
        try:
            c.execute("UPDATE `tags` SET Tag = LOWER(Tag)")
            self.db.commit()
        except pymysql.Error as e:
            logging.error(e)

    def add_tag(self, cl, tag):
        c = self.db.cursor()
        for id in cl:
            print('Inserted: ', id)
        try:
            c.execute("insert into tags (BookID, Tag) values (%s, %s)", (id, tag))
        except pymysql.Error as e:
            logging.error(e)

    def get_category_ID_list(self, cat):
        c = self.db.cursor()
        cat_ID_list = []
        try:
            c.execute("select BookCollectionID from `book collection` where Category=%s", cat)
        except pymysql.Error as e:
            logging.error(e)
        else:
            s = c.fetchall()
            for i in s:
                cat_ID_list.append(i[0])
        return cat_ID_list

    def deduplicate_tags(self):
        c = self.db.cursor()
        try:
            c.execute("SELECT COUNT(*) FROM tags")
            a = c.fetchall()
            print("Tags Before: {}".format(a[0][0]))
            c.execute("truncate temp")
            c.execute("insert into temp (BookID, Tag) select distinct BookID, Tag from tags")
            c.execute("truncate tags")
            c.execute("insert into tags (BookID, Tag) select BookID, Tag from temp")
            c.execute("truncate temp")
            c.execute("delete from tags where Tag=''")
            self.db.commit()
            c.execute("SELECT COUNT(*) FROM tags")
            a = c.fetchall()
            print("Tags After: {}".format(a[0][0]))
        except pymysql.Error as e:
            logging.error("Error %d: %s" % (e.args[0], e.args[1]))

    def get_dataframe(self, year=None):
        if year is not None:
            df = pd.read_sql("select * from `book collection` where YEAR(LastRead)={}".format(year),
                             self.db, "BookCollectionID", parse_dates=["LastRead", "PreviouslyRead"])
        else:
            df = pd.read_sql("select * from `book collection`",
                             self.db, "BookCollectionID", parse_dates=["LastRead", "PreviouslyRead"])
        return df

    def get_rank_dataframe(self):
        search_str = """ select year(LastRead) as Year, sum(Pages) as `Pages Read` from `book collection` 
            where LastRead is not NULL and LastRead <> "0000-00-00 00:00:00" and year(LastRead) <> "1966" 
            group by Year order by `Pages Read` desc;"""
        df = pd.read_sql(search_str, self.db)
        df["Rank"] = df.index + 1
        return df

    def get_running_year_dataframe(self):
        search_str = """ SELECT LastRead, Sum(Pages) as Pages
                    FROM `book collection`
                    WHERE LastRead is not NULL and LastRead <> "0000-00-00 00:00:00" and year(LastRead) <> "1966" 
                    GROUP BY LastRead
                    ORDER BY LastRead ASC;"""
        df = pd.read_sql(search_str, self.db).set_index("LastRead")
        df = df.groupby(df.index.to_period('y')).cumsum().reset_index()
        df["Day"] = df.LastRead.apply(lambda x: x.dayofyear)
        df["Year"] = df.LastRead.apply(lambda x: x.year)
        return df

    def close(self):
        self.db.close()