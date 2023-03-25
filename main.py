from app import app
from flask import flash, session, render_template, request, redirect, url_for

@app.route('/')
def produtos():

    return render_template('index.html')


if __name__ == "__main__":
    app.run()