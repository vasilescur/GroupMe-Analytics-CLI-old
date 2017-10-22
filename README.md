# GroupMe Analytics
Scans a GroupMe chat and generates insightful message and like analytics.

## [Online Demo](http://vasilescur.github.io/GroupMe-Analytics)
You can view the analytics for my groupchat with 3 friends (called "Polyinstrumental Cacophony") at this link. To make this nice presentation format, I used the analytics my Python script gave me, and placed them into some JS code using the Google Charts API in a simple HTML page.

## Generating the Statistics
To generate the statistics, I used a Python script. Called `groupme-analytics.py`, it pulls down messages from GroupMe's API in chunks of 20 and analyzes them. After being sorted by user, they are counted and analyzed to produce the metrics you see in the results.


## Displaying the Results
I created a custom webpage from scratch to display the results, using HTML and CSS. I utilized the Google Charts JavaScript library in my page to create a variety of charts to visualize the data. Then, I entered the values by hand from my Python script's output into the HTML and JS webpage.



