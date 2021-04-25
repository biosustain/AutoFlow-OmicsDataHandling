                                                            Backend Doc
In order to execute code first time please follow following steps 

$ flask db init

This will add a migrations folder to your application. The contents of this folder need to be added to version control along with your other source files.

$ flask db migrate -m "Initial migration."

You can then generate an initial migration:


Then you can apply the migration to the database:

$ flask db upgrade

Then each time the database models change repeat the migrate and upgrade commands.

To run the application you can either use the flask command or python’s -m switch with Flask. Before you can do that you need to tell your terminal the application to work with by exporting the FLASK_APP environment variable:

$ export FLASK_APP=hello.py
$ flask run
 * Running on http://127.0.0.1:5000/
 
                                                                OR
                                
  In order to execute code second time onwards please follow following steps 
  
  $ flask db migrate -m "Second migration."

You can then generate an initial migration:


Then you can apply the migration to the database:

$ flask db upgrade

Then each time the database models change repeat the migrate and upgrade commands.

To run the application you can either use the flask command or python’s -m switch with Flask. Before you can do that you need to tell your terminal the application to work with by exporting the FLASK_APP environment variable:

$ flask run
 * Running on http://127.0.0.1:5000/