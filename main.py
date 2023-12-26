from flask import Flask, abort, Response
import os
from notion_servers_count import get_pages, find_id, any_count, reduce_and_try_date, which_conf
from threading import Thread
import logging

app = Flask(__name__)

@app.route("/<id_str>", methods=['GET'])
def get_json_data(id_str):
    pages = get_pages(200)
    the_page = find_id(id_str, pages)
    
    if the_page:
        if any_count(the_page):

            conf = which_conf(the_page)

            if conf == 'private':
                file_path = os.path.join(os.path.dirname(__file__), f'proxy-config/private/{id_str}')
            else:
                file_path = os.path.join(os.path.dirname(__file__), f'proxy-config/public/{conf}')

            try:
                with open(file_path, 'r') as file:
                    file_contents = file.read()

                logging.info(f"return conf: {file_path}")

                thread_add_try_date = Thread(target=reduce_and_try_date, args=(the_page, True))
                thread_add_try_date.start()

                return file_contents
            
            except FileNotFoundError as fnf_error:
                logging.info(fnf_error)

                thread_add_try_date = Thread(target=reduce_and_try_date, args=(the_page, False))
                thread_add_try_date.start()

                abort(Response("FileNotFound\n\ncontanct support: @krowcy", 406))
        else:
            thread_add_try_date = Thread(target=reduce_and_try_date, args=(the_page, False))
            thread_add_try_date.start()
            
            abort(Response("\nYou can use this URL just once.\n\ncontact support: @krowcy", 401))
    else:
        abort(Response("\nUser not found\n\nneed support? @krowcy", 404))

if __name__ == "__main__":
    logging.basicConfig(level = logging.INFO,
                        format = '%(message)s')
    app.run(host="0.0.0.0", port=80)
