import js2py
import urllib

class JsExecutor:

    def __init__(self, filename):

        def quote_url(url):
            '''
            URL-encodes a string (either str (i.e. ASCII) or unicode);
            uses de-facto UTF-8 encoding to handle Unicode codepoints in given string.
            '''
            return urllib.quote(unicode(url).encode('utf-8'), safe='~()*!.\'')

        self.context = js2py.EvalJs({'encodeURIComponent': quote_url})

        with open(filename) as fp:
            js_code = fp.read()

        self.context.execute(js_code)

