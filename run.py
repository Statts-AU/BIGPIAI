from app import app

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)


# for running production level code :
# waitress-serve --listen=0.0.0.0:80 app:app
# Previously ,  waitress-serve --listen=0.0.0.0:80 run:app
# start waitress-serve --listen=0.0.0.0:80 myproject:app
