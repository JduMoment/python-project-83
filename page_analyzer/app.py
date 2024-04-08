from flask import Flask, render_template
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

__all__ = ['first_page']


@app.route('/')
def first_page():
    return render_template('index.html')


# if __name__ == '__main__':
#     app.run(port=8080, debug=True)
