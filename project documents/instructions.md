Udacity is creating a new cafe on campus for students to drink coffee and study hard. They've test you with the responsibility of creating a digital menu so everyone knows what drinks are available at any given point in time. Through this exercise, we want you to demonstrate your ability to secure an API and assign roles to particular users. We provided you some of the starter code to get started on this project, but your task is to secure the restful API in the Flask server and connect the front end using some simple configuration options. You'll be using authXero to perform the bulk of the hosted authentication service. We provided a simple front end using the ionic framework to get you started on this project. This front end will connect to the back end service you'll be securing to access a SQL database of drinks. It renders these drinks on the screen with some very simple little representations of graphics. Let's say we wanted to add a new drink. We can login as a user, in my case I'm a barista, I'll login with my Google credentials which returns us to the website with our JWT. Now, we have a new create drink option that's turned on because this user has that permission. I can go ahead and create a new drink. We're going to call it the Udaci-spice latte and we're going to add some information to this drink. So our ingredient list we're going to have some blue foam at the top and we're going to have let's say one part of that, and then we'll add some nice blueberry drink. This will be our beautiful Udacity blue and we want some let's say, two parts of that blue drink there. Saving this will add that information to our database. Now even if we log out, our drink menu persists and our students know what's available in our cafe.

What will I build?
You have been called on to demonstrate your newly learned skills to create a full stack drink menu application. The application must:

Display graphics representing the ratios of ingredients in each drink.
Allow public users to view drink names and graphics.
Allow the shop baristas to see the recipe information.
Allow the shop managers to create new drinks and edit existing drinks.
This project will give you a hands-on chance to practice and demonstrate what you've learned in this lesson, such as:

Implementing authentication and authorization in Flask
Designing against key security principals
Implementing role-based control design patterns
Securing a REST API
Applying software system risk and compliance principles