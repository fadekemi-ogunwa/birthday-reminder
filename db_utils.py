import sqlite3

def insert_into_db(query):	
	conn = sqlite3.connect('gifter.db')
	c = conn.cursor()
	c.execute(query)
	conn.commit()
	c.close()
	return response


# Create table
def create_table():
	table_name = 'gifters_locations'
	conn = sqlite3.connect('gifter.db')
	c = conn.cursor()
	query = "SELECT count(*) FROM sqlite_master WHERE type='table' AND name='" + table_name + "';"
	w = c.execute(query)
	table_count = w.fetchone()[0]
	if table_count > 0:
		print "Dropping existing table"
		delete_query = "DROP TABLE " + table_name + ";"
		c.execute(delete_query)

		print "Creating new table " + table_name

	query = '''CREATE TABLE ''' + table_name + '''
		  		(email text, city text)'''
	c.execute(query)

	gifters_cities = gifters_cities_dict()
	for gifter in gifters_cities:
		for location in gifters_cities[gifter]:
			query = "INSERT INTO " + table_name + "(email, city) VALUES ('" + gifter + "', '" + location + "')"
			c.execute(query)
			conn.commit()

	conn.close()



def gifters_cities_dict():
	return {'olaoluwa.ogunwa@rimonlaw.com' : ['Bedminster', 'Boston', 'Jerusalem', 'Miami', 'New York', 'Newark', 'Northern Virginia', 'NYC', 'Orlando', 'Research Triangle', 'Tel Aviv', 'Washington, D.C.', 'DC'],
	'oluwafadekemmie@gmail.com' : ['Chicago', 'Dallas', 'Minneapolis'],
	'fadekemmie@yahoo.com' : ['Lake Tahoe', 'Las Vegas', 'Los Angeles', 'Orange County', 'Palo Alto', 'Menlo Park', 'Silicon Valley', 'Portland', 'Sacramento', 'San Diego', 'San Francisco', 'Seattle'],
	'olarimonuipathquiz@gmail.com': ['Not Available'] }

	

create_table()




# # check  if table exist
# conn = sqlite3.connect('gifter.db')
# c = conn.cursor()
# query = "SELECT count(*) FROM sqlite_master WHERE type='table' AND name='gifters_locations';"
# # print "wrong table name", c.execute(query)
# w = c.execute(query)
# print  "right table", w.fetchone()

# query = "SELECT count(*) FROM sqlite_master WHERE type='table' AND name='stocks';"
# # print "right table name", c.execute(query)
# r = c.execute(query)
# print "right table", r.fetchone()[1]



# gifters = [
# 	{'olaoluwa.ogunwa@rimonlaw.com' : ['Bedminster', 'Boston', 'Jerusalem', 'Miami', 'New York', 'Newark', 'Northern Virginia', 'NYC', 'Orlando', 'Research Triangle', 'Tel Aviv', 'Washington, D.C.', 'DC'] },
# 	{'oluwafadekemmie@gmail.com' : ['Chicago', 'Dallas', 'Minneapolis'] },
# 	{'fadekemmie@yahoo.com' : ['Lake Tahoe', 'Las Vegas', 'Los Angeles', 'Orange County', 'Palo Alto', 'Menlo Park', 'Silicon Valley', 'Portland', 'Sacramento', 'San Diego', 'San Francisco', 'Seattle'] },
# 	{'olarimonuipathquiz@gmail.com', ['-'] }

# ]
