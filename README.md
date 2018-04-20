Jack Clegg - SI 364 - 4/20

NOTE: IT IS REQUIRED ON LINE 55 THAT YOU ADD AN OAUTH TOKEN FROM HERE:
https://beta.developer.spotify.com/console/get-search-item/?q=&type=&market=&limit=&offset=

My application is a website that allows users to login and access their saved playlists, and then rank these songs in their own order based on how much they like it. The application allows users to view a global average rating of every song in the database. The user also has the ability to change the way they rank a song, or delete a song from playlists. This application is different from my midterm as it saves every song in different playlists, and not just a library of songs. It allows more customization with the playlists and the ability to edit or delete songs from a playlist. It also allows users to view global averages.

Songs should ALWAYS BE ADDED LIKE: Songname, rank

Route: '/' -> index.html: Allows the user to view their playlists if they're logged in, search for a song already in the database, or create a new playlist and seed it with one song.

Route '/playlist_<name>' -> playlist_view.html: Allows you to view an individual playlist. Here, the user can click a link to add a song, delete the playlist, or click a link to edit a song on the playlist (the rating, the playlist it is on).

Route '/edit_song_<name>' -> edit_song.html: This lets you see all the playlists that this song is on for you, as well as a form to delete the song from certain playlists. You can also change the rank with the rerank form.

Route '/add_songs_<pname>' -> add_songs.html: This presents a form that allows you to add a song to a certain playlist.

Route '/all_songs' -> global_rankings.html: This presents every song in the database and its average ranking across all playlists / users. It also presents the data if you search a song from the home page.

Code Requirements
Note that many of these requirements of things your application must DO or must INCLUDE go together! Note also that you should read all of the requirements before making your application plan***.***

**Ensure that your SI364final.py file has all the setup (app.config values, import statements, code to run the app if that file is run, etc) necessary to run the Flask application, and the application runs correctly on http://localhost:5000 (and the other routes you set up). Your main file must be called SI364final.py, but of course you may include other files if you need.**

**A user should be able to load http://localhost:5000 and see the first page they ought to see on the application.**

**Include navigation in base.html with links (using a href tags) that lead to every other page in the application that a user should be able to click on. (e.g. in the lecture examples from the Feb 9 lecture, like this )**

**Ensure that all templates in the application inherit (using template inheritance, with extends) from base.html and include at least one additional block.**

**Must use user authentication (which should be based on the code you were provided to do this e.g. in HW4).**

**Must have data associated with a user and at least 2 routes besides logout that can only be seen by logged-in users.**

**At least 3 model classes besides the User class.**

**At least one one:many relationship that works properly built between 2 models.**

**At least one many:many relationship that works properly built between 2 models.**

**Successfully save data to each table.**

**Successfully query data from each of your models (so query at least one column, or all data, from every database table you have a model for) and use it to effect in the application (e.g. won't count if you make a query that has no effect on what you see, what is saved, or anything that happens in the app).**

**At least one query of data using an .all() method and send the results of that query to a template.**

**At least one query of data using a .filter_by(... and show the results of that query directly (e.g. by sending the results to a template) or indirectly (e.g. using the results of the query to make a request to an API or save other data to a table).

**At least one helper function that is not a get_or_create function should be defined and invoked in the application.**

**At least two get_or_create functions should be defined and invoked in the application (such that information can be saved without being duplicated / encountering errors).**

**At least one error handler for a 404 error and a corresponding template.**

**At least one error handler for any other error (pick one -- 500? 403?) and a corresponding template.**

**Include at least 4 template .html files in addition to the error handling template files.**

**At least one Jinja template for loop and at least two Jinja template conditionals should occur amongst the templates.**

**At least one request to a REST API that is based on data submitted in a WTForm OR data accessed in another way online (e.g. scraping with BeautifulSoup that does accord with other involved sites' Terms of Service, etc).**

**Your application should use data from a REST API or other source such that the application processes the data in some way and saves some information that came from the source to the database (in some way).**

**At least one WTForm that sends data with a GET request to a new page.**

**At least one WTForm that sends data with a POST request to the same page. (NOT counting the login or registration forms provided for you in class.)**

**At least one WTForm that sends data with a POST request to a new page. (NOT counting the login or registration forms provided for you in class.)**

**At least two custom validators for a field in a WTForm, NOT counting the custom validators included in the log in/auth code.**

**Include at least one way to update items saved in the database in the application (like in HW5).**

**Include at least one way to delete items saved in the database in the application (also like in HW5).**

**Include at least one use of redirect.**

**Include at least two uses of url_for. (HINT: Likely you'll need to use this several times, really.)**

**Have at least 5 view functions that are not included with the code we have provided. (But you may have more! Make sure you include ALL view functions in the app in the documentation and navigation as instructed above.)**

Additional Requirements for additional points -- an app with extra functionality!
Note: Maximum possible % is 102%.

(100 points) Include a use of an AJAX request in your application that accesses and displays useful (for use of your application) data.
**(100 points) Create, run, and commit at least one migration.**
(100 points) Include file upload in your application and save/use the results of the file. (We did not explicitly learn this in class, but there is information available about it both online and in the Grinberg book.)
(100 points) Deploy the application to the internet (Heroku) — only counts if it is up when we grade / you can show proof it is up at a URL and tell us what the URL is in the README. (Heroku deployment as we taught you is 100% free so this will not cost anything.)
(100 points) Implement user sign-in with OAuth (from any other service), and include that you need a specific-service account in the README, in the same section as the list of modules that must be installed.
