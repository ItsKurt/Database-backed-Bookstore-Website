By: Kurt Mueller

#################################################
DEPLOYING THE PROJECT:

Creating your Virtual Environment:

On Windows:

$ py -3 -m venv venv
$ venv\Scripts\activate

$ pip install Flask
$ pip install mysql-connector-python
$ pip install passlib
$ pip install -U WTForms

Now run main.py in this virtual environment to start up the website.

As for the Database, you will need to install MariaDB. The database should follow these credentials:

host='localhost'
user='431user'
passwd='bookstore'
database='Bookstore'

Included in the Bookstore project\projectFiles\table_queries folder is a bookStoreCreation.sql file that creates all of the tables needed for the database and populates them. Also included in this folder are four python scripts I used for scraping the books.csv file and populating the tables.

#################################################
TOOLS USED FOR THE PROJECT:

-Python and FLASK for my web framework and backend development
-Bootstrap, HTML, and very little CSS for frontend development
-PyCharm IDE for all coding
-MariaDB for my database
-HeidiSQL for visualizing my database

#################################################
FUNCTIONALITY AND CONTROL FLOW:

User Login/Logout and Registration:
When entering the system, you will be prompted to Sign In or Create and Account. The buttons are shown on the home page. When creating a new account, your Login Name must be unique so no other user has the same name. It will check for this an alert you if it has been taken already. You cannot access any of the features of the website until you are signed in. You are also able to Logout by pressing the green "Logout" button in the top right corner on the navigation bar.


Browsing Books:
On the navigation bar, press "Search Books". This page shows 100 books at a time to so that the page doesn't have too hard of a time. You are able to enter keywords in the "Search for Books" search box and you can select what your keyword correlates with (Title, Author, Publisher, Language). In the same form, you can sort by the book's publication date and Rating made by the comments other made on the books. To sort the searched books, you must enter the keyword(s) and specify the sort BEFORE pressing search. Each book title shown can be pressed to take you to a page that shows all the information about the books (specific book page).


Specific Book Pages:
On this page, users can add any number of copies of the to their shopping cart as long as there is enough in stock. When books are added to the cart, the stock is lowered, if it is removed from the shopping cart, the copies are put back in stock. Users are also able to see comments made by other users and even sort them to see the top n most useful comments. Users can then rate these comments as "useless", "useful", or "very useful". The number of each of these ratings a comment gets is stored and used to calculate the usefulness score of the comments. Obviously users can also write comments by clicking the "Write a Comment" button above the comments. After the form is completed for making a comment, it will appear on the book page and if you are the creator of the comment, a "edit comment" and "delete comment" button will be shown on the comment (these do what you would expect). Lastly, users can press the "Request More Copies of this Book" button at the top right of the page to post a request that they want more copies of this book in stock so managers can see what customers want. If you are a manager, there is an option to "Add more copies" where you can enter the number of books you want to add to the stock to fulfill requests made by customers.


More on Comments:
As previously stated, comments can be made on the book page for a specific book. When a comment is created by pressing the light blue "Write a Comment" button, the book's rating is adjusted because the book's numRatings attribute is increased by one. And when the book page is loaded, the book's rating is calculated by taking the average of all of the Book Ratings in the comments made about the book by dividing the total of the ratings by numRatings. Users are able to see all comments made on the book through the bottom of the book page and can show the top n comments based on usefulness if they would like. You are also able to rate comments made by other users by "useless", "useful", or "very useful". If the comment is your own, you can see "edit comment" and "delete comment" buttons which can be pressed to do exactly would you would expect and when a bookRating is changed or a comment is deleted, the book's rating is properly adjusted.


Book Recommendations: 
To see a list of books recommended for you based on books you have purchased, you can click "Recommended Books" on the navigation bar. You will also automatically be redirected to this page after completing an order.


Degrees of Separation Search:
To look up books related to a given author by degrees of separation, you can press "Degrees of Separation Book Search" on the navigation bar. On this page you are prompted to enter the author name you wish to search off of and submit this author for search by pressing the "search" button. This will the supply a list of books related to the entered author and will show the books given by degree one relationships first and second degree after. The book titles can be clicked on to bring you to the book's page.


Placing an Order:
As previously mentioned, on the book page for a specific book you can enter the "copies wanted" and press "Add to Cart" when you enter the number of copies you would like. This is then added to your user's SHOPPING CART. You can access the shopping cart by pressing the orange "Shopping Cart" button on the right end of the navigation bar. Here all of items you added to your cart are listed and you are able to remove items easily be pressing "Remove item" button on the specific item you would like removed. This adds the book(s) back to the stock and removes the item(s) from your shopping cart. If you would like to complete your order after seeing the total price shown, you can press the green "checkout" button. This will put all of the contents of your shopping cart into and order and will clear your shopping cart since the order is complete.


Orders:
When you make an order, you can easily see your previous orders by pressing "Profile" on the left end of the navigation bar and clicking the "Order History" button on your PROFILE PAGE. Here you can see all your orders you have made and the date and time they were made. You can click on the order IDs to bring you to a page that shows all of the details of the order like what items were in it and how much it costed.


Trusted or Un-trusted Users:
When visiting another user's profile page, you can click "Mark as Trusted" or "Mark as Un-trusted" to mark the specific user as trusted or un-trusted respectively. When these buttons are clicked a record is created in the trust table and the user being marked has their trust score increased by one if they are being marked as trusted or decreased by one of they are being marked as un-trusted. You can't mark a user as trusted or un-trusted more than once, but you can switch from having them marked as trusted or un-trusted by and the trust score for that user will be properly adjusted to reflect this change.


User Profile Pages:
By pressing "Profile" on the left end of the navigation bar, you are brought to your profile page where you can access the comments you have made, with links back to the book pages that the comments were made on. You can also see your order history as previously mentioned, all of your information like name, address, phone number, etc., the books you own based on the items in the orders you have made, and you can see the users you have marked as Trusted or Un-trusted. Lastly, if it is your profile page that you are looking at, a green "Change Password" button is above your name that you can click to change your password by filling out a form that is validated. As for seeing another user's profile page, you can access these by pressing their names on comments they have made, typing in "/profile/user'sloginName/" onto the url or other places around the store where names are listed. If you are a manager you can see all the users through the ADMIN PAGE. When you are on another user's profile page, you can mark them as trusted or un-trusted by clicking the corresponding buttons above their name. You can also see the comments they have made and users they have marked as trusted or un-trusted. The other information that you could see on your own profile like order history and books owned are not able to be accessed unless you are a manager for privacy. If a user has received an AWARD at any point, they will receive a gold header on their page saying that they are an awarded user and they will also be displayed on the website's home page.


Admin Page and Manager Access:
If you are signed in to an account that is a manager (if isManager attribute equals 1), a blue "Admin Page" button is shown at the right end of the navigation bar. On this page, managers can press "User Stats" to find the top n most trusted or useful users and can promote or demote users from manager positions as well as give user's awards if they would like. Next, managers can press "Requests" to see the list of requests for more copies of a book that users have made. Managers can press the link to the book requested on the request and add more copies on the book's page. When more copies are successfully added, the requests affiliated with that book are deleted. Managers can also press "Orders" to see the list of all of the orders made in the system. From this page you can see who made the order and can press on the order ID to see what exactly was in the order. You can also see the date and time that the order was made, the orders are sorted by showing the most recent orders at the top. Additionally, managers can click "Add a Book" to be brought to a form where they can add all of the required details of new book they would like add to the system. The book will be added to the list of books the store has and the authors table will be updated to show the book and authors that wrote it as well. Lastly, by pressing "Book Stats" on the admin page, managers can get the top n most popular books, authors, and publishers based on the copies sold of the books in the system.

#################################################



