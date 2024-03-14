from flask import  Flask, request

app = Flask(__name__)

@app.route('/webhookcallback',  methods=['POST'])
def webhookcallback():
    print(request.data)
    return "Hello world"

if __name__ == '__main__':
    app.run(debug=True)
