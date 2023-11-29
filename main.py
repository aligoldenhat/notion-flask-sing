from flask import Flask, abort, Response
import os
from notion_servers_count import get_pages, find_id, any_count, reduce_count, add_one_try, which_server
from threading import Thread
from time import sleep

app = Flask(__name__)

@app.route("/<id_str>", methods=['GET'])
def get_json_data(id_str):
    pages = get_pages(200)
    the_page = find_id(id_str, pages)
    
    if the_page:
        thread_add_one_try = Thread(target=add_one_try, args=(the_page,))
        if any_count(the_page):

            server = which_server(the_page)

            file_path = os.path.join(os.path.dirname(__file__), f'proxy-config/{server}/{id_str}')

            thread_reduce_count = Thread(target=reduce_count, args=(the_page,))
            try:
                with open(file_path, 'r') as file:
                    file_contents = file.read()

                print (f"return conf: {file_path}")

                thread_reduce_count.start()

                return file_contents
            
            except FileNotFoundError as fnf_error:
                print (fnf_error)
                thread_add_one_try.start()
                abort(Response("FileNotFound\n\ncontanct support: @krowcy", 406))
        else:
            thread_add_one_try.start()
            abort(Response("\nYou can use this URL just once.\n\ncontact support: @krowcy", 401))
    else:
        thread_add_one_try.start()
        abort(Response("\nUser not found\n\nneed support? @krowcy", 404))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80)
