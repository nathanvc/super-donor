# super-donor
Web app interface for a project to detect distinct donors IDs in the [Donor Sibling Registry](http://donorsiblingregistry.com) most likely to represent the same person. Project built as part of the [Insight Health Data Science](http://insighthealthdata.com) program. Distance prediction uses Large Margin Nearest Neighbor metric-learning. File LMNN_mat5 contains the metric learned space transformation that produces the distance measure. 

See web-site at [http//:super-donor.com] (https://super-donor.com)

Dependencies:
Flask
Numpy
Pandas
PostgreSQL 9.5

Program must have access to postgres database. Postgres "dump" of database is available here in the file dsr_db5_out
Provided you have postgres installed and running, database can be recovered in a format compatible with this code using the command psql dsr_db5<dsr_db5_out from inside the super-donor folder. 

Nathan Vierling-Claassen, Ph.D. 2016
