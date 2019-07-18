from routes import *
app.register_blueprint(routes)

if __name__ == '__main__':
      app.run(host='0.0.0.0', port=2000)