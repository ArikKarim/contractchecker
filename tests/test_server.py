import json
import threading
import unittest
import urllib.request
import urllib.error
from http.server import HTTPServer
from contractchecker.server import Handler

class ServerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server=HTTPServer(('127.0.0.1',0),Handler)
        cls.thread=threading.Thread(target=cls.server.serve_forever,daemon=True)
        cls.thread.start()
        cls.base=f'http://127.0.0.1:{cls.server.server_port}'

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown();cls.server.server_close();cls.thread.join()

    def request(self,path,body=None,origin=None):
        headers={'Content-Type':'application/json'}
        if origin:headers['Origin']=origin
        request=urllib.request.Request(self.base+path,data=json.dumps(body).encode() if body is not None else None,headers=headers)
        return urllib.request.urlopen(request,timeout=5)

    def test_sample_analysis_and_exact_evidence(self):
        with self.request('/sample') as response:sample=json.load(response)['text']
        with self.request('/analyze',{'text':sample},self.base) as response:result=json.load(response)
        self.assertGreater(len(result['review_prompts']),0)
        for p in result['review_prompts']:
            e=p['evidence'];self.assertEqual(sample[e['start']:e['end']],e['quote'])

    def test_bad_input_and_cross_origin(self):
        for body,origin,status in [({'text':''},None,400),({'text':42},None,400),({'text':'MAE'},'https://unrelated.example',403)]:
            with self.assertRaises(urllib.error.HTTPError) as ctx:self.request('/analyze',body,origin)
            self.assertEqual(ctx.exception.code,status)

    def test_frontend_and_not_found(self):
        with self.request('/') as response:
            self.assertIn(b'Evidence and questions',response.read())
        with self.assertRaises(urllib.error.HTTPError) as ctx:self.request('/missing')
        self.assertEqual(ctx.exception.code,404)

if __name__=='__main__':unittest.main()
