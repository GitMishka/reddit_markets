Project consist of creating sql tables to store new posts from r/gundeals, taking out price/catagory out of title for better logical processing.
Application sends out a text to user(me) with deals I specfied, putting those deals into another table for easier tracking.
There is a feature which moves aggregated data price by category into another database.
From new database this data sent into s3 bucket on AWS in csv format.
Dockorized app2