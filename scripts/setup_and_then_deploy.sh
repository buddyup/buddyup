

heroku git:remote -a hudson-buddyup -r heroku-hudson-buddyup git@heroku.com:hudson-buddyup.git --account buddyup
heroku git:remote -a oit-buddyup -r heroku-oit-buddyup git@heroku.com:oit-buddyup.git --account buddyup
heroku git:remote -a oregonstate-buddyup -r heroku-oregonstate-buddyup git@heroku.com:oregonstate-buddyup.git --account buddyup
heroku git:remote -a ecampus-oregonstate-buddyup -r heroku-ecampus-oregonstate-buddyup git@heroku.com:ecampus-oregonstate-buddyup.git --account buddyup
heroku git:remote -a buddyup -r heroku-buddyup git@heroku.com:buddyup.git --account buddyup

git push heroku-hudson-buddyup
git push heroku-oit-buddyup
git push heroku-oregonstate-buddyup
git push heroku-ecampus-oregonstate-buddyup
git push heroku-buddyup



