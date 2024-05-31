#!/bin/bash
export DATABASE_URL="postgresql+psycopg2://sarbanidas@localhost:5432/postgres"
export EXCITED="true"
export AUTH0_CLIENT_ID='54gqvo1PWQDifjHKJ5fCnIdmQXBw3H8v'
export AUTH0_CLIENT_SECRET=CXMW0rq4qmj7fs4wLVf6uJl14q6Nb9UfXXfV6ESEtyfc0p3Eov5UoitYPIlmdXYC
export AUTH0_DOMAIN=audacity-fsnd-sarbani.uk.auth0.com
export APP_SECRET_KEY=mysupersecretkey  
echo "setup.sh script executed successfully!"

# postgres://usryfdfgywnsgl:04c3ded6d767ee72d40dbc0912c9e7ff0b9e2a1a61581ecc7ba73fac70f2787a@ec2-54-157-172-245.compute-1.amazonaws.com:5432/dfb2q4q3jcgbkm