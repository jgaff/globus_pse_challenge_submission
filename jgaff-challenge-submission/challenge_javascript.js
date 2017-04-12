/*
Javascript behind the Globus PSE Coding Challenge front end.
Author: Jonathon Gaff
*/


//In case of an error, clean up the tweet list before displaying the error
function showErr(err) {
    "use strict";
    var table = document.getElementById("tweetList");
    if (table !== null) {
        table.innerHTML = "";
    }
    document.getElementById("err").innerHTML = err;
}


//Takes the JSON return value from the challenge API and parses the tweets to the screen, if possible
function displayTweets(tweets_json) {
    "use strict";
    //Error check incoming JSON
    if (!tweets_json.success) {
        //404s are likely to be common, and so have a custom message
        if (tweets_json.error_code == 404) {
            showErr("Sorry, we couldn't find that user ID.\nError code: 404");
            return;
        //Anything else can just use the error given by the API
        } else {
            showErr("Sorry, there was an error getting those tweets.\nError code: " + String(tweets_json.error_code) + " - " + String(tweets_json.error_message));
            return;
        }
    }

    var all_tweets = tweets_json.tweet_list;
    //Find and/or make the table
    var table = document.getElementById("tweetList");
    if (table == null) {
        table = document.createElement("table");
        table.id = "tweetList";
        document.getElementById("main").appendChild(table);
    }
    //Don't keep any previous data
    table.innerHTML = "";

    //Extract information to display from each tweet, into the table
    //But do so in reverse, to keep the first tweets first
    all_tweets.reverse();
    all_tweets.forEach(function(tweet) {
        //Need two rows for the textCell rowspan and vertically stacked elements
        var row = table.insertRow(0);
        row.id = "r1";
        var row2 = table.insertRow(1);
        row2.id = "r2";

        var avatarCell = row.insertCell(0);
        var scNameCell = row2.insertCell(0);
        var textCell = row.insertCell(1);
        textCell.rowSpan = "2";
        var timeCell = row.insertCell(2);
        var replyCell = row2.insertCell(1);

        avatarCell.innerHTML = "<img src='" + tweet.user_profile_image + "' id='avatar' />";
        avatarCell.id = "avatarCell";
        scNameCell.innerHTML = "<p id='scName'>@" + tweet.user_screen_name + "</p>";
        scNameCell.id = "scNameCell";
        textCell.innerHTML = "<p id='text'>" + tweet.tweet_text + "</p>";
        textCell.id = "textCell";
        //Moment.js handles the relative timestamp
        timeCell.innerHTML = "<p id='time'>" + moment.unix(tweet.tweet_unix_timestamp).fromNow() + "</p>";
        timeCell.id = "timeCell";
        //"Hardcode" the reply button onclick call arguments to simplify
        replyCell.innerHTML = "<button type='button' id='reply' onclick='replyToTweet(\"" + tweet.tweet_text + "\", \"" + tweet.tweet_id + "\", \"" + tweet.user_id + "\")'>Reply</button>";
        replyCell.id = "replyCell";
    });

    document.getElementById("prompt").innerHTML = "Enter another user's ID:";
}


//Calls to the challenge API to get tweets, and handles basic input validation
function fetchTweets() {
    "use strict";
    document.getElementById("err").innerHTML = "";
    var userId = document.getElementById("userId").value.trim();

    //A Twitter user ID is a series of numbers, so valid input should look something like that
    if (!userId) {
        showErr("You must enter a user ID.");
        return;
    } else if (!(/^[0-9]+$/).test(userId)) {
        showErr("'" + String(userId) + "' is not a valid user ID.");
        return;
    }

    var requestUrl = "http://127.0.0.1:5000/tweets/" + userId;
    var request = new XMLHttpRequest();
    if (!"withCredentials" in request) {
        showErr("ERROR: CORS not supported in this browser.\nPlease update or change your browser.");
        throw new Error("CORS not supported");
    }
    request.onreadystatechange = function() {
        if (request.readyState === 4) {
            if (request.status == 200) {
                displayTweets(JSON.parse(request.responseText));
            } else if (request.status >= 500) {
                showErr("Sorry, there seems to be a server problem right now.\nPlease try again later.");
            } else if (request.status == 404) {
                showErr("Sorry, that user ID wasn't found.");
            } else if (request.status >= 400) {
                showErr("Sorry, that's not a valid user ID");
            } else if (request.status == 0) {
                showErr("Sorry, we couldn't get those tweets.");
            }
        }
    };
    request.open("GET", requestUrl, true);
    request.send();
}


//Dummy reply button
function replyToTweet(tweetText, tweetId, userId) {
    "use strict";
    var reply = prompt("Tweet " + tweetId + " by User " + userId + ":\n\n" + tweetText + "\n\n\nEnter your reply:");
}
