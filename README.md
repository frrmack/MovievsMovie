# Movie vs Movie 

This is the source code for [movievsmovie.datasco.pe](http://movievsmovie.datasco.pe)

## Screenshots

![](http://i.imgur.com/2HA3NK1.gif)
----
----


## Talk explaining the data science behind Movie vs Movie

Watch the talk on vimeo
[![Watch the talk on vimeo](http://i.imgur.com/BabK3Uu.jpg)](https://vimeo.com/manwithacam/review/116993043/c23ac72429)

Slides on slideshare
[![Slides](http://i.imgur.com/2BmVDIR.png)](http://www.slideshare.net/frrmack/the-anatomy-of-a-data-science-project)

## What's your top ten? 

This is a very hard question to answer. Research has shown that when we rate movies, the rating depends a lot on our mood, what we've seen/rated lately, etc.

Rating movies is sensitive to environmental factors. Our memories cannot evalute the entirety of all movies we have seen, so every time we rate a movie, even though it feels like an ultimate rating, we are really comparing it to a limited set.

As an example, if we rate a lot of movies in succession and they are all movies we are fond of, our grading becomes a lot more strict, without us noticing it. This is because the human brain is great at adaptation, pattern recognition, and setting a baseline.

This is generally very useful, but in this case it becomes harder to find out which movies you truly like best, or to have a complete, continuous ranking that doesn't depend on different conditions of each rating session.

### Star ratings 

A star rating (1-5 stars out of 5) is a good starting point to get a general idea of where the movie is: towards the top, the middle, or the bottom of your rankings.

However, it does not have enough resolution for a continuous ranking, and it is sensitive to factors like our limited memory. In a moment of rating, we cannot analyze a movie in the context of our entire library of movies. Instead we think of a much smaller subset.

Trying to use a high resolution grading system (like out of 1-100 or 1-10 with a decimal place) makes ratings even more sensitive to such problems. Let's say you rate two movies. You may give a 7.8 to film A today, and 7.6 to film B a few weeks later, even if you would have said that you like B better than A on either day.

For a movie, we start by asking you to give a star rating out of five. Then, we get a better idea of how much you really like it from one on one fights against other movies.

### Head to head fights 

To rank movies, we need high resolution scores. Directly rating on such a scale is unreliable. Instead, we get there through one to one comparisons.

When you determine the winner (or draw) of a fight, scores change according to the result. The score for each movie starts as your star rating. Changes after a fight depend on the previous scores.

Let's say Casablanca had a score of 5.4, and The Matrix had 4. If The Matrix beats Casablanca, its score goes up quite a bit and Casablanca's score drops significantly. However, if The Godfather has a score of 4.7, and Troll 2 has a score of 1.4, and The Godfather wins, the scores don't really change much, because that was already expected.

Also, Movie vs Movie learns much more from the first fights of a movie than its hundredth, since we do not have much uncertainty left by then.

## Who made this? 

* [Irmak Sirer](http://irmaksirer.com)
