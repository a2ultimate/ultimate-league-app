# ultimate-league-app

Ultimate Frisbee League Web Application

## Install Development Environment

Start in the root of `ultimate-league-app`

```bash
./bin/mkvenv.sh dev
cd src/static
npm install
```

## Run the Development Environment

Again from the the root of `ultimate-league-app`, you will use two different terminal tabs/windows for this:

```bash
source venv/dev/bin/activate
cd src/
./manage.py runserver_plus
```

```bash
cd src/static
npm run dev
```

## Update a Production Environment

Once you are deployed in production, you can pull new code and update with the following:

```bash
git pull
source env/prod/bin/activate
cd src/
pip install -r requirements/prod.txt
./manage.py migrate
cd static/
npm run build
./manage.py collectstatic
```

_Do not forget to check for settings changes!_

Then, you will want to restart your server service.
