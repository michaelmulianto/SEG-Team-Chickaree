# Team Chickaree Small Group project

## Team members
The members of the team are:
- Michael Mulianto
- Kieran Woolley
- John Kelly
- Liam Clark Gutiérrez
- Kanishk Upadhyay

## Project structure
The project is called `system`.  It currently consists of a single app `clubs`.

## Deployed version of the application
The deployed version of the application can be found [here](https://lit-tundra-65931.herokuapp.com/).

## Installation instructions
To install the software and use it in your local development environment, you must first set up and activate a local development environment.  From the root of the project:

```
$ virtualenv venv
$ source venv/bin/activate
```

Install all required packages:

```
$ pip3 install -r requirements.txt
```

**As in Tools video 10.2, you may have to reinstall libpq-dev to remove errors if using Ubuntu 20.04:**

```
$ sudo apt-get install libpq-dev --reinstall
$ pip3 install -r requirements.txt
```

Migrate the database:

```
$ python3 manage.py migrate
```

Seed the development database with:

```
$ python3 manage.py seed
```

Run all tests with:
```
$ python3 manage.py test
```

**[optional, for deployment] Collect static files with:**
```
$ python3 manage.py collectstatic
```

## Seeding and Useful Test Accounts
Seeding provides some nice test accounts, most mandated by the project non-functional requirements.
Seeding does not impact superusers.
The deployed application is seeded.

All passwords are "Password123"
  - Jebediah142 / jeb@example.org
  - Valentina123 / val@example.org
  - Billie444 / billie@example.org

## Sources
The packages used by this application are specified in `requirements.txt`

Some code is borrowed from the Clucker application developed in the SEG practice video series.
Main sources are:
  - [Django documentation](https://docs.djangoproject.com/en/4.0/).
  - [Bootstrap 5 documentation](https://getbootstrap.com/docs/5.1/getting-started/introduction/).

While all code is original, Stack overflow and other online resources is occasionally used as reference to fix problems or guide implementaion. Some notable references are:
  - [Single boolean constraint implementation mechanism](https://stackoverflow.com/questions/1455126/unique-booleanfield-value-in-django).
  - [Sort list by diccionary values](https://www.geeksforgeeks.org/python-sort-list-by-dictionary-values/), used in get_winners() method.
  - [Date countdown as filter tag in template](https://stackoverflow.com/questions/47622089/django-template-counting-days-from-now-to-specific-date).
  - [Create basic custom template tags](https://stackoverflow.com/questions/6451304/django-simple-custom-template-tag-example), the concept is well now but unfamiliar to us and was often recommended as good practice.
