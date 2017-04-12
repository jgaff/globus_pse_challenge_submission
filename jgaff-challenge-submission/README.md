#Globus PSE Coding Challenge Submission
Applicant: Jonathon Gaff

##Steps to run application
###Step 1: Create a Python 3 environment
Install Python 3 if necessary.
```
$ virtualenv -p python3 venv
$ . venv/bin/activate
```

###Step 2: Untar the challenge archive (if using the archived version) and enter the directory
```
$ tar -xzvf jgaff-challenge.tar.gz
$ cd jgaff-challenge-submission
```

###Step 3: Install the required packages
```
$ pip install -r requirements.txt
```

###Step 4: Start the Flask server
Option 1:
```
$ python3 challenge_api.py
 * Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)
```
Option 2:
```
$ export FLASK_APP=challenge_api.py
$ flask run
 * Serving Flask app "challenge_api"
 * Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)
```

###Step 5: Load the web page
Open `jgaff-challenge-submission/index.html` in a browser that supports Cross-Origin Resource Sharing (CORS) and HTML5.
Examples of suitable browsers: Mozilla Firefox 52, Google Chrome 57.

###Step 6: Type a Twitter user ID into the input field and click "Get Tweets"
Up to the last 20 tweets by that user will appear.