ultimate-league-app
===================

Ultimate Frisbee League Web Application

## Install Development Environment

Start in the root of `ultimate-league-app`
```bash
./bin/mkvenv.sh dev
cd src/
npm install
cp ultimate/settings/base.py.dist base.py
cp ultimate/settings/dev.py.dist dev.py
```
You will then want to update the `base.py` and `dev.py`. Mainly, you need your database credentials. Other stuff toward the bottom is necessary for full functionality (e.g. Google Cal, PayPal, etc.).

## Run the Development Environment

Again from the the root of `ultimate-league-app`, you will use two different terminal tabs/windows for this:

```bash
source env/dev/bin/activate
cd src/
./manage.py runserver_plus
```

```bash
cd src/
npm run dev
```


## Update a Production Environment

Once you are deployed in production, you can pull new code and update with the following:

```bash
git pull
source env/prod/bin/activate
cd src/
./manage.py migrate
npm run build
./manage.py collectstatic
```

Then, you will want to restart your server service.
