from flask import Flask, abort, Response
from notion_servers_count import get_page, any_count, reduce_and_try_date, which_conf
from github_prox import get_config_from_github
from threading import Thread
import logging

app = Flask(__name__)

@app.route("/<id_str>", methods=['GET'])
def get_json_data(id_str):
    the_page = get_page(id_str)
    
    if the_page:
        if any_count(the_page):

            path = which_conf(the_page)

            if path == 'private':
                path = f"/private/{id_str}"
            else:
                path = f"/public/{path}"
            conf = get_config_from_github(path)

            if not conf == "Not Found":
                thread_add_try_date = Thread(target=reduce_and_try_date, args=(the_page, True, id_str, path))
                thread_add_try_date.start()

                return conf
            else:
                thread_add_try_date = Thread(target=reduce_and_try_date, args=(the_page, False, id_str, path))
                thread_add_try_date.start()

                abort(Response("FileNotFound\n\ncontanct support: @krowcy", 406))
        else:
            thread_add_try_date = Thread(target=reduce_and_try_date, args=(the_page, False, id_str, None))
            thread_add_try_date.start()

            abort(Response("\nYou can use this URL just once.\n\ncontact support: @krowcy", 401))
    else:
        abort(Response("\nUser not found", 404))

if __name__ == "__main__":
    logging.basicConfig(level = logging.INFO,
                        format = '%(message)s')
    app.run(host="0.0.0.0", port=80)
