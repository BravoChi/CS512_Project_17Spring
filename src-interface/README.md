# Interface of SetSearch Web System
SetSearch: A Set-Oriented and Entity-Aware Search  System for Biomedical Literature Web System

This repo is the interface of the system including Flask and React.

```
(sudo) pip install virtualenv
virtualenv venv 
source venv/bin/activate
(sudo) pip install -r requirements.txt
(sudo) npm install -g webpack; 
(sudo) npm install
```

Then run `python app.py`
Make edits to `js/app.js` and `app.py` to edit the frontend and backend, respectively.

## Improvements in next step

- add in author, jounral information
- better highlight terms with colors
- obtain frequent entities in the right column

- user login and upload files (for indexing)


## Prerequisites

You'll need some package managers.

- `npm`
- `pip`

## Setup

For the backend:

```
virtualenv venv
source venv/bin/activate
(sudo) pip install -r requirements.txt
```

For the frontend:

If you don't have webpack, install it:

```
(sudo) npm install -g webpack
```

Then, use `npm` to install the remaining JavaScript dependencies.

```
(sudo) npm install
```

highlight lib:
mark.js

## Development

The entry point for the app is in `js/app.js`. 

While developing on the Frontend, run `webpack --watch` to keep re-compiling your JavaScript code.

Running `webpack` creates a file in `static/bundle.js`, which is the bundled version of your frontend code.

The "backend" here is a bare-bones Flask app. Look in `app.py` if you want to make edits to the backend.

To run the application, follow the steps in the next section.

The test json data is in `templates/data/sample.json`.

![alt tag](/static/SetSearch-3.png)

## Running the app

If you're using a virtualenv, activate it.

```
source venv/bin/activate
```

Then run the Flask app:

```
python app.py
```

Finally, open your web browser and type into:

```
http://localhost:5002/
```
Example: Previous results, random color (in order)
![alt tag](/static/SetSearch-5.png)
Example: Different entities has different colors
![alt tag](/static/SetSearch-6.png)
Example: Two connected entities
![alt tag](/static/SetSearch-7.png)
Example: Different entities, two of them has same color
![alt tag](/static/SetSearch-8.png)
