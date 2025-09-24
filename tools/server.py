# Firefox has a big problem when developing JS.
# If the JS gets stuck in a loop forever, the debugging features in firefox don't work, because it is too busy running the JS or something I don't know.
# So instead just crash if we loop too many times.
# If you need to (generally if you have file level code), add // PUT_DEBUG_FOREVERLOOP_HERE somewhere. 


from http.server import HTTPServer as BaseHTTPServer, SimpleHTTPRequestHandler
import os


class HTTPHandler(SimpleHTTPRequestHandler):
    """Custom handler that modifies .js files before sending to client"""

    def translate_path(self, path):
        path = super().translate_path(path)
        relpath = os.path.relpath(path, os.getcwd())
        fullpath = os.path.join(self.server.base_path, relpath)
        return fullpath

    def do_GET(self):
        if self.path.endswith(".js"):
            self.serve_modified_js()
        else:
            super().do_GET()

    def serve_modified_js(self):
        print("test")
        filepath = self.translate_path(self.path)
        if not os.path.exists(filepath):
            self.send_error(404, "File not found")
            return

        try:
            with open(filepath, "r", encoding="utf-8") as f:
                js_content = f.read()

            # Modify the JavaScript content here
            modified_js = self.modify_js(js_content)

            self.send_response(200)
            self.send_header("Content-type", "application/javascript")
            self.send_header("Content-Length", str(len(modified_js.encode("utf-8"))))
            self.end_headers()
            self.wfile.write(modified_js.encode("utf-8"))
        except Exception as e:
            self.send_error(500, f"Error serving JS file: {e}")

    def modify_js(self, content):
        # Example modification: inject a console.log
        foreverloop_definition = "let __values = {}; function __check_no_forever_loop(n) {if (!(n in __values)) {__values[n] = 0;}; __values[n] += 1; if (__values[n]>10000) {__values = {};throw \"Too many iterations on line \" + n + \"\";}}"
        
        new = ""
        foreverloop_added = False
        for n, line in enumerate(content.split("\n")):
        	if ("while (" in line or "for (" in line) and ") {" in line:
        		split = line.split("//", 1)
        		split[0] += f" __check_no_forever_loop({n + 1}); "
        		line = "//".join(split)
        	if line.strip() == "// PUT_DEBUG_FOREVERLOOP_HERE":
        		line = foreverloop_definition + "  " + line
        		foreverloop_added = True
        	new += line + "\n"
        
        if not foreverloop_added:
        	new += "\n\n" + foreverloop_definition
        
        return new

         



class HTTPServer(BaseHTTPServer):
    """The main server, you pass in base_path which is the path you want to serve requests from"""

    def __init__(self, base_path, server_address, RequestHandlerClass=HTTPHandler):
        self.base_path = base_path
        BaseHTTPServer.__init__(self, server_address, RequestHandlerClass)


web_dir = os.path.join(os.path.dirname(__file__), '..')
httpd = HTTPServer(web_dir, ("", 8000))
httpd.serve_forever()
