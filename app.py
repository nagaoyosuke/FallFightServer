import os
import psycopg2
from FlaskServer import app,Set_DBPass

if __name__ == '__main__':
  # Set_DBPass(os.environ["DATABASE_URL"])
  app.run(host='0.0.0.0')
