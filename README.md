# Team Chickaree Small Group project

## Team members
The members of the team are:
- Michael Mulianto
- Kieran Woolley
- John Kelly
- Liam Clark Gutiérrez
- Kanishk Upadhyay

*Add any further information about the team here, such as absent team members.*

## Project structure
The project is called `system`.  It currently consists of a single app `clubs`.

## Deployed version of the application
The deployed version of the application can be found at [URL](URL).

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

*The above instructions should work in your version of the application.  If there are deviations, declare those here in bold.  Otherwise, remove this line.*

## Seeding and Useful Test Accounts
Seeding provides some nice test accounts, most mandated by the project non-functional requirements.
All superusers should be created locally as they are not used in the deployed application: seeding and unseeding won't impact these.

All passwords are "Password123"
  - testuser1 / test@example.org (This covers edge cases useful for testing)
  - Jebediah142 / jeb@example.org
  - Valentina123 / val@example.org
  - Billie444 / billie@example.org

## Sources
The packages used by this application are specified in `requirements.txt`

Some code is borrowed from the Clucker application developed in the SEG practice video series.
Main sources are:
  - [https://docs.djangoproject.com/en/4.0/]Django documentation.
  - [https://getbootstrap.com/docs/5.1/getting-started/introduction/]Bootstrap 5 documentation.

While all code is original, Stack overflow and other online resources is occasionally used as reference to fix problems or guide implementaion. Some notable references are:
  - [https://stackoverflow.com/questions/1455126/unique-booleanfield-value-in-django]Single boolean constraint implementation mechanism.
