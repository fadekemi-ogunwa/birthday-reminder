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
		delete_query = "DROP TABLE " + table_name + ";"
		c.execute(delete_query)


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
	return {'kynyziah.shaw@rimonlaw.com' : ['Bedminster', 'Boston', 'Jerusalem', 'Miami', 'New York', 'Newark', 'Northern Virginia', 'NYC', 'Orlando', 'Research Triangle', 'Tel Aviv', 'Washington, D.C.', 'DC','Washington'],
	'silvia.alonso-falip@rimonlaw.com' : ['Chicago', 'Dallas', 'Minneapolis', 'Kansas'],
	'admin@rimonlaw.com' : ['Lake Tahoe', 'Las Vegas', 'Los Angeles', 'Orange County', 'Portland', 'Sacramento', 'San Diego', 'San Francisco', 'Seattle', 'Boise', 'Idaho'],
	'jessica.gonzalez@rimonlaw.com' : ['Palo Alto', 'Menlo Park', 'Silicon Valley'],
	'yaacov@rimonlaw.com': ['Not Available'] }

create_table()
