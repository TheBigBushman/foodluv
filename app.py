import os
from flask import (
    Flask, flash, render_template,
    redirect, request, session, url_for)
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
if os.path.exists("env.py"):
    import env


app = Flask(__name__)

app.config["MONGO_DBNAME"] = os.environ.get("MONGO_DBNAME")
app.config["MONGO_URI"] = os.environ.get("MONGO_URI")
app.secret_key = os.environ.get("SECRET_KEY")

mongo = PyMongo(app)


@app.route("/")
@app.route("/home")
def home():
    recipes = mongo.db.recipes.find()
    return render_template("home.html", recipes=recipes)


@app.route("/get_recipes")
def get_recipes():
    recipes = mongo.db.recipes.find()
    return render_template("recipes.html", recipes=recipes)


@app.route("/register", methods={"GET", "POST"})
def register():
    if request.method == "POST":
        # check if username exists
        existing_user = mongo.db.users.find_one(
            {"username": request.form.get("username").lower()})

        if existing_user:
            flash("Username already exists")
            return redirect(url_for("login"))
        # Registers user
        register = {
            "username": request.form.get("username").lower(),
            "password": generate_password_hash(request.form.get("password"))
         }
        mongo.db.users.insert_one(register)

    # put the user into session cookie
        session["user"] = request.form.get("username").lower()
        flash("Registration Successful")
        return redirect(url_for("profile", username=session["user"]))
    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        # check if username exists in db
        existing_user = mongo.db.users.find_one(
            {"username": request.form.get("username").lower()})

        if existing_user:
            # ensure hashed password matches user input
            if check_password_hash(
                    existing_user["password"], request.form.get("password")):
                    session["user"] = request.form.get("username").lower()
                    flash("Welcome, {}".format(request.form.get("username")))
                    return redirect(url_for(
                            "profile", username=session["user"]))
            else:
                # invalid password match
                flash("Incorrect Username and/or Password")
                return redirect(url_for("login"))

        else:
            # username doesn't exist
            flash("Incorrect Username and/or Password")
            return redirect(url_for("login"))

    return render_template("login.html")


@app.route("/profile/<username>", methods=["GET", "POST"])
def profile(username):
    # gets session users name from db
    username = mongo.db.users.find_one(
        {"username": session["user"]})["username"]
    return render_template("profile.html", username=username)

    if session["user"]:
        return render_template("profile.html", username=username)

    return redirect(url_for("login"))


@app.route("/logout")
def logout():
    # logs out user
    flash("You have been successfully logged out")
    session.pop("user")
    return redirect(url_for("login"))


@app.route("/add_recipe", methods={"GET", "POST"})
def add_recipe():
    if request.method == "POST":
        recipe = {
            "recipe_name": request.form.get("recipe_name"),
            "cuisine_name": request.form.get("cuisine_name"),
            "preperation": request.form.get("preperation"),
            "ingredients": request.form.get("ingredients"),
            "time_to_cook": request.form.get("time_to_cook"),
            "difficulty": request.form.get("difficulty"),
            "created_by": session["user"]
        }
        mongo.db.recipes.insert_one(recipe)
        flash("Recipe Successfully Added")
        return redirect(url_for("get_recipes"))

    cuisine = mongo.db.cuisine.find().sort("cuisine_name", 1)
    return render_template("add_recipe.html", cuisine=cuisine)


@app.route("/edit_recipe/<recipe_id>", methods=["GET", "POST"])
def edit_recipe(recipe_id):
    if request.method == "POST":
        submit = {
            "recipe_name": request.form.get("recipe_name"),
            "cuisine_name": request.form.get("cuisine_name"),
            "preperation": request.form.get("preperation"),
            "ingredients": request.form.get("ingredients"),
            "time_to_cook": request.form.get("time_to_cook"),
            "difficulty": request.form.get("difficulty"),
            "created_by": session["user"]
        }
        mongo.db.recipes.update({"_id": ObjectId(recipe_id)}, submit)
        flash("Recipe Successfully Updated")

    recipe = mongo.db.recipes.find_one({"_id": ObjectId(recipe_id)})
    cuisine = mongo.db.cuisine.find().sort("cuisine_name", 1)
    return render_template("edit_recipe.html", recipe=recipe, cuisine=cuisine)


@app.route("/delete_recipe/<recipe_id>")
def delete_recipe(recipe_id):
    mongo.db.recipes.remove({"_id": ObjectId(recipe_id)})
    flash("Recipe Deleted")
    return redirect(url_for("get_recipes"))


@app.route("/get_cuisines")
def get_cuisines():
    cuisine = mongo.db.cuisine.find().sort("cuisine_name", 1)
    return render_template("cuisines.html", cuisine=cuisine)


@app.route("/add_cuisine", methods=["GET", "POST"])
def add_cuisine():
    if request.method == "POST":
        cuisine = {
            "cuisine_name": request.form.get("cuisine_name")
        }
        mongo.db.cuisine.insert_one(cuisine)
        flash("New cuisine added")
        return redirect(url_for("get_cuisines"))

    return render_template("add_cuisine.html")


@app.route("/edit_cuisine/<cuisine_id>", methods=["GET", "POST"])
def edit_cuisine(cuisine_id):
    if request.method == "POST":
        submit = {
            "cuisine_name": request.form.get("cuisine_name")
        }
        mongo.db.cuisine.update({"_id": ObjectId(cuisine_id)}, submit)
        flash("Cuisine Updated")
        return redirect(url_for("get_cuisines"))

    cuisine = mongo.db.cuisine.find_one({"_id": ObjectId(cuisine_id)})
    return render_template("edit_cuisine.html", cuisine=cuisine)


@app.route("/delete_cuisine/<cuisine_id>")
def delete_cuisine(cuisine_id):
    mongo.db.cuisine.remove({"_id": ObjectId(cuisine_id)})
    flash("Cuisine Deleted")
    return redirect(url_for("get_cuisines"))


if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            debug=False)
