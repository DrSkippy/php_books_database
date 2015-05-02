#!/usr/bin/env python
#
# Written by Scott Hendrickson
#
# 2006/01/09
#
# Tools for manipulating the book database 
###################################################

import  datetime, unittest, string, urllib, MySQLdb
from optparse import OptionParser

UN=xxx
PWD=xxx
DB=xxx
DBHOST=xxx

class bookDBTool:
  def __init__(self):
	self.db=MySQLdb.connect(host=DBHOST,
                            port=3306,
                            user=UN,
                            passwd=PWD,
                            db=DB)
	return

  def showTags(self):
	c = self.db.cursor()
  	try:
	  c.execute("""select distinct Tag from tags order by Tag""")
 	except MySQLdb.Error, e:
		print "Error %d: %s" % (e.args[0], e.args[1])
 	s = c.fetchall()
	st = []
	for i in s:
		print "  %s"%i[0]
#		st.append(i[0])
#	print st
#	return st
    
  def showLocations(self):
	c = self.db.cursor()
  	try:
	  c.execute("""select distinct Location from `book collection`""")
 	except MySQLdb.Error, e:
		print "Error %d: %s" % (e.args[0], e.args[1])
 	s = c.fetchall()
	sl = []
	for i in s:
		print "  %s"%i[0]
#		sl.append(i[0])
#	print sl
#	return sl


  def tagFromCategory(self,tag,cat):
	cl = self.getCategoryIDList(cat)
	self.addTag(cl, tag)
	return

  def addTag(self, cl, tag):
	c = self.db.cursor()
	for id in cl:
		print 'Inserted: ',id
		try:
	  	   c.execute("""insert into tags (BookID, Tag) values (%s, %s)""",\
		        (id, tag))
 		except MySQLdb.Error, e:
		   print "Error %d: %s" % (e.args[0], e.args[1])
	return

  def getCategoryIDList(self,cat):
	c = self.db.cursor()
  	try:
	  c.execute("""select BookCollectionID from `book collection` where Category=%s""",cat)
 	except MySQLdb.Error, e:
		print "Error %d: %s" % (e.args[0], e.args[1])
 	s = c.fetchall()
	catIDList = []
	for i in s:
		catIDList.append(i[0])
	return catIDList


  def deDuplicateTags(self):
	c = self.db.cursor()
  	try:
	  c.execute("""truncate temp""")
	  c.execute("""insert into temp (BookID, Tag) select distinct BookID, Tag from tags""")
	  c.execute("""truncate tags""")
	  c.execute("""insert into tags (BookID, Tag) select BookID, Tag from temp""")
	  c.execute("""truncate temp""")
	  c.execute("""delete from tags where Tag=''""");
 	except MySQLdb.Error, e:
		print "Error %d: %s" % (e.args[0], e.args[1])
	return 

if __name__ == '__main__':
  parser = OptionParser()
  parser.add_option("-d","--deDup",action="store_true",dest="dup",help="Remove duplicate tag entries from Tag table")
  parser.add_option("-f",dest="tagAttr",nargs=2,help="Enter tag and field values, e.g. -f poetry Poetry. Each occurance of (field) in column Category will result in tagging the record with (tag).")
  parser.add_option("-s","--show",action="store_true",dest="show",help="Show tags and fields.")
  (options, args) = parser.parse_args()
  bt = bookDBTool()
  if (options.tagAttr):
	  print "Adding tag " + options.tagAttr[0] + " to records in category " + options.tagAttr[1]
	  bt.tagFromCategory(options.tagAttr[0],options.tagAttr[1])
  if (options.dup):
	  print "Removing duplicate and null tags..."
	  bt.deDuplicateTags()
  if (options.show):
	  print "Tags:"
	  bt.showTags()
	  print "Locations:"
	  bt.showLocations()
