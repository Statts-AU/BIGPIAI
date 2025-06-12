from app import create_app, socketio
app = create_app()


if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)


# if __name__ == '__main__':
#     socketio.run(app, host='0.0.0.0', port=5000, debug=False,use_reloader=False)


# for running production level code :
# waitress-serve --listen=0.0.0.0:80 app:app
# Previously ,  waitress-serve --listen=0.0.0.0:80 run:app
# start waitress-serve --listen=0.0.0.0:80 myproject:app
