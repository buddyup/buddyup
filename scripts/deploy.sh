#!/bin/sh
echo "Deploying Hudson"
git push heroku-hudson-buddyup
echo "Deploying Template"
git push heroku-template-buddyup
echo "Deploying OIT"
git push heroku-oit-buddyup
echo "Deploying OSU"
git push heroku-oregonstate-buddyup
echo "Deploying OSU ecampus"
git push heroku-ecampus-oregonstate-buddyup
echo "Deploying PSU"
git push heroku-buddyup
